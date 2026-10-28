import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from zimscraperlib.constants import DEFAULT_USER_AGENT

from nautiluszim.scraper import Nautilus


@pytest.fixture
def user_agent_server():
    """Local HTTP server recording (path, User-Agent) of each request it receives"""
    seen: list[tuple[str, str | None]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            seen.append((self.path, self.headers.get("User-Agent")))
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *_args, **_kwargs):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}", seen
    server.shutdown()
    server.server_close()
    thread.join()


class FakeZimCreator:
    """Stands in for the ZIM Creator, we only care about downloads here"""

    def add_item_for(self, **_kwargs):
        pass


def make_scraper(tmp_path, *, archive="", collection=None, **kwargs):
    if collection is None:
        collection = str(tmp_path / "collection.json")
    return Nautilus(
        archive=archive,
        collection=collection,
        nb_items_per_page=10,
        no_random=True,
        show_description=True,
        output_dir=str(tmp_path / "out"),
        fname="test.zim",
        debug=False,
        keep_build_dir=False,
        language="eng",
        locale_name="en",
        tags="test",
        name="test",
        title="test",
        creator="test",
        publisher="test",
        **kwargs,
    )


def write_collection(tmp_path, base_url):
    (tmp_path / "collection.json").write_text(
        json.dumps([{"title": "t", "files": [{"url": f"{base_url}/file.txt"}]}])
    )


def test_collection_urls_check_sends_scraperlib_user_agent(user_agent_server, tmp_path):
    """Direct requests: the early check of URLs in the collection"""
    base_url, seen = user_agent_server
    write_collection(tmp_path, base_url)
    scraper = make_scraper(tmp_path)

    scraper.test_all_urls()

    assert seen == [("/file.txt", DEFAULT_USER_AGENT)]


def test_archive_download_sends_scraperlib_user_agent(user_agent_server, tmp_path):
    """save_large_file: download of the archive"""
    base_url, seen = user_agent_server
    write_collection(tmp_path, base_url)
    scraper = make_scraper(tmp_path, archive=f"{base_url}/archive.zip")
    scraper.make_build_folder()

    scraper.download_archive()

    assert seen == [("/archive.zip", DEFAULT_USER_AGENT)]


def test_collection_file_download_sends_scraperlib_user_agent(
    user_agent_server, tmp_path
):
    """save_large_file: download of the files of the collection"""
    base_url, seen = user_agent_server
    write_collection(tmp_path, base_url)
    scraper = make_scraper(tmp_path)
    scraper.make_build_folder()
    scraper.load_collection()
    scraper.zim_creator = FakeZimCreator()

    scraper.process_collection_entries()

    assert seen == [("/file.txt", DEFAULT_USER_AGENT)]


def test_collection_url_download_sends_scraperlib_user_agent(
    user_agent_server, tmp_path
):
    """handle_user_provided_file (stream_file): collection given as a URL"""
    base_url, seen = user_agent_server

    make_scraper(tmp_path, collection=f"{base_url}/collection.json")

    assert seen == [("/collection.json", DEFAULT_USER_AGENT)]


def test_branding_url_download_sends_scraperlib_user_agent(user_agent_server, tmp_path):
    """handle_user_provided_file (stream_file): branding files given as URL"""
    base_url, seen = user_agent_server
    write_collection(tmp_path, base_url)
    scraper = make_scraper(tmp_path, about=f"{base_url}/about.html")
    scraper.make_build_folder()

    scraper.check_branding_values()

    assert seen == [("/about.html", DEFAULT_USER_AGENT)]
