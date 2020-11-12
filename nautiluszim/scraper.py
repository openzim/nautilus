#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import re
import json
import locale
import shutil
import pathlib
import datetime
import subprocess
from pathlib import Path

import jinja2
from zimscraperlib.logging import nicer_args_join
from zimscraperlib.download import save_large_file
from zimscraperlib.zim import ZimInfo, make_zim_file
from zimscraperlib.fix_ogvjs_dist import fix_source_dir
from zimscraperlib.inputs import handle_user_provided_file
from zimscraperlib.i18n import setlocale, get_language_details, _
from zimscraperlib.imaging import resize_image, get_colors, is_hex_color, create_favicon

from .constants import ROOT_DIR, SCRAPER, getLogger

logger = getLogger()


class Nautilus(object):
    def __init__(
        self,
        archive,
        collection,
        nb_items_per_page,
        no_random,
        show_description,
        output_dir,
        no_zim,
        fname,
        debug,
        keep_build_dir,
        skip_download,
        language,
        locale_name,
        tags,
        name=None,
        title=None,
        description=None,
        creator=None,
        publisher=None,
        favicon=None,
        main_logo=None,
        secondary_logo=None,
        main_color=None,
        secondary_color=None,
        about=None,
    ):
        # options & zim params
        self.archive = archive
        self.collection = handle_user_provided_file(source=collection, nocopy=True)
        self.nb_items_per_page = nb_items_per_page
        self.show_author = True
        self.show_description = show_description
        self.fname = fname
        self.language = language
        self.tags = [t.strip() for t in tags.split(",")]
        self.title = title
        self.description = description
        self.creator = creator
        self.publisher = publisher
        self.name = name
        self.favicon = favicon
        self.main_logo = main_logo
        self.secondary_logo = secondary_logo
        self.main_color = main_color
        self.secondary_color = secondary_color
        self.about = about
        self.randomize = not no_random

        # process-related
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.period = datetime.datetime.now().strftime("%Y-%m")

        # debug/devel options
        self.no_zim = no_zim
        self.debug = debug
        self.keep_build_dir = keep_build_dir
        self.skip_download = skip_download

        self.build_dir = self.output_dir.joinpath("build")

        # store ZIM-related info
        self.zim_info = ZimInfo(
            language=language,
            tags=tags,
            title=title,
            description=description,
            creator=creator,
            publisher=publisher,
            name=name,
            scraper=SCRAPER,
        )

        # set and record locale for translations
        locale_name = locale_name or get_language_details(self.language)["iso-639-1"]
        try:
            self.locale = setlocale(ROOT_DIR, locale_name)
        except locale.Error:
            logger.error(
                f"No locale for {locale_name}. Use --locale to specify it. defaulting to en_US"
            )
            self.locale = setlocale(ROOT_DIR, "en")

    @property
    def root_dir(self):
        return ROOT_DIR

    @property
    def templates_dir(self):
        return self.root_dir.joinpath("templates")

    @property
    def assets_dir(self):
        return self.templates_dir.joinpath("assets")

    @property
    def vendors_src_dir(self):
        return self.templates_dir.joinpath("vendors")

    @property
    def vendors_dir(self):
        return self.build_dir.joinpath("vendors")

    @property
    def main_logo_path(self):
        return self.build_dir.joinpath("assets", "main-logo.png")

    @property
    def secondary_logo_path(self):
        return self.build_dir.joinpath("assets", "secondary-logo.png")

    @property
    def archive_path(self):
        return (
            self.output_dir.joinpath("archive.zip")
            if self.archive.startswith("http")
            else pathlib.Path(self.archive).expanduser().resolve()
        )

    @property
    def files_path(self):
        return self.build_dir.joinpath("files")

    def run(self):
        """ execute the scrapper step by step """
        logger.info(f"starting nautilus scraper for {self.archive}")

        logger.info("preparing build folder at {}".format(self.build_dir.resolve()))
        if not self.keep_build_dir and self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.make_build_folder()

        # fail early if supplied branding files are missing
        self.check_branding_values()

        # download videos (and recompress)
        if not self.skip_download:
            self.download_and_extract_archive()

        if not self.collection:
            self.collection = self.files_path.joinpath("collection.json")

        self.test_collection()

        logger.info("update general metadata")
        self.update_metadata()

        logger.info("creating HTML files")
        self.make_html_files()

        # make zim file
        if not self.no_zim:
            self.fname = Path(
                self.fname if self.fname else f"{self.name}_{self.period}.zim"
            )
            logger.info("building ZIM file")
            print(self.zim_info.to_zimwriterfs_args())
            make_zim_file(self.build_dir, self.output_dir, self.fname, self.zim_info)
            logger.info("removing HTML folder")
            if not self.keep_build_dir:
                shutil.rmtree(self.build_dir, ignore_errors=True)

        logger.info("all done!")

    def make_build_folder(self):
        """ prepare build folder before we start downloading data """

        # create build folder
        os.makedirs(self.build_dir, exist_ok=True)

        # copy vendors and assets
        for folder in ["vendors", "assets"]:
            target = self.build_dir.joinpath(folder)
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(self.templates_dir.joinpath(folder), target)

        fix_source_dir(self.build_dir.joinpath("vendors"), "vendors")

        for fname in ["nautilus.js", "zimwriterfs.js", "favicon.png"]:
            target = self.build_dir.joinpath(fname)
            try:
                target.unlink()
            except FileNotFoundError:
                pass
            shutil.copy(self.templates_dir.joinpath(fname), target)
        os.makedirs(self.files_path, exist_ok=True)

    def check_branding_values(self):
        """ checks that user-supplied images and colors are valid (so to fail early)

            Images are checked for existence or downloaded then resized
            Colors are check for validity """

        # skip this step if none of related values were supplied
        if not sum(
            [
                bool(x)
                for x in (
                    self.favicon,
                    self.main_logo,
                    self.secondary_logo,
                    self.main_color,
                    self.secondary_color,
                    self.about,
                )
            ]
        ):
            return

        logger.info("checking your branding files and values")

        images = [
            (self.favicon, self.build_dir.joinpath("favicon.png"), 48, 48),
            (self.main_logo, self.main_logo_path, 300, 65),
            (self.secondary_logo, self.secondary_logo_path, 300, 65),
        ]

        for src, dest, width, height in images:
            if src:
                handle_user_provided_file(source=src, dest=dest)
                resize_image(dest, width=width, height=height, method="thumbnail")

        if self.main_color and not is_hex_color(self.main_color):
            raise ValueError(
                f"--main-color is not a valid hex color: {self.main_color}"
            )

        if self.secondary_color and not is_hex_color(self.secondary_color):
            raise ValueError(
                f"--secondary_color-color is not a valid hex color: {self.secondary_color}"
            )

        if self.about:
            handle_user_provided_file(
                source=self.about, dest=self.build_dir / "about.html"
            )

    def update_metadata(self):
        self.title = self.title or self.name
        self.description = self.description or "-"
        self.creator = self.creator or "Unknown"
        self.publisher = self.publisher or "Kiwix"

        self.tags = self.tags or []

        # generate ICO favicon (fallback for browsers)
        create_favicon(
            self.build_dir.joinpath("favicon.png"),
            self.build_dir.joinpath("favicon.ico"),
        )

        self.zim_info.update(
            title=self.title,
            description=self.description,
            creator=self.creator,
            publisher=self.publisher,
            name=self.name,
            tags=self.tags,
        )

        # set colors from images if not supplied
        main_color, secondary_color = "#95A5A6", "#95A5A6"
        if self.main_logo:
            main_color = secondary_color = get_colors(self.main_logo_path)[1]
        self.main_color = self.main_color or main_color
        self.secondary_color = self.secondary_color or secondary_color

        # get about content from param, archive or defaults to desc
        self.about_content = f"<p>{self.description}</p>"
        about_source = self.build_dir / "about.html"
        if about_source.exists():
            with open(about_source, "r") as fh:
                self.about_content = fh.read()
            about_source.unlink(missing_ok=True)
        else:
            about_source = about_source.parent / "files" / "about.html"
            if about_source.exists():
                with open(about_source, "r") as fh:
                    self.about_content = fh.read()

    def download_and_extract_archive(self):
        # download if it's a URL
        if self.archive.startswith("http"):
            logger.info(f"Downloading archive at {self.archive}")
            save_large_file(self.archive, self.archive_path)

        # extract ZIP
        logger.info(f"Extracting ZIP archive {self.archive_path} to {self.files_path}")
        args = [
            "unzip",
            "-u",
            "-q",
            "-D",
            str(self.archive_path),
            "-d",
            str(self.files_path),
        ]
        logger.debug(nicer_args_join(args))
        subprocess.run(args, check=True)

    def test_collection(self):
        with open(self.collection, "r") as fp:
            self.json_collection = [i for i in json.load(fp) if i.get("files", [])]
        nb_items = len(self.json_collection)
        nb_files = sum([len(i.get("files", [])) for i in self.json_collection])
        logger.info(f"Collection loaded. {nb_items} items, {nb_files} files")

    def make_html_files(self):
        """ make up HTML structure to read the content
        """

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)), autoescape=True
        )

        # build homepage
        html = env.get_template("home.html").render(
            debug=str(self.debug).lower(),
            title=self.title,
            description=self.description,
            main_color=self.main_color,
            secondary_color=self.secondary_color,
            db_name=f"{self.name}_db",
            db_version=int(re.sub(r"([^0-9])", "", self.period)[-4:]),
            nb_items_per_page=self.nb_items_per_page,
            show_author=self.show_author,
            show_description=self.show_description,
            randomize=self.randomize,
            search_label=_("Search"),
            search_input_label=_("Keywords…"),
            close_label=_("Close"),
            loading_label=_("Loading…"),
            no_result_text=_("No result for this search request."),
            backtotop_label=_("Back to Top"),
            secondary_logo=self.secondary_logo,
            about_label=_("About this content"),
            about_content=self.about_content,
        )
        with open(self.build_dir.joinpath("home.html"), "w", encoding="utf-8") as fp:
            fp.write(html)

        with open(self.build_dir.joinpath("database.js"), "w", encoding="utf-8") as fp:
            fp.write("var DATABASE = [\n")
            for docid, document in enumerate(self.json_collection):
                fp.write(
                    "{},\n".format(
                        str(
                            {
                                "_id": str(docid),
                                "ti": document.get("title") or "Unknown?",
                                "dsc": document.get("description") or "",
                                "aut": document.get("authors") or "",
                                "fp": document.get("files", []),
                            }
                        )
                    )
                )
            fp.write("];\n")
