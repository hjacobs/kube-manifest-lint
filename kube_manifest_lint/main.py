import argparse
import json
import sys
from pathlib import Path

import jsonschema
import yaml


def additional_properties(data):
    """Set additionalProperties=false on the object.

    Copied from https://github.com/instrumenta/openapi2jsonschema/blob/master/openapi2jsonschema/util.py
    This recreates the behaviour of kubectl at https://github.com/kubernetes/kubernetes/blob/225b9119d6a8f03fcbe3cc3d590c261965d928d0/pkg/kubectl/validation/schema.go#L312"""
    new = {}
    try:
        for k, v in data.items():
            new_v = v
            if isinstance(v, dict):
                if "properties" in v:
                    if "additionalProperties" not in v:
                        v["additionalProperties"] = False
                new_v = additional_properties(v)
            else:
                new_v = v
            new[k] = new_v
        return new
    except AttributeError:
        return data


class SchemaResolver(jsonschema.RefResolver):
    def resolve_remote(self, uri):
        """Only resolve from local directory."""
        with Path(uri).open() as fd:
            result = json.load(fd)
        # make it a strict schema (do not allow additional properties)
        result = additional_properties(result)
        if self.cache_remote:
            self.store[uri] = result
        return result


def main(argv: list = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ignore-non-k8s-files", action="store_true")
    parser.add_argument("--ignore-unknown-schemas", action="store_true")
    parser.add_argument("files", nargs="+", type=Path)

    args = parser.parse_args(argv)

    kubernetes_version = "v1.17.0"

    lookup = {}

    schema_dir = Path(__file__).parent / "schemas" / kubernetes_version

    for path in schema_dir.glob("*.json"):
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

    exit_code = 0

    errors = []
    for path in args.files:
        with path.open() as fd:
            for instance in yaml.safe_load_all(fd):

                try:
                    api_version = instance["apiVersion"]
                    kind = instance["kind"]
                except (TypeError, KeyError):
                    if not args.ignore_non_k8s_files:
                        print("no Kubernetes manifest (apiVersion/kind not set)")
                        exit_code |= 1
                    # YAML file is apparently not a Kubernetes manifest, skip
                    continue

                try:
                    schema_path = lookup[(api_version, kind)]
                except KeyError:
                    if not args.ignore_unknown_schemas:
                        print(f"schema for {api_version} {kind} not found")
                        exit_code |= 2
                    continue

                with schema_path.open() as fd:
                    schema = json.load(fd)

                if schema["description"].startswith("DEPRECATED"):
                    message = f"{api_version} {kind} is deprecated"
                    errors.append(message)
                    exit_code |= 4
                    print(message)

                resolver = SchemaResolver(
                    base_uri=str(schema_path.resolve()), referrer=schema
                )
                try:
                    jsonschema.validate(
                        instance=instance,
                        schema=schema,
                        cls=jsonschema.Draft7Validator,
                        resolver=resolver,
                    )
                except jsonschema.ValidationError as e:
                    errors.append(e)
                    exit_code |= 8
                    print(e)
                except jsonschema.SchemaError as e:
                    errors.append(e)
                    exit_code |= 16
                    print(e)

    sys.exit(exit_code)
