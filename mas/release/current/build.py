"""Build a complete Solo to Team candidate from the verified previous release and a reviewed overlay."""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

HERE = Path(__file__).resolve().parent
ROOT = 'Solo-to-Team/'
BASE = '5e2f86298c08182eb7f2f3500ff767adc4b2a21e59a64a8c5c6993333f5b4d73'
OLD_VERSION = '0.2.2-rc.5'
LICENSE_OVERRIDES = {'core/RIGHTS.md', 'source/SOURCES.md'}
BASE_EDITS = {'index.html', 'README.md', 'README.en.md', 'SCOPE.md', 'checksums.json', 'proof/authority/returned/README.md', 'core/RIGHTS.md', 'source/SOURCES.md', 'core/checksums.json'}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def as_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()

def safe_path(name):
    if (not name or '\\' in name or ':' in name or name.startswith('/')
            or any(part in ('', '.', '..') for part in name.split('/'))):
        raise ValueError('Unexpected path: '+repr(name))
    return name

def load_archive(path):
    data = path.read_bytes()
    if digest(data) != BASE:
        raise ValueError('The input must be the reviewed 0.2.2-rc.5 archive')
    with ZipFile(io.BytesIO(data)) as archive:
        files = {}
        for entry in archive.infolist():
            if not entry.filename.startswith(ROOT):
                raise ValueError('Unexpected root')
            name = safe_path(entry.filename[len(ROOT):])
            if name in files:
                raise ValueError('Repeated source member: '+name)
            files[name] = archive.read(entry)
    manifest = json.loads(files['checksums.json'])
    if manifest['files'] != {n:digest(b) for n,b in files.items() if n!='checksums.json'}:
        raise ValueError('Original manifest mismatch')
    return files, manifest

def tree(files, folder):
    prefix=folder+'/'
    names=sorted((n for n in files if n.startswith(prefix)), key=str.encode)
    return {'file_count':len(names),'sha256':digest(''.join(digest(files[n])+'  '+n[len(prefix):]+'\n' for n in names).encode())}

def overlay_files():
    root=HERE/'overlay'
    lock=json.loads((HERE/'overlay.lock.json').read_bytes())
    files={}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('No symlinks in overlay')
        if path.is_file():
            name=safe_path(path.relative_to(root).as_posix())
            files[name]=path.read_bytes()
    if {n:digest(b) for n,b in files.items()}!=lock['files']:
        raise ValueError('Overlay source differs from its manifest')
    node=shutil.which('node')
    if not node:
        raise RuntimeError('Use an available Node.js runtime to rebuild the local application pages')
    with tempfile.TemporaryDirectory(prefix='solo-team-pages-') as temporary:
        for component in ('team-16','start-with-files','update-team'):
            target=Path(temporary)/(component+'.html')
            subprocess.run([node,str(root/component/'source/build.mjs'),str(target)],
                           cwd=temporary,check=True,stdout=subprocess.DEVNULL)
            if target.read_bytes()!=files[component+'/index.html']:
                raise ValueError('The bundled page differs from its source: '+component)
    return files,lock['version']

def replace_one(data,old,new):
    if data.count(old)!=1:
        raise ValueError('Cannot find unambiguous edit in the reviewed base')
    return data.replace(old,new,1)

