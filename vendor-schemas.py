#!/usr/bin/env python
import json
import sys
from pathlib import Path

# source should contain clone of https://github.com/instrumenta/kubernetes-json-schema
source = Path(sys.argv[1])

kubernetes_version = "v1.17.0"
dest = Path("kube_manifest_lint/schemas") / kubernetes_version

dest.mkdir(exist_ok=True)

for path in source.glob(f"{kubernetes_version}-local/*.json"):
    with path.open() as fd:
        data = json.load(fd)

    with (dest / path.name).open("w") as fd:
        json.dump(data, fd)
