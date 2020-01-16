
VERSION          ?= $(shell git describe --tags --always --dirty)
TAG              ?= $(VERSION)

default: test

.PHONY: install
install:
	poetry install

.PHONY: lint
lint: install
	poetry run pre-commit run --all-files


.PHONY: test
test: lint install
	poetry run coverage run --source=kube_manifest_lint -m py.test -v
	poetry run coverage report

.PHONY: mirror
mirror:
	git push --mirror git@github.com:hjacobs/kube-manifest-lint.git
