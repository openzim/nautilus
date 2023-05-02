#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import argparse
import logging
import os
import pathlib
import pprint
import shutil
import subprocess
import sys
import zipfile

import humanfriendly

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger("comp")

PDF, VIDEO, AUDIO, JPEG, PNG, EPUB = "pdf", "video", "audio", "jpeg", "png", "epub"
ALL_PRESETS = {
    PDF: ("gs-ebook", "qpdf", "gs-screen", "gs-printer", "gs-prepress", "gs-default"),
    JPEG: ("high", "medium", "low"),
    PNG: ("high", "medium", "low"),
    VIDEO: ("360p", "240p", "360p+", "yt2z"),
    AUDIO: ("ogg-48k", "mp3-48k"),
    EPUB: ("default",),
}
PRESETS = {key: value[0] for key, value in ALL_PRESETS.items()}

# update default presets via environ
for key in PRESETS.keys():
    PRESETS[key] = os.getenv(f"{key.upper()}_PRESET", PRESETS[key])

FALLBACK_IGNORE = "ignore"
FALLBACK_COPY = "copy"
FALLBACK_FAIL = "fail"
VIDEO_EXTENTIONS = (
    "webm",
    "ogv",
    "mp4",
    "mpg",
    "mpeg",
    "avi",
    "mkv",
    "mov",
    "wmv",
    "m4v",
    "h264",
    "3gp",
)
AUDIO_EXTENSIONS = ("ogg", "mp3", "aif", "mpa", "wav", "wma", "aiff")


def hsize(size):
    return humanfriendly.format_size(size, binary=True)


def run_args(args):
    logger.debug(" ".join(args))
    return subprocess.run(args, capture_output=True, text=True)


