# nautilus devel


## setup

__Note__: make sure you've installed non-python dependencies first, as mentioned in the [README](README.md).

Then, setup a python `virtualenv` using `python 3.6+` and install our python dependencies using `pip`:

```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py  # you may use sudo
pip install -U virtualenv  # sudo to install globally
virtualenv -p python3.6 nautilus-env
source nautilus-env/bin/activate
pip install -r requirements.txt
```

You now have an isolated python installation in the `./nautilus-env/` folder, containing all the python dependencies.

__Note__: you must activate the `virtualenv` before running the scraper so it uses this virtual python installation

``` bash
source nautilus-env/bin/activate
```

and then run it:

``` bash
python nautiluszim --help
# or, without activating the virtualenv:
nautilus-env/bin/python nautiluszim --help
```

_Note_: when using raw source, you need to compile JS templates first (see bellow).

## contributions

* Open issues, bug reports and send PRs [on github](https://github.com/openzim/nautilus).
* Make sure it's `py3.6+` compatible.
* Use [black](https://github.com/psf/black) code formatting.

#### templates

In-JS templates uses [handlebars](https://handlebarsjs.com). When editing them, always recompile them all into precompiled.js:

```
handlebars nautiluszim/templates -f nautiluszim/templates/assets/templates/precompiled.js
```

## notes

In order to support all platform for audio/video playback, we use `ogv.js`, to play ogv/ogg files on browsers that don't support it. Using `video.js`, we default to native playback if supported.

`ogv.js` is an emscripten-based JS decoder for webm and thus dynamically loads differents parts at run-time on platforms that needs them. It has two consequences:

* `file://` scheme doesn't work as the binary `.wasm` files are sent naively as `text/html` instead of `application/oct-stream`. If you want to use the HTML generated folder instead of ZIM, serve it through a web server and [configure the Content-Type response](https://emscripten.org/docs/compiling/WebAssembly.html#web-server-setup).
* [ZIM](https://wiki.openzim.org/wiki/ZIM_file_format) places JS files under the `/-/` namespace and binary ones under the `/I/` one. Dynamically loading of JS and WASM files within `ogv.js` requires us to tweak it to introduce some ZIM-specific logic. See `fix_ogvjs_dist.py`.


## i18n

`nautilus` has very minimal non-content text but still uses gettext through [babel](http://babel.pocoo.org/en/latest/) to internationalize.

To add a new locale (`fr` in this example, use only ISO-639-1):

1. init for your locale: `pybabel init -d nautiluszim/locale -l fr -i nautiluszim/locale/messages.pot`
2. make sure the POT is up to date `pybabel extract -o nautiluszim/locale/messages.pot nautiluszim`
3. update your locale's catalog `pybabel update -d nautiluszim/locale/ -l fr -i nautiluszim/locale/messages.pot`
3. translate the PO file ([poedit](https://poedit.net/) is your friend)
4. compile updated translation `pybabel compile -d nautiluszim/locale -l fr`

## releasing

* Update your dependencies: `pip install -U setuptools wheel twine`
* Make sure CHANGELOG is up-to-date
* Bump version on `nautiluszim/VERSION`
* Build packages `python ./setup.py sdist bdist_wheel`
* Upload to PyPI `twine upload dist/nautiluszim-1.0.0*`.
* Commit your CHANGELOG + version bump changes
* Tag version on git `git tag -a v1.0.0`
