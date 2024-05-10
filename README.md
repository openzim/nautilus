
# Nautilus

`nautilus` turns a collection of documents into a browsable [ZIM file](https://openzim.org).

[![CodeFactor](https://www.codefactor.io/repository/github/openzim/nautilus/badge)](https://www.codefactor.io/repository/github/openzim/nautilus)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![codecov](https://codecov.io/gh/openzim/nautilus/branch/main/graph/badge.svg)](https://codecov.io/gh/openzim/nautilus)
[![PyPI version shields.io](https://img.shields.io/pypi/v/nautiluszim.svg)](https://pypi.org/project/nautiluszim/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nautiluszim.svg)](https://pypi.org/project/nautiluszim)
[![Docker](https://ghcr-badge.deta.dev/openzim/nautilus/latest_tag?label=docker)](https://ghcr.io/openzim/nautilus)

It downloads the video (webm or mp4 format – optionally recompress it in lower-quality, smaller size), the thumbnails, the subtitles and the authors' profile pictures ; then, it creates a static HTML files folder of it before creating a ZIM off of it.

# Preparing the archive

To be used with nautilus, your archive should be a ZIP file.
* it doesn't need to be structured, but it can.
* it doesn't need to be compressed. It's usually recommended not to.
* it should contain a `collection.json` file, but it can also be provided separately (see below).
* it should only contain to-be-included files. No filtering is done.
* Audio and video files should be in ogg format with an `.ogg`/`.ogv` extension to be supported on all platforms (`mp3`/`mp4` would work only on platforms with native support).

```
cd content/path
zip -r -0 -T ../content_name.zip *
```

## JSON collection file

Either inside the archive ZIP as `/collection.json` or elsewhere, 
specified via `--collection mycollection.json`, you must supply a JSON file describing your content.

The user-interface only gives access to files referenced properly in the collection.

At the moment, the JSON file needs to provide the following fields for each item in an array:

```json
[
    {
        "title": "...",
        "description": "...",
        "authors": "...",
        "files": ["relative/path/to/file"]
    },
    {
        "title": "...",
        "description": "...",
        "authors": "...",
        "files": [
            {
                "archive-member": "01 BOOK for printing .pdf",  // optional, member name inside archive (same as simpler format)
                "url": "http://books.com/310398120.pdf",  // optional, has precedence over `archive-member`, url to download file from
                "filename": "My book.pdf",  // optional, filename to use in ZIM, regardless of original one
            }
        ]
    }
]
```

## About page

Either inside the archive ZIP as `/about.html` or elsewhere, specified via `--about myabout.html`,

- You may supply an about page in HTML format. It will be displayed in a modal popup and will be included.
- At its bottom your *secondary-logo* if provided.

* Use only content tags (no `<html />` nor `<head />` nor `<script />` etc)
* Use inline styling if required, but no styling is recommended.
* Include one logo inline if required.

## Usage

```sh
❯ nautuluszim --help
usage: nautuluszim [-h] [-V]

# everything bundled in a ZIP
nautiluszim --archive my-content.zip

# In this mode every file entry must have a valid url.
nautiluszim --collection https://example.com/to-your-collection-file
```

### Installation

You'd want to install it in a dedicated virtual-environment (`python3 -m venv some-env && source ./some-env/bin/activate`)

```sh
❯ pip install nautiluszim
```

### Contributing

```sh
❯ pip install -e .
```

#### Notes

* On macOS, the locale setting is buggy. You need to launch it with the `LANGUAGE` environment variable (as ISO-639-1) for the translations to work.

```
LANGUAGE=fr nautiluszim --language fra
```

Nautilus adheres to openZIM's [Contribution Guidelines](https://github.com/openzim/overview/wiki/Contributing).

Nautilus has implemented openZIM's [Python bootstrap, conventions and policies](https://github.com/openzim/_python-bootstrap/docs/Policy.md) **v1.0.0**.
