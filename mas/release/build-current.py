"""Build the current two downloads and validate their README/HTML links. No release ZIP is an input."""
import argparse
from html.parser import HTMLParser
import importlib.util
import os
from pathlib import Path
import platform
import shutil
import sys
import tempfile
import zipfile
import zlib

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as frozen
import build_downloads as shared

spec = importlib.util.spec_from_file_location('current_overlay', HERE/'current/build.py')
overlay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overlay)

def locked_current():
    lock = frozen.load_json(HERE/'current.expected.json')
    source = frozen.load_json(HERE/'current/overlay.lock.json')
    if lock.get('format') != 1 or lock['version'] != source['version']:
        raise ValueError('Current source version and expected version differ')
    if lock['filename'] != 'Solo-to-Team-MAS-'+lock['version']+'.zip':
        raise ValueError('Current download filename differs from its version')
    return lock

def verify_pair(paths, lock):
    cfg = {'outer_prefix': 'Solo-to-Team/'}
    frozen.verify(paths[lock['filename']], cfg, lock)
    shared.verify_quick(paths[shared.QUICK_NAME], lock['files'][shared.QUICK_PAGE])

class DownloadLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.hrefs.extend(value for key, value in attrs
                              if key == 'href' and value is not None)

def verify_html_links(hashes, current_name):
    for guide in ('index.html', 'index.en.html'):
        links = DownloadLinks()
        links.feed((frozen.ROOT/'mas'/guide).read_text(encoding='utf-8'))
        for filename in hashes:
            if 'downloads/'+filename not in links.hrefs:
                raise ValueError('Current download link absent from mas/'+guide+': '+filename)
        stale = [href for href in links.hrefs
                 if href.startswith('downloads/Solo-to-Team-MAS-')
                 and href != 'downloads/'+current_name]
        if stale:
            raise ValueError('Stale download link in mas/'+guide+': '+', '.join(stale))

def install_pair(staged, paths, hashes, lock):
    # Both complete archives have already been verified; inspect both destinations
    # before linking either. Existing files are never replaced.
    for name, path in paths.items():
        shared.existing(path, hashes[name])
    created = []
    try:
        for name, path in paths.items():
            if shared.existing(path, hashes[name]):
                continue
            try:
                os.link(staged/name, path)
                created.append((staged/name, path))
            except FileExistsError:
                shared.existing(path, hashes[name])
        verify_pair(paths, lock)
    except BaseException:
        for source, path in reversed(created):
            # Roll back only our own still-identical links, never another writer.
            if not path.is_symlink() and path.exists() and os.path.samefile(source, path):
                path.unlink()
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true',
                        help='Verify the current two downloads only; no build or write.')
    args = parser.parse_args()
    lock = locked_current()
    name = lock['filename']
    hashes = {name: lock['sha256'], shared.QUICK_NAME: shared.QUICK_ZIP_SHA}
    for guide in ('README.md', 'README.en.md'):
        text = (frozen.ROOT/'mas'/guide).read_text(encoding='utf-8')
        for filename in hashes:
            if '(downloads/'+filename+')' not in text:
                raise ValueError('Current download link absent from mas/'+guide+': '+filename)
    verify_html_links(hashes, name)

    directory = frozen.ROOT/'mas/downloads'
    if directory.is_symlink() or directory.resolve() != directory:
        raise ValueError('The download directory must not be a symbolic link')
    paths = {n: directory/n for n in hashes}
    have = {n: shared.existing(p, hashes[n]) for n, p in paths.items()}
    if args.verify:
        if not all(have.values()):
            raise FileNotFoundError('Missing: '+', '.join(n for n in hashes if not have[n]))
        verify_pair(paths, lock)
    else:
        if not shutil.which('node'):
            raise ValueError('Node.js is required to rebuild the three bundled application pages')
        directory.mkdir(exist_ok=True)
        # Rebuild even when identical targets already exist, so changed sources
        # cannot be hidden by a stale completed download.
        with tempfile.TemporaryDirectory(prefix='.current-build-', dir=directory) as temp:
            stage = Path(temp)
            cfg = frozen.load_json(HERE/'release.json')
            old_lock = frozen.load_json(HERE/'expected.json')
            if cfg['version'] != '0.2.2-rc.5' or old_lock['sha256'] != overlay.BASE:
                raise ValueError('Frozen source and overlay base identities differ')
            try:
                old_files = frozen.make_files(cfg, old_lock)
                base = stage/'generated-base.zip'
                frozen.write(old_files, base, cfg, old_lock)
            except (OSError, ValueError) as exc:
                raise ValueError('Frozen source/page/archive stage: '+str(exc)) from exc
            try:
                files = overlay.make_product(base)
                frozen.compare(lock['files'], frozen.member_hashes(files),
                               'Current source-derived file tree differs')
                new_cfg = {'outer_prefix': 'Solo-to-Team/',
                           'timestamp': [2026, 11, 11, 0, 0, 0]}
                frozen.write(files, stage/name, new_cfg, lock)
                shared.write_quick(stage/shared.QUICK_NAME, files[shared.QUICK_PAGE])
                verify_pair({n: stage/n for n in hashes}, lock)
            except (OSError, ValueError) as exc:
                raise ValueError('Current source/page/archive stage: '+str(exc)) from exc
            install_pair(stage, paths, hashes, lock)
    for filename, expected in hashes.items():
        print(expected+'  mas/downloads/'+filename)

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        sys.exit(str(exc)+'\nRuntime: Python '+platform.python_version()
                 +', zlib '+zlib.ZLIB_RUNTIME_VERSION)

