# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = 
SPHINXBUILD   = sphinx-build
SPHINXAPIDOC  = sphinx-apidoc
SPHINXPROJ    = Capsule
SOURCEDIR     = ../
BUILDDIR      = build
DOCSOUTDIR    = source
CONFIG        = config.yaml

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

.PHONY: man
man:
	@$(SPHINXBUILD) -c ./ -b man "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	sudo cp "$(BUILDDIR)/capsule.1" /usr/local/share/man/man1/

.PHONY: clean
clean:
	rm -rf "$(BUILDDIR)" "$(DOCSOUTDIR)"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	cp "$(SOURCEDIR)$(CONFIG)" .
	@$(SPHINXAPIDOC) -f -o "$(DOCSOUTDIR)" "$(SOURCEDIR)" conf.py
	@$(SPHINXBUILD) -c ./ -b $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	rm -f "$(CONFIG)"
#	cp "$(BUILDDIR)/
