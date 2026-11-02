# Rebuilding from the public source snapshot

Use a Windows development checkout **outside the game's Game directory**. These tools write only to this checkout. Never point a repacker at your original installation.

## Tools

- Python 3.11 or later with `cryptography` installed. The accepted packing environment used cryptography 50.0.2.
- WitchyBND 3.0.1.0, with the matching parameter definitions and compression libraries installed/configured separately: https://github.com/ividyon/WitchyBND/releases . Tool binaries and game compression libraries are not distributed in this repository.
- Zig 0.13.0 to compile the icon helper, or the accepted MelinaIcons.dll from the player release when rebuilding resources without changing icon code.

## Prepare working copies

Copy resources from your own supported installation into the following ignored working folders, then unpack/export those **copies** with WitchyBND:

```text
work/vanilla/regulation.bin
work/vanilla/regulation-bin/_witchy-bnd4.xml
work/vanilla/regulation-bin/*.param
work/vanilla/regulation-bin/{NpcParam,NpcThinkParam,BuddyParam,EquipParamGoods,SpEffectParam,ShopLineupParam}.param.xml
work/resources-vanilla/msg/zhocn/item-msgbnd-dcx/
work/resources-vanilla/msg/zhocn/item_dlc01-msgbnd-dcx/
work/resources-vanilla/msg/zhocn/item_dlc02-msgbnd-dcx/
```

Keep the original binder manifests and all binary PARAM/FMG entries. In each message-binder directory, export GoodsName.fmg, GoodsInfo.fmg, GoodsInfo2.fmg and GoodsCaption.fmg to `.fmg.xml`. There are three separate containers; changing only the base container does not provide the final game's complete text path.

The expected parameter binder version is 11730034. These inputs are not part of the repository or source ZIP. Paths in the original binder's internal manifest may be native game build paths; do not replace them with workstation paths.

## Build resources

From the repository root, use the accepted player DLL without recompiling it:

```powershell
.\tools\build_resources.ps1 -Python python -Witchy 'PATH_TO_WITCHYBND_EXE' -IconDll 'PATH_TO_ACCEPTED_MelinaIcons.dll'
```

Alternatively compile the unchanged helper as part of the build:

```powershell
.\tools\build_resources.ps1 -Python python -Witchy 'PATH_TO_WITCHYBND_EXE' -Zig 'PATH_TO_ZIG_EXE'
```

`config/balance.json` is the numeric input to the parameter builder. It retains the final user-selected values and completed curves, without requiring a spreadsheet. The text builder contains the Chinese item/summon-bar text. Image/layout assets are pinned to the accepted custom-only assets; there is no original-image archive reconstruction.

The workflow prepares independent rows, checks original PARAM row bytes, retains the real binder version, packs/encrypts the regulation copy, builds all three message containers, and publishes the custom UI assets/helper under `build/melina_ashes/mod`. It does not install into ModEngine2, modify saves, or launch the game.

The original Tiche/Melina rows are left unchanged. Refer to the source's separate IDs and target-priority/perception adaptation before merging with other parameter mods.

## Verify

```powershell
python .\tools\verify_runtime.py --directory .\build\melina_ashes\mod
```

This checks the exact accepted nine-file snapshot. If a freshly compiled DLL differs while the other eight files match, use `--allow-rebuilt-helper` only to compare the resource build; it does not runtime-certify that DLL. The C contract test checks string-prefix/identifier/bounds handling during native compilation, not all game behavior.

Changes to balance, text, native interfaces, compiler or executable need their own validation. Do not remove the executable/interface checks to label an unsupported build as compatible. Local resource reconstruction is independent from the immutable player-release assets.

## Publishing

Do not upload `work`, `build`, original game data, tools, caches or an existing private `.git` history. The clean source snapshot and release assets were separately assembled and checked. No automated GitHub publishing workflow or account credentials are included.
