# 团队配置编辑器 · Team builder

解压这个目录，用浏览器打开 [index.html](index.html)。席位、群籍、职责、交接和任选头像均在本机编辑。默认有首席、生产官、审核官。要为自己的团队扩编，可以新增席位或群，再在「交接」里指定派工、制作、独审和交回人。

1. 改团队名称。到「席位」改职责或新增岗位。头像可留空，也可选择 PNG、JPEG 或 WebP（单张 ≤ 512 KiB、每边 ≤ 2048 像素）。
2. 到「群组」选择知情成员，写明这个群为什么存在。到「交接」选择实际责任人。建队器核对生产与独审的席位 ID 是否不同。两席背后是否同一操作者、审核是否实际独立，要看运行记录和审核席打开的成品。
3. 点「保存配置文件」。浏览器将导出包含头像的 JSON。以后点「打开配置」选回该文件，即可接着编辑。浏览器页面内的草稿只保留到关页。已有宿主账号的权限、模型和收费由宿主管理。

来自随包三席配置的 `solo-to-team.team` 1.0 文件可以作为起点。预览会提醒，本次只采用其岗位、群、成员及交接分工，以编辑器的中性格式另存。原文件保留。“带到你的平台”可下载两种文件：OpenMausBot 部门定义或 DeepSeek Harness 项目 ZIP。前者保留分开的派工席与交回席；后者由派工席所在根会话交付，只支持派工与交回指向同一席。群与群籍随协作说明保存，本页不会在宿主开原生群聊。下载后按对应宿主说明导入或打开。

**English.** Extract the files together and [open the local editor](index.html#en). Customize the three starter seats, add roles and groups, choose their members and purposes, then assign dispatch, production, independent review, and delivery. Optional avatars are stored in the file; use a PNG/JPEG/WebP up to 512 KiB and 2048 pixels per side. Group membership provides context. Each host decides what actions an account is authorized to take. Save the JSON before closing to resume later. The host buttons produce an OpenMausBot department file or a DeepSeek Harness project ZIP. OpenMausBot can keep dispatch and delivery separate. The Harness project returns in the root session and requires the same dispatch and delivery seat. Group membership is carried as coordination instructions. Open the export in the appropriate host.

## 自定义导出的验证范围 / Evidence for custom exports

固定首单包与用户导出的岗位包是两份不同的文件，各自核收。自定义 DeepSeek 样例改名并新增一席后，据团队本机观察，使用当前这版建队器导出的项目在本机宿主运行；界面显示 3 个子任务，留有岗位分工、审核记录和第四席回件。云端复核未取得平台运行日志。自定义 OpenMausBot 四席部门文件已用 0.1.148 的实际数据层在隔离存储导入；用户真实账号界面跑单尚未实测。两项的回执和导入记录留在团队侧，未放入本包，读者无法在包内复核。

The builder checks that production and review have different role IDs. The run record and the file the reviewer opened are needed to establish who operated those seats and whether review was independent. The fixed starter and a team exported by the editor are separate artifacts with separate evidence. In the team’s local observation, a renamed four-seat team ran in DeepSeek Harness from a project exported by this version of the builder. The UI showed three subtasks; retained files cover assignments, review and the fourth seat’s return. Cloud review had no platform runtime logs. A custom four-seat OpenMausBot department was imported with the native 0.1.148 data layer in isolated storage. A run in a real user account through its UI remains untested. The team holds the receipts and import records for these two observations outside this package; readers cannot independently verify them from this download.

[中性文件格式 / Definition format](FORMAT.md)
