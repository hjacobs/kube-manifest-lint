from pathlib import Path

import pytest

from kube_manifest_lint.main import main


def test_valid_deployment_yaml():
    path = Path(__file__).parent / "manifests" / "deployment-valid.yaml"
    with pytest.raises(SystemExit) as e:
        main([str(path)])
        assert e.code == 0


def test_deprececated_deployment_yaml():
    path = Path(__file__).parent / "manifests" / "deployment-deprecated.yaml"
    with pytest.raises(SystemExit) as e:
        main([str(path)])
        assert e.code == 1
