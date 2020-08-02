# https://stackoverflow.com/a/46153901/8087167
srpm:
    mock -r epel-7-x86_64 \
      --enable-network \
      --buildsrpm \
      --source=. \
      --spec=$(spec) \
      --resultdir=$(outdir) \
      --define '_disable_source_fetch %{nil}'