class Compressor:
    def __init__(self, src_path, dst_path, keep_ext, fallback, force, presets):
        self.src_path = src_path
        self.dst_path = dst_path
        self.keep_ext = keep_ext
        self.fallback = fallback
        self.force = force
        # custom presets
        self.presets = presets

    @staticmethod
    def recompress_epub(src_path, dst_path, preset):
        # exract epub to temp location
        epub_dir = dst_path.parent.joinpath(f"{dst_path.name}.folder")
        if epub_dir.exists():
            shutil.rmtree(epub_dir, ignore_errors=True)

        # compress all files inside that tree
        zipped_files = []
        with zipfile.ZipFile(f"{src_path}", "r") as zf:
            zipped_files = zf.namelist()
            zf.extractall(epub_dir)

        # loop through all files to recompress
        for fname in zipped_files:
            fpath = epub_dir.joinpath(fname)
            if fpath.suffix.lower() in (".png", ".jpeg", ".jpg", ".mp3"):
                Compressor(
                    fpath,
                    fpath,
                    keep_ext=True,
                    fallback=FALLBACK_COPY,
                    force=True,
                    presets={AUDIO: "mp3-48k", JPEG: "low", PNG: "low"},
                ).run()

        # recreate epub file
        with zipfile.ZipFile(f"{dst_path}", "w", zipfile.ZIP_DEFLATED) as zf:
            for fpath in zipped_files:
                zf.write(epub_dir.joinpath(fpath), fpath)

        # delete temp folder
        shutil.rmtree(epub_dir, ignore_errors=True)

        return subprocess.CompletedProcess(args=[], returncode=0, stdout="")

    @staticmethod
    def recompress_jpeg(src_path, dst_path, preset):
        quality = {"low": 25, "medium": 50, "high": 75}.get(preset)
        args = [
            "jpegoptim",
            "--strip-all",
            "--force",
            "--overwrite",
            "--preserve",
            "--preserve-perms",
            f"--dest={dst_path.parent}",
            f"--max={quality}",
            f"{src_path}",
        ]
        return run_args(args)

    @staticmethod
    def recompress_png(src_path, dst_path, preset):
        quality = {"low": "0-25", "medium": "0-50", "high": "0-75"}.get(preset)
        args = [
            "pngquant",
            "--strip",
            "--quality",
            f"{quality}",
            "--force",
            "--output",
            f"{dst_path}",
            f"{src_path}",
        ]
        return run_args(args)

    @staticmethod
    def recompress_audio(src_path, dst_path, preset):
        final_dst_path = None
        if src_path == dst_path:
            final_dst_path = pathlib.Path(dst_path)
            dst_path = dst_path.parent.joinpath(
                f"{dst_path.stem}.temp{dst_path.suffix}"
            )
        presets = {
            "ogg-48k": [
                "-codec:a",
                "libvorbis",
                # set sample rate
                "-ar",
                "44100",
                # constant bitrate
                "-b:a",
                "48k",
            ],
            "mp3-48k": [
                "-codec:a",
                "mp3",
                # set sample rate
                "-ar",
                "44100",
                # constant bitrate
                "-b:a",
                "48k",
            ],
        }

        args = ["ffmpeg", "-y", "-i", f"file:{src_path}", "-vn"]
        args += presets[preset]
        args += [f"file:{dst_path}"]

        ffmpeg = run_args(args)
        if dst_path.exists() and final_dst_path:
            dst_path.replace(final_dst_path)

        return ffmpeg

    @staticmethod
    def recompress_video(src_path, dst_path, preset):
        video_format = "webm"
        video_codecs = {"mp4": "h264", "webm": "libvpx"}
        audio_codecs = {"mp4": "aac", "webm": "libvorbis"}
        params = {"mp4": ["-movflags", "+faststart"], "webm": []}

        presets = {
            "yt2z": [
                # target video codec
                "-codec:v",
                video_codecs[video_format],
                # compression efficiency
                "-quality",
                "best",
                # increases encoding speed by degrading quality (0: don't speed-up)
                "-cpu-used",
                "0",
                # set output video average bitrate
                "-b:v",
                "300k",
                # quality range (min, max), the higher the worst quality
                # qmin 0 qmax 1 == best quality
                # qmin 50 qmax 51 == worst quality
                "-qmin",
                "30",
                "-qmax",
                "42",
                # constrain quality to not exceed this bitrate
                "-maxrate",
                "300k",
                # decoder buffer size, which determines the variability
                # of the output bitrate
                "-bufsize",
                "1000k",
                # nb of threads to use
                "-threads",
                "8",
                # change output video dimensions
                "-vf",
                "scale='480:trunc(ow/a/2)*2'",
                # target audio codec
                "-codec:a",
                audio_codecs[video_format],
                # set output audio average bitrate
                "-b:a",
                "128k",
            ],
            "240p": [
                "-codec:v",
                video_codecs[video_format],
                # keep good quality image
                "-qmin",
                "16",
                "-qmax",
                "26",
                # best compression
                "-quality",
                "best",
                # set constant rate
                "-minrate",
                "128k",
                "-maxrate",
                "128k",
                "-b:v",
                "128k",
                # scale to 240p 4:3, adding bars if necessary
                "-vf",
                "scale=426:240:force_original_aspect_ratio=decrease,"
                "pad=426:240:(ow-iw)/2:(oh-ih)/2",
                "-codec:a",
                audio_codecs[video_format],
                # constant bitrate
                "-b:a",
                "48k",
            ],
            "360p": [
                "-codec:v",
                video_codecs[video_format],
                # keep good quality image
                "-qmin",
                "16",
                "-qmax",
                "26",
                # best compression
                "-quality",
                "best",
                # set constant rate
                "-minrate",
                "192k",
                "-maxrate",
                "192k",
                "-b:v",
                "192k",
                # scale to 360p 4:3, adding bars if necessary
                "-vf",
                "scale=640:360:force_original_aspect_ratio=decrease,"
                "pad=640:360:(ow-iw)/2:(oh-ih)/2",
                "-codec:a",
                audio_codecs[video_format],
                # constant bitrate
                "-b:a",
                "48k",
            ],
            "360p+": [
                "-codec:v",
                video_codecs[video_format],
                # keep good quality image
                "-qmin",
                "16",
                "-qmax",
                "26",
                # best compression
                "-quality",
                "best",
                # set constant rate
                "-minrate",
                "384k",
                "-maxrate",
                "384k",
                "-b:v",
                "384k",
                # scale to 360p 4:3, adding bars if necessary
                "-vf",
                "scale=640:360:force_original_aspect_ratio=decrease,"
                "pad=640:360:(ow-iw)/2:(oh-ih)/2",
                "-codec:a",
                audio_codecs[video_format],
                # constant bitrate
                "-b:a",
                "48k",
            ],
        }

        args = ["ffmpeg", "-y", "-i", f"file:{src_path}"]
        args += presets[preset]
        args += params[video_format]
        args += ["-max_muxing_queue_size", "9999"]
        args += [f"file:{dst_path}"]

        return run_args(args)

    @staticmethod
    def recompress_pdf_qpdf(src_path, dst_path):
        return run_args(["qpdf", "--linearize", f"{src_path}", f"{dst_path}"])

    @staticmethod
    def recompress_pdf_ghostscript(src_path, dst_path, setting):
        if setting not in ("screen", "ebook", "printer", "prepress", "default"):
            raise ValueError("Unsupported `{setting}` setting for ghostscript.")

        return run_args(
            [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS=/{setting}",
                "-dNOPAUSE",
                "-dBATCH",
                "-dQUIET",
                f"-sOutputFile={dst_path}",
                f"{src_path}",
            ]
        )

    @staticmethod
    def recompress_pdf(src_path, dst_path, preset):
        # ghosscript presets are prefixed with gs-
        if preset.startswith("gs-"):
            return Compressor.recompress_pdf_ghostscript(
                src_path, dst_path, preset.split("-", 1)[1]
            )
        # other pdf presets
        return getattr(Compressor, f"recompress_pdf_{preset}")(src_path, dst_path)

    @staticmethod
    def copy_source_to_dest(src_path, dst_path):
        if src_path != dst_path:
            shutil.copyfile(src_path, dst_path)

    def get_target_for(self, fpath):
        ext = fpath.suffix.lower()[1:]
        target, preset, dst_ext = None, None, None
        if ext == "pdf":
            target = PDF
            preset = self.presets.get(PDF, PRESETS[PDF])
            dst_ext = "pdf"
        if ext in VIDEO_EXTENTIONS:
            target = VIDEO
            preset = self.presets.get(VIDEO, PRESETS[VIDEO])
            dst_ext = "webm"
        if ext in AUDIO_EXTENSIONS:
            target = AUDIO
            preset = self.presets.get(AUDIO, PRESETS[AUDIO])
            dst_ext = "mp3" if "mp3" in preset else "ogg"
        if ext in ("jpeg", "jpg"):
            target = JPEG
            preset = self.presets.get(JPEG, PRESETS[JPEG])
            dst_ext = ext
        if ext == "png":
            target = PNG
            preset = self.presets.get(PNG, PRESETS[PNG])
            dst_ext = ext
        if ext == "epub":
            target = EPUB
            preset = self.presets.get(EPUB, PRESETS[EPUB])
            dst_ext = ext

        return target, preset, dst_ext

    def run(self):
        # use fname from source if not full path supplied
        if self.dst_path.is_dir() or not self.dst_path.suffix:
            self.dst_path = self.dst_path.joinpath(self.src_path.name)

        # create dest folder if not exists
        if not self.dst_path.parent.exists():
            self.dst_path.parent.mkdir(parents=True, exist_ok=True)

        # find out what we'll do with this file
        target, preset, new_ext = self.get_target_for(self.src_path)

        # if we have no recompressor for this file type
        if not target:
            if self.fallback in (FALLBACK_IGNORE, FALLBACK_FAIL):
                logger.info(f"NOT re-compressing {self.src_path} (not supported)")
                return 0 if FALLBACK_IGNORE else 1
            if self.fallback == FALLBACK_COPY:
                self.copy_source_to_dest(self.src_path, self.dst_path)
                return 0

        # change destination extension unless asked not to
        if new_ext != self.dst_path.suffix[1:] and not self.keep_ext:
            self.dst_path = self.dst_path.parent.joinpath(
                f"{self.dst_path.stem}.{new_ext}"
            )

        # skip if destination already exists
        if self.src_path != self.dst_path and self.dst_path.exists() and not self.force:
            logger.info("Skipping (destination exists)")
            return 0

        logger.info(
            f"re-compressing {preset.upper()}: {self.src_path} -> {self.dst_path}"
        )

        src_size = self.src_path.stat().st_size
        ps = getattr(self, f"recompress_{target}")(self.src_path, self.dst_path, preset)
        if ps.returncode == 0:
            dst_size = self.dst_path.stat().st_size
            diff_size = (1 - (dst_size / src_size)) * 100
            logger.info(
                f"{self.src_path}: {hsize(src_size)} -> {hsize(dst_size)} "
                f"({diff_size:.1f}%)"
            )
            return 0

        logger.error(f"Failed to recompress:\n{ps.stdout}")
        return ps.returncode


