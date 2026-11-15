# 一份团队配置，四个入口

[team.json](team.json) 定义三席共同的交付方式。新用户选择自己使用的平台入口；制作适配器时，按这里的稳定编号对应实际席位。此 JSON 供人和程序读，各平台通过它们自己的文件或原生操作建队。

| 稳定编号 | 谁来做 | 怎样才算接完 |
|---|---|---|
| `lead` | 首席接任务或半成品，处理后续变更，派制作与独审 | 在用户原会话交付能打开的成品，审核版次与文件一致 |
| `producer` | 生产官制作、标记版本，按明确意见修订 | 首席收到实际文件、版次和仍待核实的事项 |
| `reviewer` | 审核官独立读原要求与指定产物，可以退修 | 首席收到点明版本和依据的结论；有改动就复核新版 |

三席组成一个项目交付组。群聊、部门、专家团或项目会话都可以承载协作。共享进度不赋予成员额外权限，最终质量结论由审核席给出。基础配置只有三席，可以按相同分工为自己的组织扩展席位。

## 各入口怎样承载这份配置

| 入口 | 三席如何对应 | 目前有依据的能力 |
|---|---|---|
| Grok Bot | 试用首席、生产官、审核官分别使用自己的 Bot 对话。引导页先预览，再根据账号允许的原生能力建立或使用本次专用空席 | 现役团队已有真实制件、退修、独审和首席回件；普通新账号独立完成建队与首单还有待验证 |
| OpenMausBot | 部门文件以 `lead / producer / reviewer` 为岗位键，`team.leader` 指向首席 | 0.1.148 的原生函数已在隔离存储导入、导出并再次导入。实际三席办单另有手动建队的运行记录。这份部门文件在真实账号中的界面导入待验证。重复导入会产生新部门 |
| WorkBuddy | 专家团主理人为 `solo-to-team-delivery-team-lead`，成员为 `producer` 和 `reviewer`，从专家团入口收件 | 本机私有专家团已完成一次原生三席首单，有独立退修与同版回件。新用户采用还取决于其安装入口和账号用量 |
| DeepSeek Harness | 进入项目，加载 `.dsh/skills/solo-to-team/SKILL.md` 及三份岗位说明。原会话任首席，执行席名为 `production`、审核席名为 `review` | 优先用已启用的队友工具；缺少该能力时只接受能分别委派并接回结果的独立子任务。需按所用入口实测。这里的文件面向 Harness 项目，DS Bot 的常驻建队包单独提供 |

头像可按入口沿用默认、选用包内示意图或在支持的宿主中自行设置。在没有头像槽的项目入口，仍可按三个岗位的实际身份核交接。四个配套 Skill 在清单中按原名列出，三席首单无需先装它们。

**First run in English.** Start in your host’s team lead chat with a new brief or an existing draft. The producer returns a versioned artifact. The independent reviewer opens that version and returns a decision to the lead. If changes are required, the producer revises and the reviewer checks the new version. The lead returns the reviewed file to the original conversation.
