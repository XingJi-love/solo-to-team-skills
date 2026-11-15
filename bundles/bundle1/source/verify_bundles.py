from pathlib import Path
import json,zipfile,hashlib,tempfile,re,sys
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parent.parent;O=ROOT/'packages'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SMALL=['dispatch-accept-verify','evidence-before-done','beginner-ops-writing','ops-case-notes']
class H(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src'] and v:self.links.append(v)
def link_check(root):
 count=0;missing=[];escapes=[]
 for f in root.rglob('*'):
  if not f.is_file() or f.suffix not in ['.md','.html']:continue
  # Authoring templates and test fixtures are sources, not shipped navigation pages.
  if '/source/' in '/'+str(f.relative_to(root)) or '/tests/' in '/'+str(f.relative_to(root)):continue
  text=f.read_text()
  if f.suffix=='.html':parser=H();parser.feed(text);links=parser.links
  else:
   text=re.sub(r'```.*?```','',text,flags=re.S);links=re.findall(r'\]\(([^)\n]+)\)',text)
  for raw in links:
   raw=raw.strip().strip('<>');u=urlsplit(raw)
   if u.scheme or u.netloc or not u.path:continue
   path=unquote(u.path);t=(f.parent/path).resolve();count+=1
   if not t.is_relative_to(root.resolve()):escapes.append([str(f.relative_to(root)),raw])
   elif not t.exists():missing.append([str(f.relative_to(root)),raw])
 return count,missing,escapes
results=[];bad=[]
with tempfile.TemporaryDirectory(prefix='mas-bundle-verify-') as temp:
 for info in json.loads((O/'DOWNLOADS.json').read_text())['packages']:
  zpath=O/info['file'];assert sha(zpath)==info['sha256'];loc=Path(temp)/info['id'];loc.mkdir()
  with zipfile.ZipFile(zpath) as z:
   assert z.testzip() is None
   assert len(z.namelist())==len(set(z.namelist()))
   assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
   z.extractall(loc)
  p=next(loc.iterdir());m=json.loads((p/'BUNDLE.json').read_text())
  actual={str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}
  assert actual==set(m['files'])|{'BUNDLE.json','SHA256SUMS'},actual^set(m['files'])
  for rel,vals in m['files'].items():assert sha(p/rel)==vals['sha256'] and (p/rel).stat().st_size==vals['bytes'],rel
  for rel,h in m['original_files'].items():assert sha(p/rel)==h,rel
  for row in (p/'SHA256SUMS').read_text().splitlines():h,rel=row.split('  ',1);assert sha(p/rel)==h
  names=[]
  for sid in SMALL:
   f=p/'foundation/skills'/sid/'SKILL.md';s=f.read_text();assert f.exists();names.append(re.search(r'^name:\s*(.+)$',s,re.M).group(1).strip('"\''))
  assert set(names)==set(SMALL) and len(names)==4
  assert (p/'foundation/skills/dispatch-accept-verify/templates/登记行模板.md').is_file()
  assert (p/'foundation/templates/task-register-line.md').is_file()
  assert 'Jesse Vincent' in (p/'foundation/NOTICE').read_text()
  conf=json.loads((p/'config/team.json').read_text());assert len(conf['roles'])==16 and len(conf['groups'])==6
  # Membership field name is discovered rather than guessed.
  keys=conf['groups'][0].keys();member_key=next(k for k in ['members','memberIds','member_ids'] if k in keys)
  assert sum(len(g[member_key]) for g in conf['groups'])==26
  count,missing,esc=link_check(p)
  T=Path(temp)/('materials-'+info['id']);T.mkdir()
  with zipfile.ZipFile(p/'TASK-MATERIALS.zip') as z:
   assert z.testzip() is None;assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(T)
  tm=json.loads((T/'MATERIALS.json').read_text())
  for rel,h in tm['files'].items():assert sha(T/rel)==h
  for sid in SMALL:
   f='foundation/skills/'+sid+'/SKILL.md';assert sha(T/f)==sha(p/f)
  tc,tm,te=link_check(T)
  forbidden=[]
  for f in p.rglob('*'):
   if f.is_file() and f.suffix in ['.md','.txt','.json','.html','.js','.mjs']:
    s=f.read_text(errors='replace')
    if re.search(r'/Users/[^/]+/|/var/folders/|xwechat_files|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|sk-[A-Za-z0-9]{24,}',s):forbidden.append(str(f.relative_to(p)))
  # Fixture markers can contain deliberate invalid paths: record for manual review, never silently approve.
  row={'platform':info['platform'],'zip':info['file'],'archive_files':len(actual),'skill_count':5,'foundation_skill_count':4,'roles':16,'groups':6,'memberships':26,'local_links':count,'missing_links':missing,'escaping_links':esc,'task_material_links':tc,'task_material_missing_links':tm,'task_material_escaping_links':te,'sensitive_scan_hits':forbidden,'original_file_hashes_verified':len(m['original_files']),'sha256':sha(zpath),'scope':'static package verification; no native platform run'}
  results.append(row)
  if missing or esc or tm or te or forbidden:bad.append(row)
report={'packages':results,'passed':not bad,'limitations':['No native platform adoption or five-skill runtime acceptance in this revision.','External URLs and GitHub current remote have not been validated by this script.']}
(ROOT/'review/完整包核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(1 if bad else 0)
