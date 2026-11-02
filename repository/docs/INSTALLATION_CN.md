# 梅琳娜的骨灰 1.1.0

Steam PC / App 1.17.2 / Regulation 1.17.3 / 简体中文 / 原版单机。

新增独立梅琳娜骨灰，复用蒙葛特战梅琳娜的外观、动作、战斗AI及祷告。大赐福孪生老妪处10000卢恩购买，每周目库存1；召唤消耗132 FP，遵循普通骨灰限制；使用灵依墓地铃兰强化至+10。原版梅琳娜和其他骨灰记录保留。

1.1.0改用独立图像加载：只有梅琳娜的160像素小图和1024像素详情图，不携带原版图像合集，不在安装时复制或生成原版大图包。其他图像继续从自己的游戏原档读取。骨灰参数与文本和已验收1.0一致。

## 安装到ModEngine2

1. 正常退出游戏，将压缩包中的`mod/MelinaAshes`放入ModEngine2目录，保留文件层级。
2. 在`config_eldenring.toml`已有的`[extension.mod_loader]`段，将以下条目加入`mods = [...]`数组，条目间用英文逗号分隔：

```toml
{ enabled = true, name = "MelinaAshes", path = "mod/MelinaAshes" }
```

3. 在`[modengine]`已有的`external_dlls = [...]`数组加入以下DLL路径：

```toml
"mod/MelinaAshes/MelinaIcons.dll"
```

保留原有其他DLL项。不要创建第二份同名表或数组，也不要把资源文件夹写入`external_dlls`。所需设置为`extension.mod_loader.enabled = true`和`loose_params = false`。包内`ModEngine2配置片段.txt`可供复制，不用于覆盖整份配置。

4. 使用原有`launchmod_eldenring.bat`脱机启动。不要将资源或DLL复制到游戏的`Game`目录。

图标DLL是本包必需组件，仅处理本MOD的图标。它校验原版exe的SHA-256及原生接口后启用；不同版本或经过修改的exe不在支持范围，校验不符时不会安装图标钩子。无需额外安装ERNativeUI。DLL可在本MOD目录生成小型诊断日志`MelinaIcons.log`，不会改写游戏文件。

本包不含ModEngine2、Alt Saves、ermerchant、幻化、测试存档或账户信息。如已使用Alt Saves，请保留它与原存档扩展名配置；不转换或覆盖存档。使用原版角色前自行备份，MOD副档不改名覆盖原版在线存档。

## 更新和停用

从旧的大图包更新时，先退出游戏，用这个完整文件夹替换旧`MelinaAshes`文件夹。新目录不应保留`01_common.tpf.dcx`、`00_solo.tpfbhd`、`00_solo.tpfbdt`或测试用`05_dummy.tpf.dcx`。它们会阻碍原版图像回退，也会保留大体积。

停用时，将`mods`中的本MOD条目设为`enabled = false`，并移除`external_dlls`中的`MelinaIcons.dll`条目。保留自己的存档隔离设置和其他MOD。不要通过删除Alt Saves切换存档。

## 兼容与已验证范围

仅支持上述原版Steam PC版本及简体中文。其他语言的新增文案尚未提供；其他应用版本需要更新组件和参数。

与其他`regulation.bin`、简中文本、`01_common.sblytbnd.dcx`修改不能自动合并。自定义图标ID为65000；合用冲突MOD时需合并参数、文案和布局，并避免重复ID。此包按原版单机制作，未制作无缝联机兼容版。

购买、完整强化链、FP与重复召唤限制、士兵/Boss仇恨、读档限购、新周目补货/再购买以及新图标的背包、详情、快捷栏、其他原图均获手动验收。+10生命与异常阈值有只读运行时证据。具体每个祷告、治疗触发、所有剧情状态、每种元素最终伤害/减伤和异常积累未逐项隔离实测。

## 内容与鸣谢

- 本体为参数、文本和布局/图像资源；`MelinaIcons.dll`负责小图的原生资源注册和详情图路径，不修改战斗AI、数值或存档。
- 图标、代码和部分说明使用生成式AI制作并经过人工验收。原版人物、动作及其他图像仍使用玩家自己的游戏文件。
- 第三方代码：MinHook（BSD）及ERNativeUI的原生图像接口/所有权研究（MIT），许可见`LICENSES`。不依赖或打包ERNativeUI宿主DLL。
- 图像处理/构建使用WitchyBND、DirectXTex和Zig。源码和重建说明见仓库的src/melina_icons及docs/BUILD.md。

权限说明见仓库或安装包内PERMISSIONS.md；第三方代码遵循各自许可。
