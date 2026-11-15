"""Build both public-facing download paths locally from source, or verify them."""
import argparse
import hashlib
import os
from pathlib import Path
import platform
import sys
import tempfile
import zipfile
import zlib

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as release

QUICK_NAME = 'quick-review.zip'
QUICK_PAGE = 'learn/try-review.html'
QUICK_ZIP_SHA = '192fcdb700265600ff48c0c345a4ab19598a24703cbcbd0212d5d4346785e0dd'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def existing(path, expected):
    if not os.path.lexists(path): return False
    if path.is_symlink() or not path.is_file():
        raise ValueError('Output is not a regular file: '+path.name)
    if digest(path)!=expected:
        raise FileExistsError('Different existing file preserved: '+path.name)
    return True

def verify_quick(path, page_sha):
    with zipfile.ZipFile(path) as archive:
        if archive.namelist()!=['Start-here.html']:raise ValueError('Quick ZIP has an unexpected file tree')
        if release.sha(archive.read('Start-here.html'))!=page_sha:
            raise ValueError('Quick ZIP contains a different exercise HTML')
    if digest(path)!=QUICK_ZIP_SHA:
        raise ValueError('Quick HTML matches, but ZIP bytes differ; check Python, zlib and ZIP metadata')

def write_quick(path, page):
    info=zipfile.ZipInfo('Start-here.html',(2026,11,11,0,0,0))
    info.create_system=3
    info.external_attr=0o600<<16
    with zipfile.ZipFile(path,'x') as archive:
        archive.writestr(info,page,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify',action='store_true',help='Check both existing downloads; never build or write.')
    args=parser.parse_args()
    cfg=release.load_json(release.HERE/'release.json')
    locked=release.load_json(release.HERE/'expected.json')
    full_name='Solo-to-Team-MAS-'+cfg['version']+'.zip'
    names={full_name:locked['sha256'],QUICK_NAME:QUICK_ZIP_SHA}
    for guide in ['README.md','README.en.md']:
        text=(release.ROOT/'mas'/guide).read_text(encoding='utf-8')
        for name in names:
            if '(downloads/'+name+')' not in text:
                raise ValueError('The download link is absent from mas/'+guide+': '+name)
    directory=release.ROOT/'mas/downloads'
    if directory.is_symlink() or directory.resolve()!=directory:
        raise ValueError('The download directory must not be a symbolic link')
    if not args.verify:directory.mkdir(exist_ok=True)
    destinations={name:directory/name for name in names}
    # Examine every destination before considering a write to either of them.
    have={name:existing(path,names[name]) for name,path in destinations.items()}
    if args.verify:
        if not all(have.values()):
            raise FileNotFoundError('Missing: '+', '.join(n for n in names if not have[n]))
    elif not all(have.values()):
        with tempfile.TemporaryDirectory(prefix='.mas-build-',dir=directory) as tmp:
            stage=Path(tmp)
            files=release.make_files(cfg,locked)
            if not have[full_name]:release.write(files,stage/full_name,cfg,locked)
            if not have[QUICK_NAME]:
                write_quick(stage/QUICK_NAME,files[QUICK_PAGE])
                verify_quick(stage/QUICK_NAME,locked['files'][QUICK_PAGE])
            created=[]
            try:
                for name,path in destinations.items():
                    if have[name]:continue
                    try:
                        os.link(stage/name,path)
                        created.append((stage/name,path))
                    except FileExistsError:
                        existing(path,names[name])
            except Exception:
                for staged,path in reversed(created):
                    # Roll back only links this invocation actually created.
                    if not path.is_symlink() and path.exists() and os.path.samefile(staged,path):path.unlink()
                raise
    release.verify(destinations[full_name],cfg,locked)
    verify_quick(destinations[QUICK_NAME],locked['files'][QUICK_PAGE])
    for name,expected in names.items():print(expected+'  mas/downloads/'+name)

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,zipfile.BadZipFile) as exc:
        sys.exit(str(exc)+'\nRuntime: Python '+platform.python_version()+', zlib '+zlib.ZLIB_RUNTIME_VERSION)
