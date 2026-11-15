# 一人成阵 0.3.0 发布候选集成构建

这份增量将已核准的 0.2.2-rc.5 与新的项目工作台入口、16席六群建队台、带底稿开工、三方配置更新和案例文件组合。原稿与原包保留。

先用原维护者源码和公开仓基准生成 0.2.2-rc.5。也可使用已核收的同指纹原 ZIP。输入原包的 SHA-256 必须为 `5e2f86298c08182eb7f2f3500ff767adc4b2a21e59a64a8c5c6993333f5b4d73`。

在拥有 Python 3.9 及以上与已安装 Node.js 的环境中运行以下命令。所选输出路径已有不同内容时，会保留原文件并返回错误。

```sh
python3 build.py /your/path/Solo-to-Team-MAS-0.2.2-rc.5.zip /your/path/Solo-to-Team-MAS-0.3.0-rc.15.zip
```

程序先核原包每份文件，再核增量清单。16席建队台、带底稿页面和配置更新页面分别从随包源码重建，并对照拟装入的页面。旧首页在 `classic.html` 保留，只有许可提示更新为当前范围。旧 core/RIGHTS.md、source/SOURCES.md 在当前产品中明确覆写，并重算 core/checksums.json；冻结底包、原技能和历史构建输入不改。整包的同版文件清单与组件树指纹写入 `checksums.json`。合成陶艺案例保留实际印样，所列项目自制材料采用 MIT，允许商用；范围和例外见产品 NOTICE。

本版仍包含原 WorkBuddy Mac 安装预览器。它的已核二进制和 Objective-C 源码沿用原版。本步骤重新打包这些原件，未重新编译该 Mac 应用。公开候选如选择不含此程序，需要采用已备的相应差分，并重新生成该候选的清单。

## English

This overlay builds the 0.3.0 release candidate from the verified 0.2.2-rc.5 archive. Rebuild that base with the previously supplied maintainer sources first, or supply the already verified archive. Python 3.9+ and an available Node.js runtime are required. The build uses the installed runtimes and their standard libraries.

The builder checks every base file and the overlay manifest. It rebuilds all three current local applications from their supplied JavaScript sources, verifies their bundled HTML, retains the former landing page as `classic.html` with its license notice updated, and writes a complete file manifest. A different existing output is never overwritten.

The listed project-authored materials use MIT, including commercial use, within the product NOTICE scope and exclusions. Only current core/RIGHTS.md and source/SOURCES.md replace their historical counterparts; core/checksums.json is recomputed. Frozen inputs and original skills remain unchanged. This candidate retains the earlier Mac WorkBuddy preview application's reviewed binary and Objective-C source. That binary is repackaged from the earlier audited component. Recompiling it is outside this build. The separately prepared no-application option is a distinct publication choice.

[Source manifest / 增量清单](overlay.lock.json)

