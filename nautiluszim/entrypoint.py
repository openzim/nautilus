#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import argparse

from .constants import NAME, SCRAPER, getLogger, setDebug


def main():
    parser = argparse.ArgumentParser(
        prog=NAME, description="Create a ZIM file off a collection of file documents",
    )

    parser.add_argument(
        "--archive",
        help="Path or URL to a ZIP archive containing all the documents",
        required=True,
    )
    parser.add_argument(
        "--collection",
        help="Different collection JSON path or URL. Otherwise using `collection.json` from archive",
        required=False,
    )
    parser.add_argument(
        "--name",
        help="ZIM name. Used as identifier and filename (date will be appended)",
        required=True,
    )

    parser.add_argument(
        "--pagination",
        help="Number of items per page",
        type=int,
        dest="nb_items_per_page",
        default=10,
    )

    parser.add_argument(
        "--no-random",
        help="Don't randomize items in list",
        action="store_true",
        default=False,
        dest="no_random",
    )

    parser.add_argument(
        "--show-description",
        help="Show description in main list",
        action="store_true",
        default=False,
        dest="show_description",
    )

    parser.add_argument(
        "--output",
        help="Output folder for ZIM file or build folder",
        default="/output",
        dest="output_dir",
    )
    parser.add_argument(
        "--no-zim",
        help="Don't produce a ZIM file, create HTML folder only.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--zim-file",
        help="ZIM file name (based on --name if not provided)",
        dest="fname",
    )

    parser.add_argument(
        "--debug", help="Enable verbose output", action="store_true", default=False
    )
    parser.add_argument(
        "--keep",
        help="Don't erase build folder on start (for debug/devel)",
        default=False,
        action="store_true",
        dest="keep_build_dir",
    )
    parser.add_argument(
        "--skip-download",
        help="Skip the download and extract step",
        default=False,
        action="store_true",
        dest="skip_download",
    )

    parser.add_argument(
        "--language", help="ISO-639-3 (3 chars) language code of content", default="eng"
    )
    parser.add_argument(
        "--locale",
        help="Locale name to use for translations (if avail) and time representations. Defaults to --language or English.",
        dest="locale_name",
    )
    parser.add_argument(
        "--tags", help="List of comma-separated Tags for the ZIM file.", default="",
    )
    parser.add_argument(
        "--title", help="Title for your project and ZIM. Otherwise --name.",
    )
    parser.add_argument(
        "--description", help="Description for your project and ZIM.",
    )
    parser.add_argument(
        "--creator", help="Name of content creator.",
    )
    parser.add_argument(
        "--publisher", help="Custom publisher name (ZIM metadata)", default="Kiwix"
    )
    parser.add_argument(
        "--favicon",
        help="Custom favicon. Will be resized to 48x48px. Nautilus otherwise.",
    )
    parser.add_argument(
        "--main-logo",
        help="Custom logo. Will be resized to 300x65px",
        dest="main_logo",
    )
    parser.add_argument(
        "--secondary-logo",
        help="Custom footer logo. Will be resized to 300x65px. None otherwise",
        dest="secondary_logo",
    )
    parser.add_argument(
        "--main-color",
        help="Custom header color. Hex/HTML syntax (#DEDEDE). Default to main-logo's primary color solarized (or #95A5A6 if no logo).",
    )
    parser.add_argument(
        "--secondary-color",
        help="Custom secondary color. Hex/HTML syntax (#DEDEDE). Default to main-logo's primary color solarized (or #95A5A6 if no logo).",
    )

    parser.add_argument(
        "--about",
        help="Custom about HTML file. Uses file `about.html` of archive if present otherwise.",
    )

    parser.add_argument(
        "--version",
        help="Display scraper version and exit",
        action="version",
        version=SCRAPER,
    )

    args = parser.parse_args()

    setDebug(args.debug)
    logger = getLogger()
    from .scraper import Nautilus

    try:
        scraper = Nautilus(**dict(args._get_kwargs()))
        scraper.run()
    except Exception as exc:
        logger.error(f"FAILED. An error occured: {exc}")
        if args.debug:
            logger.exception(exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
