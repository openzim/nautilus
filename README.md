Nautilus
=============

[![CodeFactor](https://www.codefactor.io/repository/github/openzim/nautilus/badge)](https://www.codefactor.io/repository/github/openzim/nautilus)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version shields.io](https://img.shields.io/pypi/v/nautiluszim.svg)](https://pypi.org/project/nautiluszim/)

`nautilus` turns a collection of documents into a browsable [ZIM file](https://openzim.org).

It downloads the video (webm or mp4 format – optionnaly recompress them in lower-quality, smaller size), the thumbnails, the subtitles and the authors' profile pictures ; then, it create a static HTML files folder of it before creating a ZIM off of it.

# Preparing the archive

To be used with nautilus, your archive should be a ZIP file.

* it doesn't need to be structured, but it can.
* it doesn't need to be compressed. It's usually recommended not to.
* it should contain a `collection.json` file, but it can also provided separately (see below).
* it should only contain to-be-included files. No filtering is done.
* Audio and video files should be in ogg format with `.ogg`/`.ogv` extension to be supported on all platform (`mp3`/`mp4` would work only on platform with native support).

```
cd content/path
zip -r -0 -T ../content_name.zip *
```

## JSON collection file

Either inside the archive ZIP as `/collection.json` or elsewhere, 
specified via `--collection mycollection.json`, you must supply a JSON file describing your content.

The user-interface only gives access to files referenced properly in the collection.

At the moment, the JSON files needs to provide the following fields for each item in an Array:

``` JSON
[
    {
        "title": "...",
        "description": "...",
        "authors": "...",
        "files": ["relative/path/to/file"]
     }
]
```

## About page

Either inside the archive ZIP as `/about.html` or elsewhere, specified via `--about myabout.html`,
you may supply an about page in HTML format. It will be displayed in a modal popup and will include
at its bottom your *secondary-logo* if provided.

* Use only content tags (no `<html />` nor `<head />` nor `<script />` etc)
* Use inline styling if required but no styling is recommended.
* Include one logo inline if required.

# Requirements

* [`zimwriterfs`](https://github.com/openzim/zimwriterfs) for ZIM file packaging. Use `--no-zim` to skip this step.
* `wget` and `unzip` to install JS dependencies. See `get_js_deps.sh` if you want to do it manually.
* `wget` is used to download archive files as well.
* [`handlebars`](https://handlebarsjs.com) is used to compile JS templates

# Installation

`nautilus` is a python program. if you are not using the docker image, you are advised to use it in a virtualenv. See `requirements.txt` for the list of python dependencies.

## docker

```
docker run -v my_dir:/output openzim/nautilus nautiluszim --help
```

## pip

```
pip install nautiluszim
nautiluszim --help
```

# Usage

```
nautiluszim --archive my-content.zip
```

## Notes

* On macOS, the locale setting is buggy. You need to launch it with `LANGUAGE` environment variable (as ISO-639-1) for the translations to work.

```
LANGUAGE=fr nautiluszim --language fra
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md)
