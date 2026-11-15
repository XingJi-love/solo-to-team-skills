from pathlib import Path
import json,zipfile,hashlib,shutil,re,csv,io,argparse,html,tempfile
HERE=Path(__file__).resolve().parent
args=argparse.ArgumentParser();args.add_argument('--input',type=Path,default=HERE/'inputs.zip');args.add_argument('--out',type=Path,default=HERE.parent/'packages');a=args.parse_args()
_temporary=tempfile.TemporaryDirectory(prefix='mas-bundle-input-')
I=Path(_temporary.name)
if True:
 with zipfile.ZipFile(a.input) as z:
  for n in z.namelist():
   assert not n.startswith('/') and '..' not in Path(n).parts,n
  z.extractall(I)
O=a.out;O.mkdir(parents=True,exist_ok=True)
INFOS=[('grok','Grok Bot','solo-to-team-grok','design2-doc1 / adapter.5','原生保存正文；参考作为本单任务资料','platform/solo-to-team-grok/solo-to-team-grok_design-2-doc-1_仅上传.zip'),('workbuddy','WorkBuddy','solo-to-team-workbuddy','0.1.0-rc.5','原生上传单技能ZIP；实际核用户级作用范围','platform/solo-to-team-workbuddy.zip'),('deepseek','DeepSeek Harness','solo-to-team-deepseek','0.1.0-rc.5','在本次真实项目根采用项目技能目录','platform/solo-to-team-deepseek-project.zip'),('openmaus','Open Master Bot','solo-to-team-openmaus','0.1.0-rc.5-om.4','目标Bot原生学习保存主文及三份参考','platform/solo-to-team-openmaus-0.1.0-rc.5-om.4-candidate.zip')]
SMALL=[('dispatch-accept-verify','派出去的活要收回来','派单、接单、接回、跟进与状态登记'),('evidence-before-done','交活前要有证据','核对实际成果、同版证据与接受依据'),('beginner-ops-writing','新手操作说明','需要用户亲手操作时，一步一个可见结果'),('ops-case-notes','脱敏运营记录','遇到交接问题时，查已有案例与方法边界')]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def cp(src,dst):
 if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
 else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def zip_dir(src,dest,include_root=True):
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for f in sorted(src.rglob('*')):
   if not f.is_file():continue
   n=str(f.relative_to(src));n=src.name+'/'+n if include_root else n
   zi=zipfile.ZipInfo(n,(2026,11,14,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16
   z.writestr(zi,f.read_bytes())
allrecords=[]
for pid,name,skill,ver,mode,native in INFOS:
 P=O/('Solo-to-Team-'+pid+'-bundle1');P.mkdir(exist_ok=True)
 cp(I/'skills-add-on'/pid,P/'platform')
 # Preserve native payloads; adapt only the outer user guide's relative navigation.
 guide=(P/'platform/开始使用.md').read_text().replace('../../team-16/','../tools/team-16/').replace('../当前版本与入口.md','../docs/历史平台证据.md')
 write(P/'platform/开始使用.md','> 本页记录 adapter.5 平台载荷的采用与更新；新完整包总入口见 [START-HERE](../START-HERE.md)。本文旧平台名称和历史实测范围保留，不能代证 bundle.1 新包全流程。\n\n'+guide)
 F=P/'foundation'
 for rel in ['skills','templates','examples','LICENSE','NOTICE']:cp(I/'core/skills-original'/rel,F/rel)
 foundation_intro='''# 四款基础 Skills · 完整随包资料

四款正文、登记模板、示例、LICENSE与NOTICE均在本包，不需要另找下载。它们作为本单可读取的完整技能材料，按任务使用；没有被偷偷注册成四个新的原生技能对象。保存文件、可读取、原生安装、实际任务运行分别核对。

| 标识 | 中文名称 | 什么时候用 |
|---|---|---|
'''+''.join(f'| [{s}](skills/{s}/SKILL.md) | {cn} | {use} |\n' for s,cn,use in SMALL)+'''
## 各宿主怎么装、怎么叫

本完整包只为所选平台提供一条主路径：[从这里开始](../START-HERE.md)。先按本包平台指南采用大Skill，再提供这份基础材料目录或TASK-MATERIALS.zip。开工读取指引按任务点名相应正文，不要求用户分别保存四次，不把资料阅读叫作四个原生Skill已安装。实际读取须核对；新会话或子执行者不能推定继承。

若用户明确想将四款逐一注册为原生技能，那是另外一种采用方式，须逐项核当前宿主契约、同名对象、保存范围、模板与许可，不沿用其他平台的路径，也不自动覆盖已有对象。本轮没有验证这种五对象注册方式。

## 谁决定派给谁

基础Skill提供方法，不扩展派工、审核、验收、发布权限。当前大Skill、适用岗位卡和用户有效决定确定委托方、接收者与工作范围。群规要求明确接单时不能用模糊开工迹象代替；只有有权者接受或有效取消才关闭，核验通过不自动等于已验收。独审必须是非制作者实际核同版成果。

## 模板与练习

- [根登记模板](templates/task-register-line.md)与派收技能内的模板均随包，路径各自适配。
- [会议纪要跟做示例](examples/walkthrough-meeting-notes/README.md)：先看输入，再看合格与缺件输出；这是教学样例，不是本版实测成绩。
- [脱敏经验](skills/ops-case-notes/SKILL.md)供查漏，不能把案例里的组织和权限当成自己已经拥有。

## 版本与许可

四款正文和原模板沿用 adapter.5 基线中的核心规则v2，逐字保留；旧插件元数据0.0.2-named不作为本包原生安装版本。历史八宿主记录不证明当前组合已在四端重新运行。LICENSE和NOTICE含原署名及第三方MIT声明，本完整包也保留其副本。

'''
 write(F/'README.md',foundation_intro)
 write(F/'README.en.md','# Foundation skills\n\nAll four complete skill directories, templates, examples and license notices are included. Use the [current bundle entry](../START-HERE.md). These are task-readable materials, not four automatically registered native skills. [Chinese instructions](README.md). Historical host evidence does not validate this bundle.\n')
 cp(I/'team-16',P/'tools/team-16');cp(I/'resume',P/'tools/resume');cp(I/'NOTICE',P/'tools/NOTICE')
 cp(I/'team-16/source/presets/team.zh.json',P/'config/team.json')
 cp(I/'skills-add-on/grok/solo-to-team-grok/task-materials/references/roles.zh.md',P/'config/roles.md')
 cp(I/'skills-add-on/grok/solo-to-team-grok/task-materials/references/groups.zh.md',P/'config/groups.md')
 cp(I/'skills-add-on/grok/solo-to-team-grok/task-materials/references/role-routing.md',P/'config/role-routing.md')
 cp(I/'LICENSE',P/'LICENSE');cp(I/'NOTICE',P/'NOTICE')
 cp(I/'skills-add-on/当前版本与入口.md',P/'docs/历史平台证据.md')
 # Historical cross-platform file links are stripped into plain references: this bundle ships one platform only.
 hp=P/'docs/历史平台证据.md';s=hp.read_text();s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:m.group(1)+'（历史路径：`'+m.group(2)+'`）',s)
 write(hp,'# 历史证据摘录（adapter.5）\n\n下文是原基线的四平台证据边界，不是bundle.1的安装结果。跨平台路径保留为历史定位文字；当前操作只用本包START-HERE。\n\n'+s)
 mapped='\n本包对外名为 **Open Master Bot**；现有文件、调用名及历史宿主记录仍使用 `openmaus` / OpenMausBot。保留这些兼容标识，不另指向其他软件，也不以改显示名冒充另一个平台适配。\n' if pid=='openmaus' else ''
 main=f'''# 一人成队 · {name} 完整包

**先解压这个完整包，再按下面步骤开始。** 包装版本 `bundle.1`；内含平台协作Skill `{skill}`（基线版本 `{ver}`）与四款完整基础Skills。四基础Skill是必带组件，按任务读取，不要求每单全部运行，不要求另找四次下载。
{mapped}
## 只走这条入口

1. **采用平台Skill。** 查看 [本平台采用说明](platform/开始使用.md)，使用 [{Path(native).name}]({native})。这个外层完整ZIP不是原生单技能上传ZIP。先核同名与作用范围，已有同版可用就复用，不为采用新包改动现役团队。
2. **提供配套资料。** 将 [TASK-MATERIALS.zip](TASK-MATERIALS.zip)作为本单普通任务附件提供，或允许助手读取解压 TASK-MATERIALS.zip 后的本单资料根，包括 `开工读取指引.md`、`foundation/` 与 `config/`。不要把它填进技能安装框。若宿主不能打开ZIP，就提供解压后的实际目录；不知道资料是否可读时先核，不假装已加载。{('DeepSeek项目中让主会话读取本次实际资料根；子会话分别核目录与访问范围。' if pid=='deepseek' else '')}
3. **给出开工要求。** 使用下面 [可复制的开工文本](开工文本.txt)。助手先核实际平台Skill与配套材料，按任务读取基础Skills，再接你的目标。材料已提供且可核时不重复索取，不凭这句话新建16席或改权限。
4. **先收一份小成果。** 按 [首次使用检查](docs/首次使用检查.md)核对实际读取、执行者、同版审核和交回。先用合成材料，不以安装回执替代完成。

[包内配置与使用清单](docs/配置使用清单.md) · [更新与退出](docs/采用与退出.md) · [四基础Skills](foundation/README.md) · [已验与未验](docs/验证范围.md)

## 两个按需工具

- [16席六群建队台](tools/team-16/index.html)：有需要再改岗位、群与交接。保存配置不会自动建队；已有团队先沿用，不用每次重建。
- [接续工具](tools/resume/从这里续办.html)：长任务中断或换会话时整理断点，不是后台唤醒程序。

## 采用范围

平台路径：{mode}。模型服务、账号、真实执行者和权限由平台提供，本包不含额度、账号或通用跨平台运行器。岗位、群与基础规则不能授予新权限。

本轮完整包已做的仅是本机装配与文件检查；逐项结果见验证报告。原平台载荷保持原字节，旧业务与原生保存证据仅按原版本范围保留。未把bundle.1标为四端完整实测通过，未正式发布。
'''
 write(P/'START-HERE.md',main)
 # One short task handoff reaches complete source materials; no required separate native registration.
 launch=f'''请使用 {skill} 处理我接下来提供的目标。先核当前采用的是哪个版本、有哪些真实执行者和已有授权，不新建团队或改权限。
请打开我已提供的 TASK-MATERIALS.zip，或读取我明确给出的实际资料目录。先读 开工读取指引.md 和 foundation/README.md，确认四款基础Skills正文、派收模板及本单岗位资料实际可读。按本单需要读取对应完整正文，不把目录存在或列出名字说成已加载。
派收用 dispatch-accept-verify，核验用 evidence-before-done；需要我亲手操作时用 beginner-ops-writing，遇到流程问题时参考 ops-case-notes。先核大Skill与现行岗位卡确定的职责和接收者，基础方法不扩大权限。无关步骤不强加。
各实际制作/审核者分别取得所需材料。收到路径、取得文件、原生安装、真实协作和我能打开成果分别确认。已提供且能核的资料不再索要；暂不可读就说缺哪一份，不假装完成。先回复材料核对与本单安排，再继续已授权的工作。
'''
 write(P/'开工文本.txt',launch)
 material_guide='''# 开工读取指引

这份附件只提供任务资料，不执行安装、不扩大权限。先按本单有效决定与平台大Skill确定任务范围，再打开 foundation/README.md；该文件链接四基础Skills全文和模板。按任务选读不能变成只列名称不读正文。

- 派发、接回或追踪工作：读 foundation/skills/dispatch-accept-verify/SKILL.md 与 templates/登记行模板.md（在该技能目录下）。
- 宣称完成或接受回件：读 foundation/skills/evidence-before-done/SKILL.md；实际核同版成果，有权接受才关闭。
- 给不熟悉电脑的人写操作：读 foundation/skills/beginner-ops-writing/SKILL.md。
- 排查交接失误与复用经验：读 foundation/skills/ops-case-notes/SKILL.md。
- 启用岗位：读 config/roles.md 的对应岗位与 config/role-routing.md；采用群时读 config/groups.md 的通则和对应节。现役有效决定优先，不用模板覆盖团队。

包内资料按已获授权范围提供给相关执行者；新会话、子会话和另一个Bot不自动继承。记录实际读到的材料版本和本单使用的规则，不能虚构工具调用、独立审核或收件证据。
'''
 write(P/'开工读取指引.md',material_guide)
 conf=[('平台协作Skill','必要',f'platform/solo-to-team-{pid}/'+('body.md' if pid=='grok' else 'SKILL.md'),'组织本平台接单、派收、审核、交回','按平台指南采用；读回实际版本'),('四基础Skills','必要随包，按任务读取','foundation/skills/','派收、证据、新手步骤与经验复用','四目录与正文可读；派收模板齐全'),('16席岗位卡','启用对应席时必要','config/roles.md','明确岗位职责与交件边界','实际执行者回读自己职责；不默认16席全开'),('角色路由','跨席协作时必要','config/role-routing.md','委托、审核、退修和私人收件对象','核委托方与真实接收者，不因群关系扩大权限'),('六群规则','使用群时必要','config/groups.md','通则、成员背景与群内交流','读取通则和所用群；文件存在不等于已建群'),('团队配置底稿','编辑团队时用','config/team.json','16席、6群、26成员关系建议数据','是建队台底稿，不是四平台通用原生导入文件'),('离线建队台','需要建队或改配置时用','tools/team-16/index.html','编辑、保存、按平台导出','保存后重开核内容；原生导入另核'),('任务登记模板','多步骤派收时用','foundation/templates/task-register-line.md','分开记录阶段、跟进事件与接受依据','收到不等于验收；两份模板路径均齐'),('接续工具','中断或换会话时用','tools/resume/从这里续办.html','整理目标、版本、证据与下一步','新会话实际读到断点；不承诺自动唤醒'),('合成跟做示例','首次练习可用','foundation/examples/walkthrough-meeting-notes/README.md','以小任务练交件和退修','教学材料，不能充当真实验收回件'),('安装更新与退出','采用或更换版本时必要','docs/采用与退出.md','同名核对、备份、更新与撤回范围','按实际宿主结果，不删除整个技能库'),('完整任务资料附件','助手读资料时用','TASK-MATERIALS.zip','一次提供四基础Skills和配置资料','普通任务附件，不是原生单技能安装包'),('版本与指纹','维护或排错时用','BUNDLE.json','把平台版本、原件和新增包装分开','自查清单与实际文件；不当作运行成绩'),('许可与来源','复制分发时保留','NOTICE','项目MIT和第三方署名条款','保留根与foundation的LICENSE/NOTICE')]
 rows='| 配置 | 是否需要 | 在哪里 | 做什么 | 怎样确认 |\n|---|---|---|---|---|\n'+''.join(f'| {x[0]} | {x[1]} | [{x[2]}](../{x[2]}) | {x[3]} | {x[4]} |\n' for x in conf)
 write(P/'docs/配置使用清单.md',f'# {name} · 包内配置与使用清单\n\n包装 `bundle.1`，平台载荷 `{ver}`。这是本版本的操作清单；PDF只作概览。新用户从 [START-HERE](../START-HERE.md) 开始，不必按目录逐个安装。\n\n'+rows+'''\n## 平台里还需要什么

已有可正常使用的平台与模型服务；本单允许的工作目录与材料；确实可用的执行者及审核者；与任务对应的权限和收件渠道。这些不是下载包能替你开通的。简单单人任务不硬建团队，缺第二真实执行者不能称独审。

## 五款技能名称

'''+f'- 平台主技能：`{skill}`。\n'+''.join(f'- `{s}`：{cn}，{use}。\n' for s,cn,use in SMALL)+mapped)
 out=io.StringIO();cw=csv.writer(out);cw.writerow(['配置','是否需要','路径','用途','确认方式']);cw.writerows(conf);write(P/'docs/配置使用清单.csv',out.getvalue())
 exitguide=f'''# {name} · 采用、更新与退出

[返回总入口](../START-HERE.md) · [平台原生步骤](../platform/开始使用.md)

## 先分清两种对象

- 平台主Skill `{skill}`：按平台原生机制保存或项目目录采用，遵循平台指南的同名、作用范围和版本核对。
- 四基础Skills与config：本包选定路径是本单可读取的普通资料，不自动创建四个原生技能对象。资料已提供不能记为四个Skill已原生安装。如果你之前已另装同名基础Skills，先核版本和来源，不让两份不同规则无声混用；沿用本单明确选定版本，不擅自覆盖旧技能。

## 更新

1. 只更新本次选择的平台对象和资料副本。保留原件、当前版及未完任务，不覆盖整个技能库或现役岗位配置。
2. 平台主Skill的更新沿 [平台说明](../platform/开始使用.md)，同版已核可用直接复用；不因收到新完整包而强制重装。
3. 四基础材料更新时将新完整包解到独立新目录，核BUNDLE版本、四个正文、派收模板及许可。新任务指向新版实际资料根；旧任务保留其实际使用版本，不把旧证据归到新包。
4. 用同一份小任务核实际采用和结果，再扩到真实材料。未核的节点写未验。

## 停用或撤回

平台主Skill只用当前宿主实际支持且范围明确的停用/恢复入口，详见平台说明；不能保证统一一键撤销。基础材料可停止向后续任务提供或指向旧副本，但这不删除对话已读内容，也不保证云端附件或记忆已清除。宿主删除/保留能力要另核，不擅自删除资料。若另外注册了四个原生基础Skill，逐对象确认真实ID、范围与恢复方式，不能把移出普通资料当成已卸载。

撤回技能或资料不撤回已经产生的业务动作，原成果、失败与未完项保留；恢复原团队权限或账号不在这份包的自动操作范围内。
'''
 write(P/'docs/采用与退出.md',exitguide)
 write(P/'docs/首次使用检查.md',f'''# 首次使用检查

按 [总入口](../START-HERE.md) 采用。以下是用户可选的小任务自检，不是已经完成的成绩。

1. 提供 [合成会议输入](../foundation/examples/walkthrough-meeting-notes/input.md)，请先确认实际读到的版本与需要保留的信息。
2. 让实际制作席生成纪要文件；另一真实执行上下文打开同版文件，指出遗漏；无此条件如实记单人工作，不扮演多人。
3. 如需退修，首席交回原执行席，只改受影响部分。完成后在原收件位置交可打开成果及审核记录。
4. 对照 [教学参考](../foundation/examples/walkthrough-meeting-notes/README.md)，独立核实是否保留输入事实，不以预先给出的参考答案充当实测。

| 节点 | 自己填写事实 | 不可替代的条件 |
|---|---|---|
| 平台主Skill | 未验 / 已采用，实际版本与依据 | 读源文件不是已安装读回 |
| 基础资料 | 实际读到哪些正文和模板 | 存在不是读到，读到不是已原生注册 |
| 执行与独审 | 实际对象、上下文及证据 | 角色名不是独立执行者 |
| 回件 | 实际附件/文件及所在入口 | 路径或发送回执不是用户能打开 |
| 接受 | 谁接受、按哪项决定或授权 | 核验通过不自动有验收权 |
| 接续（需要时） | 新会话实际读到版本和未完项 | 新子上下文不等于全新客户端聊天 |

不要预填成功，不要求每件简单任务都做全表。问题反馈只提供平台/版本/操作/预期/实际结果及脱敏必要证据，不贴账号、密钥、私人聊天或个人行程。
''')
 write(P/'docs/验证范围.md',f'''# bundle.1 的验证范围

本完整包版本与原平台版本分开：包装bundle.1；主Skill `{skill}` / `{ver}`；基础Skills来自adapter.5的核心规则v2。当前基础组合不按旧插件0.0.2-named推定原生支持。

本轮检查解包完整性、文件指纹、相对路径、配置计数、四基础正文与模板原字节、原平台载荷原字节、许可、文档和PDF一致性以及可重建性。详细本机结果随整体交付报告提供；检查脚本成功不能证明平台实际运行。

未做bundle.1新用户从下载到完整任务的原生实测；未向现役团队安装；未重跑全16席、六群、多设备或长期稳定性；未保证所有成员自动发现和加载材料。既有平台有限证据见 [历史平台证据](历史平台证据.md)，历史版本不能冒充本包已采用通过。

在最终发布前，仍需核对GitHub实际远端差异、最终版本与下载附件、发布后下载路径和指纹，并明确保留上述未测范围。不能在未补验时宣传“四端完整正式验收通过”。
''')
 # Browser-readable portal, explicit links; no JS or upload code.
 links=[('本平台开始使用','platform/开始使用.md'),('配置使用清单','docs/配置使用清单.md'),('四基础Skills','foundation/README.md'),('开工文本','开工文本.txt'),('任务资料附件','TASK-MATERIALS.zip'),('16席六群建队台','tools/team-16/index.html'),('接续工具','tools/resume/从这里续办.html'),('采用、更新与退出','docs/采用与退出.md')]
 page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>一人成队 · {name}</title><style>body{{font:18px/1.7 system-ui,sans-serif;color:#15343d;background:#f5f7f8;max-width:920px;margin:40px auto;padding:0 24px}}h1{{font-size:40px;line-height:1.2}}a{{color:#086b68}}nav{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}}nav a{{display:block;padding:18px;background:white;border:1px solid #bbcaca;border-radius:10px;text-decoration:none}}.tag{{color:#526773}}.notice{{border-left:4px solid #167f77;padding:12px 18px;background:#eaf3ef}}</style><p class="tag">SOLO TO TEAM / bundle.1 / 本机候选</p><h1>一人成队 · {name} 完整包</h1><p>一款平台协作Skill，四款完整基础Skills，配套配置、模板与使用说明。</p><p class="notice">先读 <a href="START-HERE.md">从这里开始</a>：采用平台Skill → 提供任务资料 → 发出目标 → 核对实际成果。外层完整包不直接当作原生单技能上传包。</p><nav>'''+''.join(f'<a href="{html.escape(url)}">{title}</a>' for title,url in links)+'''</nav><p>四基础Skills全部随包；按任务读取，不等于已自动安装或加载。平台账号、模型、真实执行者与权限需具备。没有统一一键建队承诺。</p><p><a href="docs/验证范围.md">查看验证范围</a> · <a href="LICENSE">MIT许可</a> · <a href="NOTICE">来源与例外</a></p></html>'''
 write(P/'START-HERE.html',page)
 # Pack task materials as a separate ordinary attachment with complete relative paths.
 T=O/('_task_'+pid);T.mkdir(exist_ok=True)
 for rel in ['foundation','config','开工读取指引.md','LICENSE','NOTICE']:cp(P/rel,T/rel)
 write(T/'START-HERE.md','# 本单任务资料\n\n先读 [开工读取指引](开工读取指引.md)，再按任务读 [基础Skills](foundation/README.md)。本附件不执行安装。采用平台Skill的步骤在完整下载包的START-HERE.md；本附件仅提供本单获准的资料。版本与文件清单见 MATERIALS.json。\n')
 write(T/'MATERIALS.json',json.dumps({'bundle_version':'bundle.1','platform':name,'primary_skill':skill,'files':{str(f.relative_to(T)):sha(f) for f in sorted(T.rglob('*')) if f.is_file() and f.name!='MATERIALS.json'}},ensure_ascii=False,indent=2)+'\n')
 zip_dir(T,P/'TASK-MATERIALS.zip',False);shutil.rmtree(T)
 original_files={}
 for f in (I/'core/skills-original/skills').rglob('*'):
  if f.is_file():original_files['foundation/skills/'+str(f.relative_to(I/'core/skills-original/skills'))]=sha(f)
 for f in (I/'skills-add-on'/pid).rglob('*'):
  if f.is_file() and f.name!='开始使用.md':original_files['platform/'+str(f.relative_to(I/'skills-add-on'/pid))]=sha(f)
 allf={str(f.relative_to(P)):{'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(P.rglob('*')) if f.is_file() and f not in [P/'BUNDLE.json',P/'SHA256SUMS']}
 manifest={'bundle_version':'bundle.1','platform':name,'compatibility_id':pid,'primary_skill':skill,'primary_version':ver,'foundation_skills':[x[0] for x in SMALL],'foundation_mode':'complete directories and resources, read as task materials; not automatically native-installed','scope':'local candidate; no runtime acceptance claimed','baseline':'adapter.5 / core rules v2','original_files':original_files,'files':allf,'manifest_self_excluded':True}
 write(P/'BUNDLE.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 hashes={**{rel:v['sha256'] for rel,v in allf.items()},'BUNDLE.json':sha(P/'BUNDLE.json')}
 write(P/'SHA256SUMS',''.join(f'{h}  {rel}\n' for rel,h in sorted(hashes.items())))
 zp=O/(P.name+'.zip');zip_dir(P,zp)
 allrecords.append({'platform':name,'id':pid,'file':zp.name,'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(allf)+2,'skill':skill})
write(O/'DOWNLOADS.json',json.dumps({'bundle_version':'bundle.1','packages':allrecords},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(allrecords,ensure_ascii=False,indent=2))
