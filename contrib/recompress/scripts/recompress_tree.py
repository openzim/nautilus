#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import argparse
import logging
import pathlib
import subprocess
import sys

import humanfriendly

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
ROOT = pathlib.Path(__file__).parent


def disk_usage(folder):
    return sum(file.stat().st_size for file in folder.glob("**/*"))


def hsize(size):
    return humanfriendly.format_size(size, binary=True)


class TexasRanger:
    def __init__(self, src_path, dst_path, compress_args, force):
        self.src_path = src_path
        self.dst_path = dst_path
        self.compress_args = compress_args.split()
        self.force = force

    def handle_file(self, src_path, dst_path):
        logger.info(f"{src_path} -> {dst_path}")
        args = [
            str(ROOT / "recompress_file.py"),
            "--src",
            str(src_path),
            "--dst",
            str(dst_path),
        ] + self.compress_args
        ps = subprocess.run(args, capture_output=True, text=True)
        if ps.returncode != 0:
            raise IOError(ps.stdout)

    def traverse_tree(self, path):
        for item in path.iterdir():
            if item.is_dir():
                self.traverse_tree(item)
            else:
                self.handle_file(item, self.dst_path / item.relative_to(self.src_path))

    def run(self):
        src_size = disk_usage(self.src_path)
        self.traverse_tree(self.src_path)
        dst_size = disk_usage(self.dst_path)
        print("done", hsize(src_size), "->", hsize(dst_size))


def main():
    parser = argparse.ArgumentParser(
        prog="nautilus tree recompressor",
        description="recompress a folder recursively for use in nautilus",
    )

    parser.add_argument(
        "--src",
        help="Source file path",
        required=True,
        dest="src_path",
    )
    parser.add_argument(
        "--dst",
        help="Destination file path. If a folder, --src's fname will be appended",
        required=False,
        dest="dst_path",
    )
    parser.add_argument(
        "--in-place",
        help="Recompress source file directly",
        action="store_true",
        default=False,
        dest="in_place",
    )
    parser.add_argument(
        "--compress-args",
        help="args to pass to recompress_file (except --src and --dst)",
        default="",
        dest="compress_args",
    )
    parser.add_argument(
        "--force",
        help="Recompress even if destination exists",
        action="store_true",
        default=False,
        dest="force",
    )

    parser.add_argument(
        "--debug",
        help="display debug message on error",
        action="store_true",
        default=False,
        dest="debug",
    )

    args = parser.parse_args()

    try:
        # sanitize inputs
        args.src_path = pathlib.Path(args.src_path).expanduser().resolve()
        if args.dst_path:
            args.dst_path = pathlib.Path(args.dst_path).expanduser().resolve()
        if args.dst_path and args.in_place:
            raise ValueError("Cannot have both --dst and --in-place")
        if args.in_place:
            args.dst_path = args.src_path
        if not args.dst_path:
            raise ValueError("Must have either --dst or --in-place")

        # update presets value based on args
        walker = TexasRanger(
            args.src_path,
            args.dst_path,
            compress_args=args.compress_args,
            force=args.force,
        )
        sys.exit(walker.run())
    except Exception as exc:
        logger.error(f"FAILED. An error occurred: {exc}")
        if args.debug:
            logger.exception(exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
