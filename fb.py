#!/usr/bin/env python

import sys
import pathlib
import subprocess
import argparse


def try_subcommands(skip_commands=[]):
    """
    Try git-style subcommands.
    """
    if len(sys.argv) > 1 and sys.argv not in skip_commands:
        binname = pathlib.Path(__file__)
        sub_cmd = (
            binname.parent.resolve() / f"{binname.stem}-{sys.argv[1]}{binname.suffix}"
        )
        try:
            sys.exit(subprocess.run([sub_cmd, *sys.argv[2:]]).returncode)
        except FileNotFoundError:
            pass


def main(args):
    pass


if __name__ == "__main__":
    try_subcommands(skip_commands=["post", "site"])

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    main(args)
