"""Minimal xmllint-compatible wrapper using lxml for schema validation."""
import subprocess
import sys


def main():
    result = subprocess.run(
        ["xmllint.cmd", "--noout", "--schema", "schemas/sila2_core_v1.0.0.xsd", "proto/hamilton_starlet.proto"],
        capture_output=True,
        text=True,
        shell=True,
    )
    print("RC:", result.returncode)
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
