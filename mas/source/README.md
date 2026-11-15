# Solo to Team · 0.2.2b builder source

## 中文

这份源码可以离线重建送审的四端统一建队台。用户编辑一次团队定义，即可导出 OpenMausBot 部门、DeepSeek Harness 项目、WorkBuddy 专家团或 Grok 引导包。已有 DS Bot v0.3.2 的用户还可在 DeepSeek 项下生成分步建队计划。

在本目录使用已安装的 Node.js 运行以下命令。已在 Node.js 24.21.0 验证。仅使用标准库，无需下载依赖。

```sh
node build.mjs
node smoke.mjs
```

第一条生成 `team-builder.html`。双击即可打开；页面不发起网络请求。不同内容的同名文件会被保留，可另给输出名。第二条在内存中把同一份虚构的四席两群配置传给真实适配模块，读取两种 ZIP 和部门 JSON，并检查两个建队计划及几项边界。它无需账户和模型。

用 `node build.mjs --check` 核对送审版。此版单文件 SHA-256 为 `d14587873861e81318e9a726b04b581efbc9c58795c8e9bad675ea0ceba7dfc3`。修改源码会产生新的散列；另存为 `node build.mjs my-builder.html` 即可试用自己的版本。

| 从哪儿看 | 负责什么 |
| --- | --- |
| [中性定义](web/core.js) · [示例](fixtures/team.json) | 稳定岗位 ID、成员、头像、派工/制作/独审/交还，以及工作语言和收件边界。 |
| [OpenMaus 与 DSH](web/adapters.js) · [可选原生群](web/rooms.js) | OpenMaus 部门 JSON、原生群选项、DSH 根工作区 ZIP。 |
| [WorkBuddy](web/workbuddy.js) · [Grok](web/grok-plan.js) | 生成专家团或引导计划。[宿主下载](web/hosts.js)包含 Grok 的双语指南和实际 ZIP 封装。 |
| [DS Bot 计划](web/ds-planner.js) · [Main Bot 指南](web/ds-runbook.js) · [选项面板](web/ds-panel.js) | 选择岗位和群、核管理员、处理重名、保留续办表。实际建队须由现有 Main Bot 执行。 |
| [页面](web/index.html) · [界面逻辑](web/app.js) · [样式](web/builder.css) | 同一份团队定义的编辑、导出、双语切换、文件校验。 |
| [ZIP 写入](web/zip-store.js) · [图标](assets/icons/) · [WorkBuddy 模板数据](assets/workbuddy.json) | 图标以独立 PNG 提供。构建时生成 `template.js` 并嵌入页面。 |

优先修改相应模块，再构建并运行冒烟。各宿主的真实权限、导入、模型行为和第一单交付需要在对应宿主另行验证。源码与素材的来源、旧四个 Skill 的 MIT 范围见[来源说明](SOURCES.md)。

## English

The editable team definition feeds native OpenMausBot, DeepSeek Harness and WorkBuddy formats plus a guided Grok package. Under DeepSeek, a user who already has DS Bot v0.3.2 can instead prepare a scoped setup plan for their existing Main Bot.

Run `node build.mjs` in this directory and open the resulting `team-builder.html`. The build uses Node standard libraries and works offline. The page makes no network requests. A different existing output is preserved; pass a new filename for a local variant. `node build.mjs --check` verifies a byte-for-byte match with the submitted HTML. The commands were tested with Node.js 24.21.0.

Run `node smoke.mjs` for a small, credential-free check. It feeds [one fictional team](fixtures/team.json) through the shipped functions, reads the OpenMaus department, reads actual DSH and WorkBuddy ZIP entries, examines the Grok and DS Bot plans and checks a conflicting name, invalid group responder and split-return limitations. No browser, host, model or business task is launched by this smoke.

Edit the individual `web/` modules listed above. `web/index.html` is the build template and `web/template.js.in` receives the local artwork at build time. Use the generated page for interactive development. Host installation, account permissions and real task execution have separate acceptance criteria. See [source and rights scope](SOURCES.md).
