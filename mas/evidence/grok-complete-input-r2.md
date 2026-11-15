# Grok 完整输入续测：有限核收

核收日期：2026年11月14日（美东时间）。对象为 design2 / adapter.2 对应技能的独立测试账号样本。这是现有测试 Bot 的完整输入续测，随后增加另一现有 Bot 的独立审阅及三份资料回取；属于人工递交附件的有限协作，不是新的首次采用或自动调度验收。

## 本轮确认的事实

第一轮任务录入被拆成多条并丢字，最后一段要求未发送；该轮样本无效，原件保留。随后把完整任务作为 UTF-8 附件，通过原生附件入口加一条英文短提示发给同一测试 Bot。发送前后截图显示附件与提示；返回的任务文件与本机输入逐字节一致。首份成品已下载、全文核读，未通过追加纠正来改到预期答案。

合成任务要求将18人的初稿调整为12人、B室、17:30—19:00、预算上限1600元。场地480元，茶点每人35元，印刷每人12元，交通补贴300元，机动费用200元。日期仍为12月6日，主持不变，现场协助替补及报名截止未定。

| 核对项 | 结果 |
|---|---|
| 完整附件传递 | 发送前后截图可见；返还输入与源字节一致 |
| 当前人数、时间、场地、日期 | 与完整任务一致 |
| 预算合计和余量 | 1544元，距上限余56元；独立复算一致 |
| 机动费用、未定人选和截止时间 | 名称及待定状态保留 |
| 旧安排与建议 | 不再列旧稿对照；流程建议明确标为建议 |
| 实际执行说明 | 明说单助手起草与自查，没有虚报独立审核 |
| 首份结果 | 另存R2，保留首轮原件 |

输入文件：1720字节，SHA-256：314e270837f12a6ca49ed9fad0f43c09d6a23175341501c45b1a1c1e62c30fc0。

首份成品：4289字节，SHA-256：e89c6b2cc21d07bc6c0d06e2ab37ec789cd1e579230aeb3574eb3d1db9bb63e3。

## 后续两个现有 Bot 的独立审阅

制件 Bot 的原任务与首份成品保持不变，由首席通过原生附件转交给另一现有 Bot。审阅者未收到预期答案或通过结论，仅要求检查事实、预算、约束及证据。独立审阅原件与证据包已下载，10项指纹核同；截图显示另一 Bot 收到两份附件并返回审阅文件。

审阅结论为“通过”，附3条非阻断意见：资料根由谁提供未在成品中交代；12人是否包含工作人员未由任务说明；主持承担开场属于已标注的流程建议。意见保留，未为取得通过而改写成品或重跑审阅。审阅者有先前上下文，本项不是盲测。

审阅原件：5144字节，SHA-256：62712fe20e921e4d1d606b7f6eda9f14c643557ea1b17ea19aa46a14dab0a71b。

本项确认“制件 Bot—首席人工递交—另一 Bot 独立审阅—原件回收”的有限链路。R2成品中“单助手起草与自查”的说明对应制件当时状态，后续独审作为独立记录补充，不倒改原件。

## 制件上下文的三份资料回取

随后只向原制件 Bot 请求从已有任务资料根交回三个原文件，不提供文件正文或预期指纹。截图显示该上下文收到一条英文取回请求并返回ZIP；实际ZIP仅含指定3件，完整性通过，全部与本机当前候选逐字节一致。

| 返回文件 | 字节数 | SHA-256 |
|---|---:|---|
| manifest.json | 1355 | fce017e9a02c35941408977e34133efc0f3ad625e8154b45e24babb4eb88fe5e |
| references/role-routing.md | 9099 | 0e6875f8189371aacc941fabf10c932f7081fb9bfb4bc4424629fedbe72b0462 |
| references/groups.zh.md | 20456 | 3f5c10e3d1edc6d71596557cf7ee326b7aa8572396f01b2c42ea890820cf9ce5 |

三文件ZIP：12643字节，SHA-256：326f88f39ed57f8af4ff50809c4025f794e4f2121932425c0125105658b98d4b。

本项确认该制件上下文实际交回了正确的三份材料；不能据此倒推它在先前制件时读了哪些内容，也不能证明内部使用了哪个加载工具。

## 没有被证明的部分

Skill加载和先前任务执行时的具体读取过程仍只有 Bot 自述；Activity 截图未显示相应原始调用记录。正文保存完整性另有此前的字节核对依据，三份资料的实际回取另有本次实件依据，两者都不冒称原始Skill调用独证。

本轮不证明干净上下文首次采用、所有 Bot 自动加载、同 Bot 新会话接续、自动派单、四平台16席全部业务或长期稳定性。已经确认的是完整附件传递、本题有限输出、两个现有 Bot 的人工接力独立审阅及三份材料回取。

## 使用时可复用的方法

长任务可以整理成 UTF-8 文本附件，附一条简短说明，发送前后核对文件名和消息内容。需要精确复核时保留输入原件、输出原件和文件指纹。该方法已在本轮独立测试账号走通，不代表所有平台和文件类型都支持。

不在公共副本中放入原始聊天截图、账号信息或授权原话。本说明只补充证据，不修改已核同的274件使用包、83件维护源码或技能载荷。

## English scope note

This bounded continuation test used a complete UTF-8 task attachment in an existing isolated test Bot. The returned input matched the source bytes; before/after screenshots showed the attachment and one short prompt. The first downloaded output correctly applied the changed attendance, venue, time and budget, retained unresolved decisions, and identified its work as a single assistant's draft and self-check.

A second existing Bot subsequently received the unchanged task and output through manual native-attachment relay and returned an independent review: pass with three non-blocking observations. The original review and ten declared evidence hashes were verified. This was a separate-context review, not a blind test or automatic delegation.

The original maker context also returned exactly three requested reference files. Their bytes matched the current candidate without supplying expected contents or hashes to that Bot. This establishes bounded material availability, not which files were read during the earlier task or which internal tools were invoked.

The earlier first-adoption attempt was invalidated by corrupted UI input and is retained separately. Raw Skill invocation records remain unavailable. These results do not establish fresh-context adoption, automatic loading or orchestration, all-platform/all-seat coverage or long-term reliability. Existing release archives and Skill payloads are unchanged.
