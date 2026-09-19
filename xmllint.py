"""Minimal xmllint-compatible wrapper using lxml for schema validation."""
import sys
import os
from pathlib import Path
from lxml import etree


def main():
    args = sys.argv[1:]
    schema_path = None
    xml_path = None
    i = 0
    while i < len(args):
        if args[i] == "--schema" and i + 1 < len(args):
            schema_path = args[i + 1]
            i += 2
        elif args[i] == "--noout":
            i += 1
        else:
            xml_path = args[i]
            i += 1

    if not schema_path or not xml_path:
        print("Missing args", file=sys.stderr)
        sys.exit(1)

    base = Path(__file__).resolve().parent
    schema_file = base / schema_path
    xml_file = base / xml_path

    print(f"DEBUG base={base}", file=sys.stderr)
    print(f"DEBUG schema_file={schema_file} exists={schema_file.exists()}", file=sys.stderr)
    print(f"DEBUG xml_file={xml_file} exists={xml_file.exists()}", file=sys.stderr)

    schema = etree.XMLSchema(file=str(schema_file))
    doc = etree.parse(str(xml_file))
    valid = schema.validate(doc)
    if not valid:
        for error in schema.error_log:
            print(error, file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
