MAKEFILE_COMMON = $(HOME)/.fedora/common.mk
-include $(MAKEFILE_COMMON)

# can not use final tarball name here as it will conflict with rules
# within Makefile.common
TARBALL_CLEAN =	${NAME}-${VERSION}-norar.tar.xz.tmp
TARBALL =	${NAME}-${VERSION}.tar.gz

clean-sources:	${TARBALL_CLEAN}

${TARBALL_CLEAN}:	${TARBALL}
	rm -f $@.tmp
	zcat $< | tar --delete -f - '*/libclamunrar/*' | xz -c > $@.tmp
	mv $@.tmp $@