def make_product(base):
    files, previous=load_archive(base)
    original=dict(files)
    custom,version=overlay_files()
    if not re.fullmatch(r'0\.3\.0-rc\.[1-9][0-9]*',version):
        raise ValueError('Unexpected preview version')
    collisions = set(files) & set(custom)
    if 'classic.html' in files or 'classic.html' in custom or collisions-({'index.html'} | LICENSE_OVERRIDES):
        raise ValueError('Overlay collides with existing content')
    if not LICENSE_OVERRIDES.issubset(collisions):
        raise ValueError('Missing current license override')
    classic=files['index.html'].decode()
    classic=replace_one(classic,'队内候选 · 新增内容尚未分配公开许可','发布候选 · 项目自制材料按 MIT 使用；范围见 <a href="NOTICE">NOTICE</a>')
    classic=replace_one(classic,'Internal candidate · No public distribution license has been assigned to the new material.','Release candidate · Project-authored materials use MIT; see <a href="NOTICE">NOTICE</a> for scope.')
    files['classic.html']=classic.encode()
    files.update(custom)
    if 'index.html' not in custom:
        raise ValueError('Missing new home page')
    files['index.html']=replace_one(files['index.html'].decode(),'[[PACKAGE_VERSION]]',version).encode()
    for suffix, language in [('md','zh'),('en.md','en')]:
        name='README.'+suffix
        content=files[name].decode()
        first,body=content.split('\n',1)
        if language=='zh':
            note='\n**从这里上手。** [打开项目工作台](index.html) · [选择 16 席团队](team-16/index.html) · [带自己的底稿](start-with-files/index.html) · [看实际印样](proof/pottery/labels.pdf) · [先用三席跑入门首单](classic.html)。\n'
        else:
            note='\n**Start here.** [Open the project desk](index.html#en) · [Choose the 16-role team](team-16/index.html#en) · [Bring your own files](start-with-files/index.html#en) · [See the print proof](proof/pottery/README.en.md) · [Try a three-role first task](classic.html#en).\n'
        if language=='zh':
            body=replace_one(body,'**队内候选 · 新增内容尚未分配公开许可**','**发布候选 · 所列项目自制材料采用 [MIT](LICENSE)，允许商用；范围和例外见 [NOTICE](NOTICE)。**')
            body=replace_one(body,'## 在我的平台跑首单','## 在我的平台跑首单\n\n以下平台说明与验证记录对应保留的三/四席首单包。当前16席团队请按[16席安装指引](team-16/SETUP.zh.md)采用；rc.4的实际观察与限制见[16席验证记录](team-16/VERIFICATION.zh.md)，不代表后续版本已重新完成全部业务验收。')
            body=replace_one(body,'[组建自己的团队](builder/四端统一建队台.html)','[组建自己的团队](team-16/index.html)')
            body=replace_one(body,'[开发者源码](source/README.md) · 查看本候选包的源码与复现入口。','[当前组件源码与重建](SOURCE.md) · 16席建队器、带底稿和配置更新的源码入口；旧 source/ 留作历史版本核对。')
            body=replace_one(body,'[现行统一建队台](builder/四端统一建队台.html)。核心保留早期建队器供原版复查。','[当前16席建队台](team-16/index.html) · [历史0.2.2b建队台](builder/四端统一建队台.html)。旧版保留原字节供复查。')
        else:
            body=replace_one(body,'**Internal candidate · No public distribution license has been assigned to the new material.**','**Release candidate · The listed project-authored materials use [MIT](LICENSE), including commercial use; see [NOTICE](NOTICE) for scope and exclusions.**')
            body=replace_one(body,'The animated preview below is formatted for GitHub; this showcase is pending publication.','The animated preview below is formatted for GitHub.')
            body=replace_one(body,'## Run it on your platform','## Run it on your platform\n\nThe platform notes below describe the retained three- and four-role starter packs. Use the [16-role setup guide](team-16/SETUP.en.md) for the current team. The [16-role verification record](team-16/VERIFICATION.en.md) reports the rc.4 observations and limits, not a new full business acceptance of later versions.')
            body=replace_one(body,'[Build your team](builder/四端统一建队台.html#en)','[Build your team](team-16/index.html#en)')
            body=replace_one(body,'[Developer source](source/README.md) · Inspect this candidate’s source and reproduction entry points.','[Current component source and rebuilding](SOURCE.md) · Source for the 16-role builder, file intake and team updater; source/ retains the historical version.')
            body=replace_one(body,'[Current unified builder](builder/四端统一建队台.html#en). The frozen core includes its earlier builder for historical verification.','[Current 16-role builder](team-16/index.html#en) · [Historical 0.2.2b builder](builder/四端统一建队台.html#en). Historical bytes remain available for comparison.')
        files[name]=(first+'\n'+note+replace_one(body,OLD_VERSION,version)).encode()
    scope=files['SCOPE.md'].decode()
    scope=replace_one(scope,'这是《一人成阵》组合包的队内候选。','这是《一人成阵》组合包的发布候选。')
    scope=replace_one(scope,'This is a private product review build.','This is a release candidate.')
    scope=replace_one(scope,'新增内容目前限队内使用。','所列项目自制材料采用 [MIT](LICENSE)，允许商用；范围与例外见 [NOTICE](NOTICE)。')
    scope=replace_one(scope,'a public distribution license has not been assigned to the new material in this build.','the listed project-authored materials use [MIT](LICENSE), including commercial use, within the scope and exclusions in [NOTICE](NOTICE).')
    scope=replace_one(scope,'统一建队台和可重建源码为 0.2.2b；core 里早期的建队器仅保留旧版核对，日常使用根目录 builder 里的现行版本','旧统一建队台和其 source/ 源码保留 0.2.2b；日常配置使用 team-16/ 中的16席建队台，当前组件源码入口见 SOURCE.md，旧 builder/ 与 core/ 建队器保留原版核对')
    scope=replace_one(scope,'the unified builder and its reproducible source are 0.2.2b.','the historical unified builder and its source/ directory retain version 0.2.2b.')
    scope=replace_one(scope,'Use the builder in the top-level builder directory for current exports.','Use team-16/ for current exports; SOURCE.md identifies the current component sources. The old builder/ is retained for historical comparison.')
    scope=replace_one(scope,'[统一建队台 / Current builder](builder/四端统一建队台.html) | 0.2.2b | 自配团队用这一份 / Use this for custom teams','[历史建队台 / Historical builder](builder/四端统一建队台.html) | 0.2.2b | 保留原版，不是当前16席入口 / Original bytes, not the current 16-role entry')
    scope=replace_one(scope,'[可重建源码 / Source](source/README.md) | 0.2.2b | 重建同版统一台 / Build the same HTML','[历史源码 / Historical source](source/README.md) | 0.2.2b | 仅重建旧统一台；当前见 SOURCE.md / Rebuilds the old builder only; current sources are in SOURCE.md')
    chinese='带底稿开工在本机准备文件，采用宿主后才会调用模型。陶艺展签为虚构业务样本，本机操作者记录了原生宿主中的制作、独立审核和原会话交回。异机复核覆盖所收到的文件与页面。旧四项技能的许可见其原件；新增项目自制材料的 MIT 范围见 NOTICE。'
    english='Preparing a workspace with your own files runs locally. The chosen host handles model use after setup. For the fictional pottery order, the Mac operator recorded production, independent review and return in the native host. Cross-machine review covered the received files and pages. NOTICE defines the MIT scope for the added project-authored materials.'
    new_rows=[
      '| [16 席团队 / 16-role team](team-16/index.html) | '+version+' | 16 岗、6 群、26 条建议群籍；按宿主实际能力启用 / 16 roles, six groups and 26 suggested memberships; activation depends on the host |',
      '| [带底稿 / Start with files](start-with-files/index.html) | '+version+' | 文件选择、原件清单及原生 DSH 项目 / File selection and a native DSH workspace |',
      '| [配置更新 / Update my team](update-team/index.html) | '+version+' | 三方对照与新配置下载 / Three-way comparison and a new configuration |',
      '| [首次使用 / First two checks](learn/first2.html) | '+version+' | 首次使用讲解，含合成题与退修示例 / First-use walkthrough with a fictional exercise and review examples |',
      '| [陶艺印样 / Pottery print proof](proof/pottery/README.md) | v1 | 虚构输入、实际产物 / Fictional inputs and actual artifacts |']
    files['SCOPE.md']=(replace_one(scope,OLD_VERSION,version)+'\n## 新增组件 / Added components\n\n| Component | Version | Scope |\n| --- | --- | --- |\n'+'\n'.join(new_rows)+'\n\n'+chinese+'\n\n'+english+'\n').encode()
    a='proof/authority/returned/README.md'
    files[a]=replace_one(files[a].decode(),'现场向南区报','南区现场主管报告').encode()
    files['core/checksums.json']=as_json({n[len('core/'):]:digest(b) for n,b in sorted(files.items())
                                      if n.startswith('core/') and n!='core/checksums.json'})
    changed={n for n in original if n!='checksums.json' and files[n]!=original[n]}
    if changed!=BASE_EDITS-{'checksums.json'}:
        raise ValueError('Unexpected change to base files: '+repr(changed))
    groups=set(previous['component_trees'])
    groups.update(n.split('/')[0] for n in custom if '/' in n)
    content={n:b for n,b in files.items() if n!='checksums.json'}
    trees={g:tree(content,g) for g in sorted(groups)}
    sources={k:v for k,v in previous['components'].items() if trees.get(k)==previous['component_trees'].get(k)}
    content['checksums.json']=as_json({'format':'solo-to-team.release-checksums','version':1,
      'product_version':version,'base_release':{'version':OLD_VERSION,'sha256':BASE},'component_trees':trees,
      'components':sources,'files':{n:digest(b) for n,b in sorted(content.items())}})
    return content

def build(path,output):
    content=make_product(path)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent,suffix='.partial',delete=False) as tmp:
        temp=Path(tmp.name)
    try:
        with ZipFile(temp,'w') as z:
            for n,data in sorted(content.items()):
                info=ZipInfo(ROOT+n,(2026,11,11,0,0,0))
                info.create_system=3
                info.external_attr=0o100644<<16
                z.writestr(info,data,compress_type=ZIP_DEFLATED,compresslevel=6)
        with ZipFile(temp) as z:
            if z.testzip() or any(z.read(ROOT+n)!=b for n,b in content.items()):
                raise ValueError('Final file check failed')
        sha=digest(temp.read_bytes())
        if output.exists():
            if output.is_symlink() or not output.is_file() or sha!=digest(output.read_bytes()):
                raise FileExistsError('Different destination already exists: '+str(output))
        else:
            try:
                os.link(temp,output)
            except FileExistsError:
                if output.is_symlink() or sha!=digest(output.read_bytes()):
                    raise
        print(f'{sha}  {output.name}  {len(content)} files, {output.stat().st_size} bytes')
    finally:
        temp.unlink(missing_ok=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    build(args.base,args.output)

