# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1]

### Fixed

- Missing libmagic in docker image

## [1.2.0]

### Added

- Add urls support to collections. (#59)
- Add archiveless collection.json support. (#60)

### Changed

- URL entries are checked early to exit should access fails (#29)
- Simplified [long]description checks using compute_descriptions
- Using PouchDB 8.0.1 (#45)

### Fixed

- Header link to home was leading to template (#68)

## [1.1.1] - 2023-05-05

### Changed

- Fixed ZIP acces when using a remote file

## [1.1.0] - 2023-05-05

### Added

- `--longdescription` (<=4000chars) ZIM Metadata (used instead of --description when there's no about.html)

### Changed

- `--description` is now mandatory and must be <= 80 chars
- using libzim directly (not via filesystem)
  - ZIP archive is not extracted to filesystem anymore
  - Only files referenced in collection are considered
  - Files are extracted one by one to filesystem and added to ZIM (then removed)
  - Files referenced in JSON but not present in ZIP halts the process
- Supports multiple language codes (comma separated)
- Unicode file paths are normalized

### Removed

- `--no-zim` param. not possible anymore
- `--skip-download` param. Input is a ZIP (local or remote)

## [1.0.8] - 2022-10-03

### Changed

- Replaced zimwriterfs with zimscraperlib –using libzim 7 without namespaces– (#41)
- Removed inline javascript to comply with some CSP (#34)

## [1.0.7] - 2022-01-04

- removed inline JS in homepage (#34)
- fixed ordering of documents (#32)

## [1.0.6] - 2021-06-10

- fixed usage on older browsers (without ES6 support)
- fixed behavior when no providing an about page
- fixed broken links on files with special chars
- using zimwriterfs 2.1.0-1

## [1.0.5]

- Hide Picture-in-Picture toggle on videos

## [1.0.4]

- Using zimcraperlib 1.0.6+ to fix translation

## [1.0.3]

- Fixed docker image

## [1.0.2]

- Using zimcraperlib 1.0.5+
- adjusting log level (DEBUG) on `--debug`
- --archive to work with user's home path (~)
- Added support for multi-format items #11
- Fixed i18n #13
- Added support for videos (and more audio formats) #2
- Updated zimwriterfs to 1.3.9
- Added support for custom about page
- Inifinite scroll disabled if nb of items <= pagination #18
- Added --no-random option to disable randomization #15

## [1.0.1]

- using zimscraperlib 1.0.2
- using handle_user_provided_file from lib
- changed charset position to overcome libkiwix issue
- fixed link on logo (was /)
- enabled history-friendly, shareable navigation
- not displaying description by default, added --show-description
- using native decoding for <audio/> if supported
- fixed popup margin on smaller screens

## [1.0.0]

- initial version
