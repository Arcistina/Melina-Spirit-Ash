# 梅琳娜的骨灰

[English](README.md)

适用于 **Steam PC App 1.17.2 / Regulation 1.17.3**，使用ModEngine2脱机单机加载。新增游戏文案仅简体中文。

## 下载和安装

在本仓库的 **Releases** 中下载 `Melina_Spirit_Ash_v1.1.0_zhCN_ME2_GitHub.zip`。这是普通玩家所需的完整运行包，已包含图标和必需的MelinaIcons.dll。

独立仓库源码包、GitHub自动生成的 **Source code** 是开发材料，不能直接当安装包使用。详细步骤见[中文安装说明](docs/INSTALLATION_CN.md)。

## 功能

- 大赐福孪生老妪处10000卢恩购买，每周目1件，不设额外剧情解锁标记。
- 召唤消耗132 FP，遵循普通骨灰区域及重复召唤限制。
- 灵依墓地铃兰路线强化至+10。
- 复用蒙葛特战梅琳娜外观、动作、战斗AI及祷告，感知/跟随/目标选择设置适配普通骨灰使用。
- 独立新增物品和召唤记录，保留原版剧情梅琳娜及其他骨灰。
- 自定义小图和详情图，不分发原版图像全集，也不在本机重建全集。

## 依赖及兼容

另行安装[ModEngine2](https://github.com/soulsmods/ModEngine2/releases)。在已有配置中同时加入资源目录和图标DLL，使用原launchmod_eldenring.bat脱机启动。不提供或声称已验证Vortex/FOMOD安装器、无缝联机兼容。

与其他regulation.bin、简中文本或公共图标布局修改需合并，自定义图标ID65000不能冲突。图标DLL只在核验支持的原版exe及接口后启用，其他或修改后的exe不在支持范围；无需安装ERNativeUI宿主DLL。

## 仓库内容

- `src/melina_icons/`：已验收图标组件源码、契约检查、构建脚本和MinHook依赖。
- `config/balance.json`：公开数值配置，已剔除原工作簿、账号及个人路径。
- `tools/`：参数/文本准备、原行校验、资源封包和精简UI资源发布脚本。
- `assets/ui/`：梅琳娜小图、详情图及高/低画质布局元数据，不含原版贴图归档或编译DLL。
- `spec/accepted_runtime.json`：已验收运行版的逐文件校验值。
- `docs/BUILD.md`：所需工具、开发副本布局、重建步骤及验证边界。

不包含游戏原文件、提取出的原版资源、测试存档、账号、日志、工具二进制或缓存。重建参数/文本时需准备自己游戏中的兼容资源副本。

## 验收与授权

购买、完整强化、召唤限制、普通敌人/Boss仇恨、限购和原生周目补货、各处图标显示已获手动验收；具体范围见[验证说明](docs/VALIDATION.md)。逐个招式/治疗条件、元素最终伤害/减伤/异常积累、自身死亡及所有剧情状态没有逐项隔离实测。

图标、代码和部分文档使用生成式AI制作，经过用户指导修订和人工游戏验收。各次重新编译/修改并不自动继承原版二进制的实机验收。

第三方许可见LICENSES，鸣谢见[CREDITS.md](CREDITS.md)，权限见[PERMISSIONS.md](PERMISSIONS.md)。未替上传者为整个MOD选择MIT等整体开源许可；第三方代码仍遵循各自许可。
