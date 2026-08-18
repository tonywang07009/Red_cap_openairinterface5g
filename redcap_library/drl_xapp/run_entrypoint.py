#!/usr/bin/env python3

import argparse
import importlib


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("entrypoint", help="module:callable")
    args = parser.parse_args()
    if args.entrypoint.count(":") != 1:
        raise SystemExit("entrypoint 必須是 module:callable")
    module_name, callable_name = args.entrypoint.split(":")
    target = getattr(importlib.import_module(module_name), callable_name)
    result = target()
    if isinstance(result, int):
        raise SystemExit(result)


if __name__ == "__main__":
    main()
