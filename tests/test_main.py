from pathlib import Path

import pytest

from kube_manifest_lint.main import main


def test_valid_deployment_yaml():
    path = Path(__file__).parent / "manifests" / "deployment-valid.yaml"
    with pytest.raises(SystemExit) as e:
        main([str(path)])
    assert e.value.code == 0


def test_non_kubernetes_yaml():
    path = Path(__file__).parent / "manifests" / "non-kubernetes-file.yaml"
    with pytest.raises(SystemExit) as e:
        main([str(path)])
    assert e.value.code == 1


def test_ignore_non_kubernetes_yaml():
    path = Path(__file__).parent / "manifests" / "non-kubernetes-file.yaml"
    with pytest.raises(SystemExit) as e:
        main(["--ignore-non-k8s-files", str(path)])
    assert e.value.code == 0


def test_deprecated_deployment_yaml():
    path = Path(__file__).parent / "manifests" / "deployment-deprecated.yaml"
    with pytest.raises(SystemExit) as e:
        main([str(path)])
    assert e.value.code == 4


def test_deployment_yaml_with_extra_properties():
    path = Path(__file__).parent / "manifests" / "deployment-extra-properties.yaml"
    with pytest.raises(SystemExit) as e:
        main([str(path)])
    assert e.value.code == 8
