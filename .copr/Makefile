# https://stackoverflow.com/a/46153901/8087167

source := $(shell dirname $(spec))

srpm:
	dnf install -y mock

	mock -r epel-7-x86_64 \
		--isolation=simple \
		--enable-network \
		--buildsrpm \
		--source=$(source) \
		--spec=$(spec) \
		--resultdir=$(outdir) \
		--define '_disable_source_fetch %{nil}'
