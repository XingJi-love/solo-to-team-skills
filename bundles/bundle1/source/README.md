# 完整包维护与重建

输入inputs.zip收集本轮所用adapter.5公开候选材料，不含现役头像、内部聊天或账号数据。build_bundles.py以Python标准库重建四个完整ZIP；不访问网络、不安装到宿主。verify_bundles.py检查独立解包、文件、路径、资料附件、许可与配置数字。

在此目录执行：

```sh
python3 build_bundles.py --out ../packages
python3 verify_bundles.py
```

需要支持Path.is_relative_to的Python3.9+；已用本机Python3.12.14运行。不要在含用户修改的已解压目录覆盖执行；默认输出是本交付的构建产物。可用--out指定新的空目录。输入和打包时间固定，独立空目录重建的四ZIP应逐字节相同。

不从网上另拉依赖，不把已有平台技能全局重装。四个基础Skill原件及原平台载荷指纹逐包列在BUNDLE.json.original_files；包装文档为本轮新写，不能称全部文件原字节。

本源码包仅重建四平台完整包；PDF为独立说明成品，本包不含PDF维护源。完整MAS维护源码另见仓库mas/releases中的对应版本，不以此打包源码替代。
