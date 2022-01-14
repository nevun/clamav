VERSION=0.103.5

if [ -z "$1" ]
then
      stage=0
else
      stage=$1
fi

NAME=clamav
TARBALL_CLEAN=${NAME}-${VERSION}-norar.tar.xz
TARBALL=${NAME}-${VERSION}.tar.gz

if test $stage -le 0
then
echo STAGE 0
wget -c https://www.clamav.net/downloads/production/${TARBALL}
wget -c https://www.clamav.net/downloads/production/${TARBALL}.sig
gpg --verify ${TARBALL}.sig ${TARBALL}
zcat ${TARBALL} | tar --delete -f - '*/libclamunrar/*' | xz -c > ${TARBALL_CLEAN}
fi

echo Press enter convert cvd into spec or n to skip ; read dummy;
if [[ "$dummy" != "n" ]]; then
# WIP clouflare don't allow wget we need download with browser
#wget https://database.clamav.net/main.cvd
#wget https://database.clamav.net/daily.cvd
#wget https://database.clamav.net/bytecode.cvd

main_ver=$(file main.cvd | sed -e 's/.*version /main-/;s/,.*/.cvd/')
daily_ver=$(file daily.cvd | sed -e 's/.*version /daily-/;s/,.*/.cvd/')
bytecode_ver=$(file bytecode.cvd | sed -e 's/.*version /bytecode-/;s/,.*/.cvd/')

cp -f main.cvd $main_ver
cp -f daily.cvd $daily_ver
cp -f bytecode.cvd $bytecode_ver

sed -i "s|^Source10: .*|Source10:   $main_ver|" clamav.spec
sed -i "s|^Source11: .*|Source11:   $daily_ver|" clamav.spec
sed -i "s|^Source12: .*|Source12:   $bytecode_ver|" clamav.spec
fi

rpmdev-bumpspec -n $VERSION -c "Update to $VERSION" clamav.spec
echo fedpkg new-sources ${TARBALL_CLEAN} $main_ver $daily_ver $bytecode_ver
echo Press enter scratch-build or n to skip ; read dummy;
if [[ "$dummy" != "n" ]]; then
#fkinit -u sergiomb
fedpkg scratch-build --srpm
fi
echo Press enter to upload sources and commit ; read dummy;
fedpkg new-sources ${TARBALL_CLEAN} $(spectool -l clamav.spec | grep -P "Source10|Source11|Source12" | sed 's/.* //')
fedpkg ci -c && git show

echo Press enter to build rawhide; read dummy;
git push && fedpkg build --nowait

for repo in "f35 f34 epel8 epel7" ; do
echo Press enter to build on branch $repo; read dummy;
git checkout $repo && git merge rawhide && fedpkg push && fedpkg build --nowait; git checkout rawhide
done

exit
# not finished yet
/usr/bin/bodhi updates new --autokarma --autotime --type bugfix --severity medium --notes "https://blog.clamav.net/2021/06/clamav-01033-patch-release.html" --bugs 1974601 --request testing clamav-0.103.3-1.fc34
/usr/bin/bodhi updates new --autokarma --autotime --type bugfix --severity medium --notes "https://blog.clamav.net/2021/06/clamav-01033-patch-release.html" --bugs 1974601 --request testing clamav-0.103.3-1.fc33
/usr/bin/bodhi updates new --autokarma --autotime --type bugfix --severity medium --notes "https://blog.clamav.net/2021/06/clamav-01033-patch-release.html" --bugs 1974601 --request testing clamav-0.103.3-1.el8

sha512sum --tag  ${TARBALL_CLEAN} $main_ver $daily_ver $bytecode_ver > sources
