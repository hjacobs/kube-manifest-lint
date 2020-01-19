# Kubernetes Manifest Linter

[![Build Status](https://travis-ci.com/hjacobs/kube-manifest-lint.svg?branch=master)](https://travis-ci.com/hjacobs/kube-manifest-lint)
[![PyPI](https://img.shields.io/pypi/v/kube-manifest-lint)](https://pypi.org/project/kube-manifest-lint/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kube-manifest-lint)
![License](https://img.shields.io/github/license/hjacobs/kube-manifest-lint)

Validate Kubernetes YAML manifests against JSON schema.

Usage:

```
pip3 install kube-manifest-lint
kube-manifest-lint my-deployment.yaml
```

## Exit Codes

* 1: file is not a Kubernetes manifests
* 2: schema for apiVersion/kind was not found
* 4: schema is deprecated (e.g. using "extensions/v1beta1" instead of "apps/v1")
* 8: schema validation failed
