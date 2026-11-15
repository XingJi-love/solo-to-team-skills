# 当前源码与重建 / Current source and rebuilding

本包内的当前组件源码：

- [16席建队器](team-16/README.md)：`team-16/source/`，含中英16席预置、6群、全文群规和四端导出。
- [带底稿开工](start-with-files/source/README.md)：`start-with-files/source/`，与16席建队器共用预置和导出适配器。
- [配置更新](update-team/source/README.md)：`update-team/source/`。三个当前入口共用16席组件中的正文校验模块，重建时保留相邻组件目录；历史校验器只供对照。

从解压后的 `Solo-to-Team` 目录运行下面的命令，将新构建写到另一个文件，不覆盖现有页面，并保留组件目录中的相对链接。需要已安装的 Node.js；检查依各组件说明。

```sh
node team-16/source/build.mjs team-16/index-rebuilt.html
node start-with-files/source/build.mjs start-with-files/index-rebuilt.html
node update-team/source/build.mjs update-team/index-rebuilt.html
```

`source/` 和 `builder/` 保存历史0.2.2b版本，`core/` 保存原首单包；其中当前产品的 core/RIGHTS.md、source/SOURCES.md 及 core/checksums.json 已随本次 MIT 范围更新；冻结输入仍留在维护者原仓，其他历史源码不变。这些历史源码不能单独重建当前完整发行ZIP。**完整发行重建使用维护者原仓的 `python3 mas/release/build-current.py`**，原仓 `mas/release/CURRENT.md` 说明冻结基底、叠加目录与同版指纹。此下载包含组件源码，不包含原仓全部发行构建材料。

## English

The links above identify the current component sources. The 16-role builder and file-intake page share the preset and export adapters. All three current pages share the body-preserving validator in the team-16 component; retain sibling source directories when rebuilding. Historical validator copies are kept for comparison. Run the commands from the extracted `Solo-to-Team` directory with an existing Node.js runtime; each writes a separate output rather than replacing the supplied page.

The top-level `source/` and `builder/` retain historical 0.2.2b, and `core/` retains the original starter. The current product updates core/RIGHTS.md, source/SOURCES.md and core/checksums.json for the approved MIT scope; frozen inputs remain in the maintainer checkout and other historical source bytes are unchanged. These historical sources do not rebuild the current complete ZIP. Full release reconstruction uses `python3 mas/release/build-current.py` from the maintainer checkout; its `mas/release/CURRENT.md` describes the frozen base, overlay and locked fingerprints. This product download includes component sources, not every release-building file from that checkout.
