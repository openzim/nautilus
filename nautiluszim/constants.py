#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import pathlib
import logging

from zimscraperlib.logging import getLogger

NAME = pathlib.Path(__file__).parent.name
VERSION = "1.0.0"
SCRAPER = f"{NAME} {VERSION}"

ROOT_DIR = pathlib.Path(__file__).parent

logger = getLogger(NAME, level=logging.DEBUG)
