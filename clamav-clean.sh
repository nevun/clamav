VERSION=0.103.2
NAME=clamav
TARBALL_CLEAN=${NAME}-${VERSION}-norar.tar.xz
TARBALL=${NAME}-${VERSION}.tar.gz

wget https://www.clamav.net/downloads/production/${TARBALL}
wget https://www.clamav.net/downloads/production/${TARBALL}.sig
gpg --verify ${TARBALL}.sig ${TARBALL}
zcat ${TARBALL} | tar --delete -f - '*/libclamunrar/*' | xz -c > ${TARBALL_CLEAN}

# WIP
wget http://database.clamav.net/main.cvd
wget http://database.clamav.net/daily.cvd
wget http://database.clamav.net/bytecode.cvd

main_ver=$(file main.cvd | sed -e 's/.*version /main-/;s/,.*/.cvd/')
daily_ver=$(file daily.cvd | sed -e 's/.*version /daily-/;s/,.*/.cvd/')
bytecode_ver=$(file bytecode.cvd | sed -e 's/.*version /bytecode-/;s/,.*/.cvd/')

cp main.cvd $main_ver
cp daily.cvd $daily_ver
cp bytecode.cvd $bytecode_ver

sed -i "s|^Source10: .*|Source10:   $main_ver|" clamav.spec
sed -i "s|^Source11: .*|Source11:   $daily_ver|" clamav.spec
sed -i "s|^Source12: .*|Source12:   $bytecode_ver|" clamav.spec

fedpkg new-sources ${TARBALL_CLEAN} $main_ver $daily_ver $bytecode_ver
