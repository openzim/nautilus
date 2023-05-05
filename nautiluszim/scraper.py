#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import datetime
import json
import locale
import os
import pathlib
import shutil
import unicodedata
import uuid
import zipfile
from pathlib import Path
from typing import Optional

import jinja2
from zimscraperlib.constants import (
    MAXIMUM_DESCRIPTION_METADATA_LENGTH,
    MAXIMUM_LONG_DESCRIPTION_METADATA_LENGTH,
)
from zimscraperlib.download import save_large_file
from zimscraperlib.i18n import _, get_language_details, setlocale
from zimscraperlib.image.convertion import create_favicon
from zimscraperlib.image.probing import get_colors, is_hex_color
from zimscraperlib.image.transformation import resize_image
from zimscraperlib.inputs import handle_user_provided_file
from zimscraperlib.zim.creator import Creator

from .constants import ROOT_DIR, SCRAPER, getLogger

logger = getLogger()


def normalized_path(path: str) -> str:
    """ASCII version of a path for use in URL"""
    return unicodedata.normalize("NFKC", path)


class Nautilus(object):
    def __init__(
        self,
        archive,
        collection,
        nb_items_per_page,
        no_random,
        show_description,
        output_dir,
        fname,
        debug,
        keep_build_dir,
        language,
        locale_name,
        tags,
        name=None,
        title=None,
        description=None,
        longdescription=None,
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
        self.long_description = longdescription
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
        self.debug = debug
        self.keep_build_dir = keep_build_dir

        self.build_dir = self.output_dir.joinpath("build")

        # set and record locale for translations
        locale_name = (
            locale_name
            or get_language_details(self.language.split(",")[0])["iso-639-1"]
        )
        try:
            self.locale = setlocale(ROOT_DIR, locale_name)
        except locale.Error:
            logger.error(
                f"No locale for {locale_name}. Use --locale to specify it. "
                "defaulting to en_US"
            )
            self.locale = setlocale(ROOT_DIR, "en")

    @property
    def root_dir(self):
        return ROOT_DIR

    @property
    def templates_dir(self):
        return self.root_dir.joinpath("templates")

    @property
    def archive_path(self):
        return (
            self.output_dir.joinpath("archive.zip")
            if self.archive.startswith("http")
            else pathlib.Path(self.archive).expanduser().resolve()
        )

    def run(self):
        """execute the scrapper step by step"""

        self.check_description_length()

        logger.info(f"starting nautilus scraper for {self.archive}")

        logger.info("preparing build folder at {}".format(self.build_dir.resolve()))
        if not self.keep_build_dir and self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.make_build_folder()

        # fail early if supplied branding files are missing
        self.check_branding_values()

        # download archive
        self.download_archive()

        if not self.collection:
            self.collection = self.extract_to_fs("collection.json")
            if not self.about:
                self.extract_to_fs("about.html", failsafe=True)

        self.test_collection()

        logger.info("update general metadata")
        self.update_metadata()

        # prepare creator
        self.zim_creator = Creator(
            filename=self.output_dir / self.fname,
            main_path="home",
            ignore_duplicates=True,
        ).config_verbose(self.debug)

        with open(self.build_dir.joinpath("favicon.png"), "rb") as fh:
            self.zim_creator.config_metadata(
                Name=self.name,
                Language=self.language,
                Title=self.title,
                Description=self.description,
                LongDescription=self.long_description,
                Creator=self.creator,
                Publisher=self.publisher,
                Date=datetime.date.today(),
                Illustration_48x48_at_1=fh.read(),
                Tags=";".join(self.tags),
                Scraper=SCRAPER,
            )
        self.zim_creator.start()

        logger.info("adding U.I")
        self.add_ui()

        logger.info("Adding all files")
        self.process_collection_entries()

        logger.info("Finishing ZIM file")
        self.zim_creator.finish()

        logger.info("removing HTML folder")
        if not self.keep_build_dir:
            shutil.rmtree(self.build_dir, ignore_errors=True)

        logger.info("all done!")

    def make_build_folder(self):
        """prepare build folder before we start downloading data"""

        # create build folder
        os.makedirs(self.build_dir, exist_ok=True)
        for fname in ("favicon.png", "main-logo.png"):
            shutil.copy2(
                self.templates_dir.joinpath(fname),
                self.build_dir.joinpath(fname),
            )

    def check_branding_values(self):
        """checks that user-supplied images and colors are valid (so to fail early)

        Images are checked for existence or downloaded then resized
        Colors are check for validity"""

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
            (self.main_logo, self.build_dir.joinpath("main-logo.png"), 300, 65),
            (
                self.secondary_logo,
                self.build_dir.joinpath("secondary-logo.png"),
                300,
                65,
            ),
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
                "--secondary_color-color is not a valid hex color: "
                f"{self.secondary_color}"
            )

        if self.about:
            handle_user_provided_file(
                source=self.about, dest=self.build_dir / "about.html"
            )

    def check_description_length(self):
        if len(self.description) > MAXIMUM_DESCRIPTION_METADATA_LENGTH:
            raise ValueError(
                "--The description is greater "
                f"than {MAXIMUM_DESCRIPTION_METADATA_LENGTH} characters: "
                f"{len(self.description)} characters"
            )
        if self.long_description is not None:
            if len(self.long_description) > MAXIMUM_LONG_DESCRIPTION_METADATA_LENGTH:
                raise ValueError(
                    "--The Long Description is greater "
                    f"than {MAXIMUM_LONG_DESCRIPTION_METADATA_LENGTH} characters: "
                    f"{len(self.long_description)} characters"
                )

    def update_metadata(self):
        self.fname = Path(
            self.fname if self.fname else f"{self.name}_{self.period}.zim"
        )
        self.title = self.title or self.name
        self.creator = self.creator or "Unknown"
        self.publisher = self.publisher or "openZIM"
        self.tags = self.tags or []

        # generate ICO favicon (fallback for browsers)
        create_favicon(
            self.build_dir.joinpath("favicon.png"),
            self.build_dir.joinpath("favicon.ico"),
        )

        # set colors from images if not supplied
        main_color, secondary_color = "#95A5A6", "#95A5A6"
        if self.main_logo:
            main_color = secondary_color = get_colors(
                self.build_dir.joinpath("main-logo.png")
            )[1]
        self.main_color = self.main_color or main_color
        self.secondary_color = self.secondary_color or secondary_color

        # get about content from param, archive or defaults to desc

        # setting the about_content to long_description if it is provided by the user
        self.about_content = f"<p>{self.long_description or self.description}</p>"
        about_source = self.build_dir / "about.html"
        if about_source.exists():
            with open(about_source, "r") as fh:
                self.about_content = fh.read()
            about_source.unlink(missing_ok=True)

    def download_archive(self):
        # download if it's a URL
        if self.archive.startswith("http"):
            logger.info(f"Downloading archive at {self.archive}")
            save_large_file(self.archive, self.archive_path)

    def extract_to_fs(
        self, name: str, failsafe: Optional[bool] = False
    ) -> pathlib.Path:
        """extracting single archive member `name` to filesystem at `to`"""

        with zipfile.ZipFile(self.archive_path, "r") as zh:
            try:
                normalized_name = zh.extract(member=name, path=self.build_dir)
                return self.build_dir.joinpath(normalized_name)
            except Exception as exc:
                logger.error(f"Unable to extract {name} from archive: {exc}")
                if failsafe:
                    return
                raise exc

    def test_collection(self):
        with open(self.collection, "r") as fp:
            self.json_collection = [i for i in json.load(fp) if i.get("files", [])]
        nb_items = len(self.json_collection)
        nb_files = sum([len(i.get("files", [])) for i in self.json_collection])
        logger.info(f"Collection loaded. {nb_items} items, {nb_files} files")

        with zipfile.ZipFile(self.archive_path, "r") as zh:
            all_names = zh.namelist()

        missing_files = []
        for entry in self.json_collection:
            if not entry.get("files"):
                continue
            for relative_path in entry["files"]:
                if relative_path not in all_names:
                    missing_files.append(relative_path)

        if missing_files:
            raise ValueError(
                "File(s) referenced in collection but missing:\n - "
                + "\n - ".join(missing_files)
            )

    def process_collection_entries(self):
        for entry in self.json_collection:
            if not entry.get("files"):
                continue

            for relative_path in entry["files"]:
                logger.debug(f"> {relative_path}")
                self.zim_creator.add_item_for(
                    path="files/" + normalized_path(relative_path),
                    fpath=self.extract_to_fs(relative_path),
                    delete_fpath=True,
                    is_front=False,
                )

    def add_ui(self):
        """make up HTML structure to read the content"""

        for fname in (
            "favicon.ico",
            "favicon.png",
            "main-logo.png",
            "secondary-logo.png",
        ):
            fpath = self.build_dir.joinpath(fname)
            if fpath.exists():
                self.zim_creator.add_item_for(path=fname, fpath=fpath)

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)), autoescape=True
        )

        # build homepage
        html = env.get_template("home.html").render(
            debug=str(self.debug).lower(),
            title=self.title,
            description=self.description,
            long_description=self.long_description,
            main_color=self.main_color,
            secondary_color=self.secondary_color,
            db_name=f"{self.name}_{self.period}_{uuid.uuid4().hex}_db",
            db_version=1,
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
        self.zim_creator.add_item_for(
            path="home", content=html, mimetype="text/html", is_front=True
        )

        initjs = env.get_template("init.js").render(
            debug=str(self.debug).lower(),
            title=self.title,
            description=self.description,
            db_name=f"{self.name}_{self.period}_{uuid.uuid4().hex}_db",
            db_version=1,
            nb_items_per_page=self.nb_items_per_page,
            show_author=self.show_author,
            show_description=self.show_description,
            randomize=self.randomize,
            loading_label=_("Loading…"),
        )
        self.zim_creator.add_item_for(
            path="init.js",
            content=initjs,
            mimetype="text/javascript",
            is_front=False,
        )

        database_js = "var DATABASE = [\n"
        for docid, document in enumerate(self.json_collection):
            database_js += "{},\n".format(
                str(
                    {
                        "_id": str(docid).zfill(5),
                        "ti": document.get("title") or "Unknown?",
                        "dsc": document.get("description") or "",
                        "aut": document.get("authors") or "",
                        "fp": [
                            normalized_path(path) for path in document.get("files", [])
                        ],
                    }
                )
            )
        database_js += "];\n"
        self.zim_creator.add_item_for(
            path="database.js",
            content=database_js,
            mimetype="text/javascript",
            is_front=False,
        )

        # recursively add all templates's folder
        for fpath in self.templates_dir.glob("**/*"):
            if not fpath.is_file():
                continue
            path = str(fpath.relative_to(self.templates_dir))

            logger.debug(f"> {path}")
            self.zim_creator.add_item_for(path=path, fpath=fpath, is_front=False)
