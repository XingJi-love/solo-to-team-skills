import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('release_build', Path(__file__).parents[1] / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class OriginalNoticeTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.previous = build.ROOT
        build.ROOT = self.root
        self.old = b'Original licensed material notice.\n'
        digest = hashlib.sha1(b'blob ' + str(len(self.old)).encode() + b'\0' + self.old).hexdigest()
        self.read = build.source_reader({'original_git_blobs': {'NOTICE': digest}})
        self.frozen = self.root / 'mas/release/original-notices/NOTICE'
        self.frozen.parent.mkdir(parents=True)
        self.frozen.write_bytes(self.old)
        (self.root / 'NOTICE').write_text('New repository scope for new materials.\n')

    def tearDown(self):
        build.ROOT = self.previous
        self.temporary.cleanup()

    def test_current_notice_cannot_change_frozen_package(self):
        self.assertEqual(self.read('NOTICE'), self.old)

    def test_changed_original_still_rejected(self):
        self.frozen.write_bytes(b'Altered original.\n')
        with self.assertRaisesRegex(ValueError, 'Original repository blob changed: NOTICE'):
            self.read('NOTICE')

    def test_missing_original_does_not_fall_back_to_current(self):
        self.frozen.unlink()
        with self.assertRaisesRegex(ValueError, 'Expected a regular source file'):
            self.read('NOTICE')


if __name__ == '__main__':
    unittest.main()
