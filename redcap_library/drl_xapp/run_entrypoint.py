#!/usr/bin/env python3

import argparse
from contextlib import redirect_stdout
import importlib
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("entrypoint", help="module:callable")
    parser.add_argument("observation", type=Path, help="immutable observation JSON")
    args = parser.parse_args()
    if args.entrypoint.count(":") != 1:
        raise SystemExit("entrypoint 必須是 module:callable")
    module_name, callable_name = args.entrypoint.split(":")
    target = getattr(importlib.import_module(module_name), callable_name)
    observation = json.loads(args.observation.read_text(encoding="utf-8"))
    with redirect_stdout(sys.stderr):
        result = target(observation)
    print(json.dumps(result, sort_keys=True))
    if isinstance(result, int):
        raise SystemExit(result)


if __name__ == "__main__":
    main()
