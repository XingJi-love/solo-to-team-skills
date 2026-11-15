> 当前 README 的 0.3.0-rc.7 下载请运行 `python3 mas/release/build-current.py`，详见 [CURRENT.md](CURRENT.md)。下文保留历史 RC5 构建说明。 / For the current downloads use [build-current.py](CURRENT.md); the RC5 recipe below remains historical.

# Build the full Solo to Team ZIP / 完整旗舰包构建

在 **solo-to-team-skills 仓库根目录**，使用 Python 3.9 及以上版本和可运行 `mas/source/build.mjs` 的 Node.js。整个流程使用标准库。日常构建不下载依赖，不读取现成发行 ZIP，不启动宿主应用。

```sh
python3 mas/release/build.py
python3 mas/release/build.py --verify dist/Solo-to-Team-MAS-0.2.2-rc.5.zip
```

The first command produces the full **119-entry** archive in `dist/`. The second independently reads every member and checks its SHA-256 and the complete archive against [the reference manifest](expected.json). A different existing output is preserved. Use `--output new-name.zip` to choose another destination.

**RC5 核收值**：18,546,193 字节，SHA-256 `5e2f86298c08182eb7f2f3500ff767adc4b2a21e59a64a8c5c6993333f5b4d73`。字节级再现是在 Python 3.9.6、zlib 1.2.12、Node.js 24.21.0 上实测的结果。其他运行时可能使用不同 DEFLATE 压缩流。构建器逐项校验内包、文件树和外层 ZIP；压缩结果有差异时，不能用该构建冒称原指纹。

## Source map / 素材从哪里来

| 输入 | 构建用途 |
| --- | --- |
| 根仓原有四个 Skill、插件清单、模板、示例、LICENSE、NOTICE 以及 `docs/solo-to-team-value.pdf` | 原件从当前 checkout 读取，先核 Git blob；NOTICE 用 original-notices/ 中的同字节原副本，避免当前新增内容的使用范围改动影响旧技能。原仓基准提交为 `bc9c19458e9d4afe42e506fc65673a68c26c6a56`。新增子树不携带第二份 PDF。 |
| [两份冻结 README](original-readmes/) | 原仓中英首页会添加 MAS 入口，这里仅保留历史技能组件需要的原始两份小文件。 |
| `mas/source/` | Node 从模块和原创图标实际构建统一台 HTML。仓内源码同时进入旗舰 ZIP。 |
| `mas/media/`、`mas/evidence/` | 复用现有媒体与两份已审核的合成题面。 |
| [payload](payload/) | 平台适配源件、岗位卡、公开或合成的示例资料、独立图像、首页及说明。模板中的 `[[MAS:version]]` 与 `[[MAS:asset-N]]` 在构建时替换，图片从共享素材取。 |
| [recipes](recipes/) | 原 6 个内包的文件顺序、属性、压缩参数和来源。WorkBuddy 安装器内的专家团共用同一份配方。续办工具的内包与外层展示共享可读文件。 |
| [platform-source/TeamPreview.m](platform-source/TeamPreview.m) | 安装预览器的项目 Objective-C 源码。为匹配已审核的既有安装器，RC5 日常打包使用随源码收录的已核通用 Mach-O、图标及签名资源，不调用 Xcode 重签。没有验证由本机编译器重新生成该二进制也能逐字节相同。 |

The checkout supplies the original 21 files, the six demo media files, proof fixtures and the readable builder sources. The release overlay supplies the remaining templates, source assets and the pinned macOS launcher. Individual adapter archives are built from their expanded members. The outer core and product checksum documents are recomputed; upstream component archive hashes identify the approved historical inputs. The two small frozen READMEs let the live repository add links without changing the old component.

## Editing and future candidates / 修改与下一版

改模板、岗位卡或 `mas/source/` 后，先用不同版本号制作本地草案：

```sh
python3 mas/release/build.py --draft 0.2.2-dev.1
```

草案仍从实际素材构建并核对写入的 ZIP。更改过的组件会记录新的文件树指纹、将对应上游压缩包指纹标为 `null`，并注明本地草案。正式 RC5 使用不带 `--draft` 的命令，任一锁定文件有差异时会拒绝产生该版本成品。To add or remove members, change [release.json](release.json) and the corresponding member recipe. For an approved successor, refresh the manifests and verified upstream component fingerprints under the new version, and repeat the isolated rebuild before identifying the new SHA-256. The project owner decides publication and licensing; packaging adds no new grant.
