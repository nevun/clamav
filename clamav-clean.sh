VERSION=0.101.1
NAME=clamav
TARBALL_CLEAN=${NAME}-${VERSION}-norar.tar.xz
TARBALL=${NAME}-${VERSION}.tar.gz

wget https://www.clamav.net/downloads/production/${TARBALL}
wget https://www.clamav.net/downloads/production/${TARBALL}.sig
gpg --verify ${TARBALL}.sig ${TARBALL}
#rm -f ${TARBALL}.tmp
zcat ${TARBALL} | tar --delete -f - '*/libclamunrar/*' | xz -c > ${TARBALL_CLEAN}
#mv ${TARBALL}.tmp ${TARBALL_CLEAN}