def main():
    parser = argparse.ArgumentParser(
        prog="nautilus file recompressor",
        description="recompress a file for smaller size use in nautilus",
        epilog=f"Available presets:\n {pprint.pformat(ALL_PRESETS)}",
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
        "--fallback",
        help="Keep source file extension for target if not specified",
        choices=[FALLBACK_IGNORE, FALLBACK_COPY, FALLBACK_FAIL],
        default=FALLBACK_IGNORE,
        dest="fallback",
    )
    parser.add_argument(
        "--keep-ext",
        help="Keep source file extension for target if not specified",
        action="store_true",
        default=False,
        dest="keep_ext",
    )
    parser.add_argument(
        "--force",
        help="Recompress even if destination exists",
        action="store_true",
        default=False,
        dest="force",
    )

    for key in PRESETS.keys():
        parser.add_argument(
            f"--{key}-preset",
            help=f"Preset to use for {key.upper()} files. "
            f"Change default via {key.upper()}_PRESET environ",
            required=False,
            dest=f"{key}_preset",
            default=PRESETS[key],
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
        presets = {key: getattr(args, f"{key}_preset") for key in PRESETS.keys()}

        compressor = Compressor(
            args.src_path,
            args.dst_path,
            keep_ext=args.keep_ext,
            fallback=args.fallback,
            force=args.force,
            presets=presets,
        )
        sys.exit(compressor.run())
    except Exception as exc:
        logger.error(f"FAILED. An error occurred: {exc}")
        if args.debug:
            logger.exception(exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
