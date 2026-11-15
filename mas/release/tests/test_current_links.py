"""Regression checks for the current download links, without building archives."""
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("current_download_builder", HERE / "build-current.py")
current = importlib.util.module_from_spec(spec)
spec.loader.exec_module(current)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.hrefs.extend(v for k, v in attrs if k == "href" and v is not None)


class CurrentLinksTest(unittest.TestCase):
    def setUp(self):
        self.name = current.locked_current()["filename"]
        self.quick = current.shared.QUICK_NAME
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "mas").mkdir()
        for name in ("README.md", "README.en.md"):
            (self.root / "mas" / name).write_text(
                "[full](downloads/" + self.name + ")\n[quick](downloads/" + self.quick + ")\n"
            )
        self.html = (
            "<a href='downloads/" + self.name + "'>Full</a>"
            '<a href="downloads/' + self.quick + '">Quick</a>'
        )
        for name in ("index.html", "index.en.html"):
            (self.root / "mas" / name).write_text(self.html)

    def run_verify(self, expected_error=None):
        with patch.object(current.frozen, "ROOT", self.root), \
             patch.object(current.shared, "existing", return_value=True) as existing, \
             patch.object(current, "verify_pair") as verify, \
             patch.object(sys, "argv", ["build-current.py", "--verify"]):
            if expected_error:
                with self.assertRaisesRegex(ValueError, expected_error):
                    current.main()
                existing.assert_not_called()
                verify.assert_not_called()
            else:
                current.main()
                verify.assert_called_once()

    def test_shipped_html_links_match_current_pair(self):
        for guide in ("index.html", "index.en.html"):
            with self.subTest(guide=guide):
                parser = Links()
                parser.feed((HERE.parent / guide).read_text())
                downloads = [h for h in parser.hrefs if h.startswith("downloads/")]
                self.assertIn("downloads/" + self.name, downloads)
                self.assertIn("downloads/" + self.quick, downloads)
                stale = [h for h in downloads if h.startswith("downloads/Solo-to-Team-MAS-")
                         and h != "downloads/" + self.name]
                self.assertEqual(stale, [])

    def test_valid_single_and_double_quoted_html(self):
        self.run_verify()

    def test_both_languages_reject_old_only_link(self):
        for guide in ("index.html", "index.en.html"):
            with self.subTest(guide=guide):
                path = self.root / "mas" / guide
                path.write_text(self.html.replace(self.name, "Solo-to-Team-MAS-0.3.0-rc.3.zip"))
                self.run_verify("mas/" + guide)
                path.write_text(self.html)

    def test_old_second_button_rejected_even_with_current_link(self):
        path = self.root / "mas" / "index.html"
        path.write_text(self.html + '<a href="downloads/Solo-to-Team-MAS-0.3.0-rc.3.zip">Old button</a>')
        self.run_verify("mas/index.html")

    def test_link_inside_comment_does_not_count(self):
        path = self.root / "mas" / "index.html"
        path.write_text("<!--" + self.html + "-->")
        self.run_verify("mas/index.html")

    def test_plain_text_download_path_does_not_count(self):
        path = self.root / "mas" / "index.en.html"
        path.write_text("downloads/" + self.name + " downloads/" + self.quick)
        self.run_verify("mas/index.en.html")

    def test_missing_quick_download_rejected(self):
        path = self.root / "mas" / "index.en.html"
        path.write_text("<a href='downloads/" + self.name + "'>Full</a>")
        self.run_verify("mas/index.en.html")

    def test_existing_markdown_guard_is_preserved(self):
        (self.root / "mas" / "README.en.md").write_text("Missing download")
        self.run_verify("mas/README.en.md")


if __name__ == "__main__":
    unittest.main()
