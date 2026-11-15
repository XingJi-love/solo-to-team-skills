# 历史rc15源码快照与当前维护入口

本目录保留的是原rc15底座源码，不是当前四平台组合的重建入口。下方原文保留其历史范围；其中“当前”指该快照形成时的版本。

本版请取[完整维护源码](../releases/rc15-skills-rc5-grok-design2-doc1-adapter5/MAS-rc15-three-rc5-grok-design2-doc1-adapter5-maintainer-source.zip)，解压后按`mas-combined-source/开始重建.md`操作。它包含所需历史源码依赖，并已空目录重建出当前完整包。

旧`build-current.py`会核原rc15展示链接；本仓现在的顶部入口已切到新版组合，因此不应直接用旧命令重建当前版，也不要删除它的保护检查或用新包指纹替换旧锁。需要研究历史源码时，使用上述维护源码中完整的历史输入快照。

**Historical source snapshot.** The original commands below describe the old rc15 base, not the current four-platform combination. Download the [current complete maintainer source](../releases/rc15-skills-rc5-grok-design2-doc1-adapter5/MAS-rc15-three-rc5-grok-design2-doc1-adapter5-maintainer-source.zip), extract it and follow `mas-combined-source/开始重建.md`. The old builder checks the historical rc15 page links and is expected to refuse the updated navigation in this checkout. Keep its guards and locked fingerprints unchanged; use the complete historical inputs bundled with the current maintainer source for historical research.

---

# Current checkout downloads / 当前原仓下载

From the repository root, run this command with an existing Python 3.9+ and Node.js runtime:

```sh
python3 mas/release/build-current.py
```

在原仓目录运行同一条命令。它只使用当前 checkout 里的公开基准、可读源码、模板和已核素材，不读取任何现成 release ZIP。流程先按原 RC5 配方重建统一编队页和临时底包，再从 `current/` 源码重建16席建队台、带底稿及更新器三页，最后输出 README 引用的两份文件：

- `mas/downloads/Solo-to-Team-MAS-0.3.0-rc.15.zip`，SHA-256 `3897384d1874efbd48d8780e4bd0b69caad203337e6399a789f86f597878cb55`
- `mas/downloads/quick-review.zip`，SHA-256 `192fcdb700265600ff48c0c345a4ab19598a24703cbcbd0212d5d4346785e0dd`

已存在的同字节文件会复用；不同内容的同名文件、软链接会拒绝。两份先在同盘临时目录完成并验证，正常发布错误会仅回退本次新建的链接，不改其他文件。强制结束进程或断电不属于跨文件原子提交保证；再运行本命令会核已有完整同版件并补另一件，已有异件仍拒绝。

只核已存在的两份下载，不重建：

```sh
python3 mas/release/build-current.py --verify
```

`--verify` 只检查两份归档及成员指纹，不运行单元测试。构建/归档核验与功能测试须分别记录。当前16席建队器的随包测试从原仓运行：

```sh
node --test mas/release/current/overlay/team-16/tests/*.test.mjs
```

`--verify` checks the archives and member fingerprints; it does not run the unit tests. Record build/archive verification separately from functional tests. The command above runs the current 16-role builder's bundled tests; it is not a browser or native-host acceptance run.

## Maintainer boundaries

The rc15 source-only doc1 revision corrects the Chinese and English lineup-link labels: the linked source archive page contains a text description, not private display avatars. It changes only those labels and this explanation. The product archives and their fingerprints above are unchanged.

rc15 源码 doc1 修订只把中英编队说明链接的名称改准确：所指页面提供文字编队说明，不提供私用展示头像。产品归档和上方指纹保持。

The earlier rc13 site1 revision updated the two HTML introduction pages and added the link check below without changing its product archives. The rc14 revision applied the approved MIT scope in active source and product notices, preserving the original four skills and frozen RC5 build inputs. The current rc15 source copy uses neutral release-candidate wording; it does not expand the license or verification scope. The quick-review archive remains unchanged. Both build and --verify now require the current downloads in the Chinese/English READMEs and in actual links on both HTML pages; a remaining old-version HTML download button stops the command before any archive is built or installed.

Run the focused link regressions without rebuilding the products:

```sh
python3 -B mas/release/tests/test_current_links.py -v
```

These checks cover the shipped introduction links and the builder's early rejection of stale or missing HTML links. They do not run a browser or prove a native browser download.

Check the current license overlay and checksum rules without rebuilding archives:

```sh
python3 -B mas/release/tests/test_current_license.py -v
```

These eight finite-fixture tests exercise the real product transformer with only its input loaders replaced. They check the two exact license overrides, rejection of extra or missing overrides, inner/root checksums, historical component attribution, and preservation of the original skill and frozen input bytes. They do not replace an actual cold build, a legal ownership review, or browser/host acceptance.

许可构建专项使用有限样本验证实际转换器，只有输入读取器使用替身；真实冷构建、现实权属核查和浏览器/宿主验收仍分别记录。

此前 rc13 site1 修订同步两份 HTML 介绍页，并增加处理归档前的网页按钮检查。rc14 已将批准的 MIT 范围写入活跃源码和产品许可说明，保留原四项技能及 RC5 冻结输入。当前 rc15 源码统一采用中性的发布候选措辞，不扩大许可或验证范围；小练习包保持原字节。上面的专项命令不重建产品，也不代表真实浏览器下载通过。

The frozen recipe remains in `release.json` and `expected.json`. The current overlay is in `current/`; `current.expected.json` pins the complete current file tree and archive. The older `build.py` and `build_downloads.py` explicitly remain historical RC5 builders. Use **build-current.py** for the version advertised by the current README.

The normal build reconstructs all source-derived files even if identical downloads already exist, so stale downloads cannot hide changed source. Differences in source content, a missing Node runtime, and ZIP-byte differences after equal file contents are reported separately. Python/zlib changes can alter compressed bytes; a matching member tree does not automatically mean the same release archive. Do not change the pinned hash to silence such a failure.

A future version must update the overlay, current expected inventory, and both language download links together, then receive its own verification. This is a release-candidate source tree based on the previously verified public commit `bc9c19458e9d4afe42e506fc65673a68c26c6a56`. The listed project-authored additions now use MIT as stated in the root NOTICE. This build does not update a remote repository or perform official publication. Historical payload/core/RIGHTS.md and mas/source/SOURCES.md are frozen RC5 inputs, not the current licensing statement; current/overlay supplies the current product counterparts. The four original skills, their license and the public PDF retain their original bytes. Their original NOTICE is read from original-notices/NOTICE and checked against the unchanged public-commit Git blob; the current root NOTICE may describe newer materials separately. The earlier reviewed Mac preview executable is preserved with its Objective-C source; this build does not recompile it.

## 维护说明

原 RC5 配方和历史脚本继续保留，当前版本只从 `build-current.py` 构建。新版需要同时更新当前增量、完整文件指纹与双语下载链接，再单独核收。源码、Node 环境及 ZIP 压缩差异分别报错，不用修改冻结指纹掩盖差异。所列项目自制材料已按根 NOTICE 范围采用 MIT，允许商用。本目录为发布候选源码；历史冻结说明保留为构建输入，当前许可说明由 current/overlay 提供。

