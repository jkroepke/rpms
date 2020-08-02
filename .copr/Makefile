# https://stackoverflow.com/a/46153901/8087167

source := $(shell dirname $(spec))

srpm:
	rpmbuild \
		--define '_srcrpmdir $(outdir)' \
		--define '_sourcedir $(source)' \
		--define 'rhel 7' \
		--define 'dist .el7' \
		--define 'el7 1' \
		--undefine=fedora \
		--undefine=_disable_source_fetch \
		-bs $(spec)
