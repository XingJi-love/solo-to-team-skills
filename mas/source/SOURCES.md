# 来源与范围 / Source and rights scope

- **建队器与适配代码。** 项目自制的中性数据结构、编辑界面、岗位流程、Grok 引导、DS 同步与续办逻辑、WorkBuddy 专家团导出和 ZIP 写入。宿主可接受的字段按 0.2.2b 对应的版本核对：OpenMausBot 0.1.148、DeepSeek Harness 0.2.1-rc.5、DS Bot v0.3.2、WorkBuddy 5.9.3。Grok 入口提供引导式建队。源码包不包含这些宿主的程序、官方注册脚本、账户资料或聊天记录。
- **DS Bot 接口依据。** 建席、建群及名册回读的调用字段来自作者固定标签的[工具定义](https://github.com/Fei2411/DS-Bot/blob/v0.3.2/ds-bot/src/host/tools.js)。原生群人数与成员约束可对照[群籍实现](https://github.com/Fei2411/DS-Bot/blob/v0.3.2/ds-bot/src/host/roster.js)和[常量](https://github.com/Fei2411/DS-Bot/blob/v0.3.2/ds-bot/src/host/constants.js)。此包提供项目编写的规划器与指南；DS Bot 的宿主代码留在上游。平台名称用于识别兼容入口。
- **四张几何图标。** 本项目 WorkBuddy 0.1.0 候选的原创图稿，原始 PNG 按字节复用。团队、首席、制作、独审各一张，供用户没有自选图时使用。此处不包含现役团队的私人头像。模板中 `example.org` 邮箱是格式占位符。
- **四个原有 Skill。** 它们继续适用原仓库随附的 MIT 许可证及 NOTICE。本源码包没有复制这四个 Skill。旧许可证的范围不能据此延伸到此处新增的代码、岗位资料、模板文案或图标。新增内容的公开许可仍待权利人决定。

| 原创图标 / Original artwork | PNG SHA-256 |
| --- | --- |
| `team.png` | `9ceb6d41b2ebb6ee57255d2819fd5e346143aec848451eb44b0a630a8c0b581b` |
| `team-lead.png` | `65f639a657e1610acb2c7a21c04257bc6943770fbab654ee7c6033582968e2ec` |
| `production.png` | `f784f80784c394e909751754fa087fb233972f413ea5ef414d2be4fd774dee42` |
| `review.png` | `a6f94f07efc4b7059596e06756d33af45f7fc8db78954c7445334ec2bd0ac42b` |

The builder, adapters, role templates, runbooks and archive writers are project-authored. Platform names identify their target formats. The four fallback PNGs are the project's original geometric icons. Upstream host applications, registration scripts, personal portraits, accounts and conversation records are outside this source package. The four earlier skills retain the MIT license and notice supplied with their own repository; their files are absent here. The owner has not assigned a public license to this new source or artwork.
