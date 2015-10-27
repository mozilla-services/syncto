SERVER_CONFIG = config/development.ini

VIRTUALENV = virtualenv
SPHINX_BUILDDIR = docs/_build
VENV := $(shell echo $${VIRTUAL_ENV-.venv})
PYTHON = $(VENV)/bin/python
DEV_STAMP = $(VENV)/.dev_env_installed.stamp
INSTALL_STAMP = $(VENV)/.install.stamp

.IGNORE: clean
.PHONY: all install install-dev virtualenv tests clean distclean maintainer-clean docs

OBJECTS = .venv .coverage

all: install
install: $(INSTALL_STAMP)

$(INSTALL_STAMP): $(PYTHON) setup.py
	$(VENV)/bin/pip install --process-dependency-links -U -e .
	touch $(INSTALL_STAMP)

install-dev: install $(DEV_STAMP)
$(DEV_STAMP): $(PYTHON) dev-requirements.txt
	$(VENV)/bin/pip install -r dev-requirements.txt
	touch $(DEV_STAMP)

virtualenv: $(PYTHON)
$(PYTHON):
	virtualenv $(VENV)
	$(VENV)/bin/pip install --upgrade pip

build-requirements:
	@rm -fr /tmp/syncto
	$(VIRTUALENV) /tmp/syncto
	/tmp/syncto/bin/pip install -Ue .
	/tmp/syncto/bin/pip freeze > requirements.txt

serve: install-dev
	$(VENV)/bin/cliquet --ini $(SERVER_CONFIG) migrate
	$(VENV)/bin/pserve $(SERVER_CONFIG) --reload

tests-once: install-dev
	$(VENV)/bin/nosetests -s --with-mocha-reporter --cover-min-percentage=100 --with-coverage --cover-package=syncto

tests:
	@rm -fr .coverage
	tox

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -exec rm -fr {} \;

distclean: clean
	rm -fr *.egg *.egg-info/

maintainer-clean: distclean
	rm -fr .venv/ .tox/ dist/ build/

# loadtest-check: install
# 	$(VENV)/bin/cliquet --ini loadtests/server.ini migrate > syncto.log &&\
# 	$(VENV)/bin/pserve loadtests/server.ini > syncto.log & PID=$$! && \
# 	  rm syncto.log || cat syncto.log; \
# 	  sleep 1 && cd loadtests && \
# 	  make test SERVER_URL=http://127.0.0.1:8000; \
# 	  EXIT_CODE=$$?; kill $$PID; exit $$EXIT_CODE

docs: install-dev
	$(VENV)/bin/sphinx-build -b html -d $(SPHINX_BUILDDIR)/doctrees docs $(SPHINX_BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(SPHINX_BUILDDIR)/html/index.html"
