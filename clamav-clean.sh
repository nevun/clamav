VERSION=0.100.1
NAME=clamav
TARBALL_CLEAN=${NAME}-${VERSION}-norar.tar.xz.tmp
TARBALL=${NAME}-${VERSION}.tar.gz

wget https://www.clamav.net/downloads/production/${TARBALL}
rm -f ${TARBALL}.tmp
zcat ${TARBALL} | tar --delete -f - '*/libclamunrar/*' | xz -c > ${TARBALL}.tmp
mv ${TARBALL}.tmp ${TARBALL}
