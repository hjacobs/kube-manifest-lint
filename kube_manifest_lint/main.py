import argparse
import json
from pathlib import Path

import yaml
from jsonschema import validate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)

    args = parser.parse_args()

    kubernetes_version = "v1.17.0"

    lookup = {}

    for path in Path(
        f"../kubernetes-json-schema/{kubernetes_version}-standalone-strict"
    ).glob("*.json"):
        with path.open() as fd:
            schema = json.load(fd)
            if "properties" in schema:
                api_version = kind = None
                for property_name, property_schema in schema["properties"].items():
                    if property_name == "apiVersion" and "enum" in property_schema:
                        api_version = property_schema["enum"][0]
                    elif property_name == "kind" and "enum" in property_schema:
                        kind = property_schema["enum"][0]
                if api_version and kind:
                    lookup[(api_version, kind)] = path

    for path in args.files:
        with path.open() as fd:
            for instance in yaml.safe_load_all(fd):

                api_version = instance["apiVersion"]
                kind = instance["kind"]

                schema_path = lookup[(api_version, kind)]

                with schema_path.open() as fd:
                    schema = json.load(fd)

                result = validate(instance=instance, schema=schema)
                print(result)
