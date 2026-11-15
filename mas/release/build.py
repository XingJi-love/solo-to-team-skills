"""Build or verify the complete checked-out MAS release. Python 3.9+ and Node are sufficient."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import zlib

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from archive_layout import build_zip
ROOT = HERE.parents[1]
def sha(data):
    return hashlib.sha256(data).hexdigest()
def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()
def load_json(path):
    return json.loads(path.read_bytes())

def safe_relative(name):
    if (not isinstance(name, str) or not name or '\\' in name or ':' in name
            or any(part in ('', '.', '..') for part in name.split('/'))):
        raise ValueError('Invalid relative path: '+repr(name))
    return PurePosixPath(name)

def member_hashes(files):
    return {name:sha(data) for name,data in sorted(files.items())}

def compare(expected, actual, label):
    if expected != actual:
        changed=sorted(k for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k))
        raise ValueError(f'{label}: {len(changed)} differences. First: '+', '.join(changed[:8]))

def tree_hashes(files, components):
    trees={}
    for component in components:
        prefix=component+'/'
        names=sorted((n for n in files if n.startswith(prefix)),key=str.encode)
        data=''.join(sha(files[n])+'  '+n[len(prefix):]+'\n' for n in names).encode()
        trees[component]={'file_count':len(names),'sha256':sha(data)}
    return trees

def source_reader(cfg):
    originals=cfg['original_git_blobs']
    def read_source(name):
        relative=safe_relative(name)
        if not (name in originals or name.startswith(('mas/source/','mas/media/','mas/evidence/',
                'mas/release/recipes/','mas/release/original-readmes/','mas/release/payload/'))):
            raise ValueError('Path outside release source set: '+name)
        # The current repository NOTICE may describe newer, separately scoped
        # material. Frozen skill packages retain the original notice, still
        # checked against its unchanged public-commit Git blob below.
        path=ROOT/('mas/release/original-notices/NOTICE' if name=='NOTICE' else relative)
        if path.resolve()!=path or not path.is_file() or path.suffix.lower()=='.zip':
            raise ValueError('Expected a regular source file (archives are built): '+name)
        data=path.read_bytes()
        if name in originals:
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if blob!=originals[name]:raise ValueError('Original repository blob changed: '+name)
        return data
    return read_source

def build_unified_page():
    node=shutil.which('node')
    if not node:raise SystemExit('Install/use an approved Node runtime to rebuild mas/source.')
    with tempfile.TemporaryDirectory(prefix='mas-page-') as temp:
        root=Path(temp);target=root/'team-builder.html'
        env={'PATH':os.environ.get('PATH',''),'HOME':temp,'TMPDIR':temp,'LANG':'C'}
        if os.name=='nt' and 'SystemRoot' in os.environ:env['SystemRoot']=os.environ['SystemRoot']
        subprocess.run([node,str(ROOT/'mas/source/build.mjs'),str(target)],cwd=root,env=env,check=True,
                       stdout=subprocess.DEVNULL)
        return target.read_bytes()

def make_files(cfg, locked, draft=False):
    read_source=source_reader(cfg)
    entries=cfg['entries'];files={}
    if not draft and set(entries)!=set(locked['files']):raise ValueError('Release recipe and locked file inventory differ')
    def expand_layout(name,seen=()):
        if name in seen:raise ValueError('Circular ZIP layout reference: '+name)
        layout=json.loads(read_source(name))
        for m in layout['members']:
            if 'archive' in m and 'layout' in m['archive']:
                m['archive']=expand_layout(m['archive']['layout'],seen+(name,))
        return layout
    for name,rule in entries.items():
        safe_relative(name)
        if 'file' in rule:
            data=read_source(rule['file'])
        elif 'template' in rule:
            src=read_source(rule['template']).decode()
            for key,asset in rule.get('base64',{}).items():
                if key not in src:raise ValueError('Missing asset placeholder in '+name)
                src=src.replace(key,base64.b64encode(read_source(asset)).decode())
            src=src.replace('[[MAS:version]]',cfg['version'])
            if '[[MAS:' in src:raise ValueError('Unresolved template field: '+name)
            data=src.encode()
        elif 'zip' in rule:
            data=build_zip(expand_layout(rule['zip']),read_source,verify=not draft)
        elif rule=={'generate':'team-builder'}:
            data=build_unified_page()
        elif (name in ('checksums.json','core/checksums.json')
              and rule=={'generate':name}):
            continue
        else:
            raise ValueError('Unrecognized source rule: '+name)
        files[name]=data
    core={n[len('core/'):]:v for n,v in files.items() if n.startswith('core/')}
    files['core/checksums.json']=json_bytes(member_hashes(core))
    trees=tree_hashes(files,cfg['component_archives'])
    current_components=dict(cfg['component_archives'])
    if draft:
        # A pinned upstream archive SHA must never be attributed to an edited component.
        for section,result in trees.items():
            if result!=cfg['component_trees'].get(section):current_components[section]=None
    else:
        compare(cfg['component_trees'],trees,'Frozen component tree differs')
    manifest={'format':'solo-to-team.release-checksums','version':1,'product_version':cfg['version'],
              'component_trees':trees,'components':current_components,'files':member_hashes(files)}
    if draft:manifest['build_origin']='Unapproved local source draft; null component archive fingerprints have no frozen upstream ZIP.'
    files['checksums.json']=json_bytes(manifest)
    if not draft:compare(locked['files'],member_hashes(files),'Candidate files differ')
    return files

def verify(archive, cfg, locked):
    hashes={}
    prefix=cfg['outer_prefix']
    with zipfile.ZipFile(archive) as z:
        for i in z.infolist():
            if not i.filename.startswith(prefix):raise ValueError('Unexpected archive root')
            name=i.filename[len(prefix):];safe_relative(name)
            if name in hashes:raise ValueError('Duplicate ZIP path: '+name)
            hashes[name]=sha(z.read(i))
    compare(locked['files'],hashes,'Archived file tree differs')
    value=sha(archive.read_bytes())
    if locked.get('sha256') is not None and value!=locked['sha256']:
        raise ValueError('File tree matches but the ZIP bytes differ; check Python/zlib and packaging metadata. '+value)
    return value,len(hashes)

def write(files, path, cfg, locked):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.partial',delete=False) as f:staged=Path(f.name)
    try:
        with zipfile.ZipFile(staged,'w') as out:
            for name,data in sorted(files.items()):
                i=zipfile.ZipInfo(cfg['outer_prefix']+name,tuple(cfg['timestamp']))
                i.create_system=3;i.external_attr=0o100644<<16
                out.writestr(i,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
        result=verify(staged,cfg,locked)
        if path.exists():
            if path.is_symlink() or not path.is_file() or sha(path.read_bytes())!=result[0]:
                raise FileExistsError('A different file exists at '+str(path))
        else:
            # A concurrent build may win; never replace the file it wrote.
            try:os.link(staged,path)
            except FileExistsError:
                if path.is_symlink() or verify(path,cfg,locked)!=result:raise
        return result
    finally:staged.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group()
    group.add_argument('--output',type=Path,help='New output path. Default: dist/<release filename>.')
    group.add_argument('--verify',type=Path,metavar='ZIP',help='Verify the complete file tree and exact archive hash only.')
    ap.add_argument('--draft',metavar='NEW_VERSION',help='Build edited sources as a new, explicitly unapproved local version.')
    a=ap.parse_args()
    cfg=load_json(HERE/'release.json');locked=load_json(HERE/'expected.json')
    if cfg['format']!=1 or locked['format']!=1 or locked['version']!=cfg['version']:raise ValueError('Inconsistent release recipe')
    if a.draft:
        if a.verify is not None or a.draft==cfg['version']:ap.error('A draft requires a different version; --verify checks the pinned release.')
        cfg={**cfg,'version':a.draft}
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z]+\.[0-9]+)?',cfg['version']):raise ValueError('Invalid release label')
    if a.verify is not None:
        dest=a.verify;res=verify(dest,cfg,locked)
    else:
        dest=a.output or ROOT/'dist'/('Solo-to-Team-MAS-'+cfg['version']+'.zip')
        files=make_files(cfg,locked,draft=bool(a.draft))
        check={'files':member_hashes(files),'sha256':None} if a.draft else locked
        res=write(files,dest,cfg,check)
        if a.draft:print('Unapproved local build '+cfg['version'])
    print(f'{res[0]}  {dest}  ({res[1]} files; zlib {zlib.ZLIB_RUNTIME_VERSION})')

if __name__=='__main__':main()
