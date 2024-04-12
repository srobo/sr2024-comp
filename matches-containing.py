#!/usr/bin/env python3

import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'include_any',
        nargs=argparse.ONE_OR_MORE,
    )
    parser.add_argument(
        '--exclude',
        nargs=argparse.ONE_OR_MORE,
        required=False,
        default=(),
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    include_any = set(args.include_any)
    exclude = set(args.exclude)

    for line in sys.stdin.readlines():
        line = line.strip()
        parts = set(line.split('|'))
        if exclude & parts:
            continue
        if include_any < parts:
            print(line)


if __name__ == '__main__':
    main(parse_args())
