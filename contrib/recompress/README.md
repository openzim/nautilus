recompress helpers
===

scripts to easily recompress all files of a folder, for use in nautilus.

# Usage

```sh
docker build . -t recompress
docker run -v $(pwd):/data recompress recompress_tree.py --src /data/source --dst /data/dest --compress-args "--fallback copy"
```
