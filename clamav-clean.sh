VERSION=0.100.2
NAME=clamav
TARBALL_CLEAN=${NAME}-${VERSION}-norar.tar.xz
TARBALL=${NAME}-${VERSION}.tar.gz

wget https://www.clamav.net/downloads/production/${TARBALL}
#rm -f ${TARBALL}.tmp
zcat ${TARBALL} | tar --delete -f - '*/libclamunrar/*' | xz -c > ${TARBALL_CLEAN}
#mv ${TARBALL}.tmp ${TARBALL_CLEAN}
