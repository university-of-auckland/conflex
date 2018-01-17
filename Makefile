# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = 
SPHINXBUILD   = sphinx-build
SPHINXAPIDOC  = sphinx-apidoc
SPHINXPROJ    = Capsule
SOURCEDIR     = .
BUILDDIR      = docs/build
DOCSOUTDIR    = docs/source
CONFIG        = config.yaml

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Generate man file and copy it to the man location.
.PHONY: man
man:
	@$(SPHINXBUILD) -c ./ -b man "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	sudo cp "$(BUILDDIR)/capsule.1" /usr/local/share/man/man1/

# Clean up documentation
.PHONY: clean
clean:
	rm -rf "$(BUILDDIR)" "$(DOCSOUTDIR)"

.PHONY: test
test:
	venv/bin/python -m unittest discover tests/test*.py

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
#	cp "$(CONFIG)" ./docs
	@$(SPHINXAPIDOC) -f -o "$(DOCSOUTDIR)" "$(SOURCEDIR)" docs/conf.py
	@$(SPHINXBUILD) -c ./docs -b $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
#	rm -f "./docs/$(CONFIG)"

#	cp "$(BUILDDIR)/
