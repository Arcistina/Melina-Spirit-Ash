# Melina Spirit Ash

[简体中文](README.zh-CN.md)

A standalone Melina spirit ash for **Steam PC Elden Ring App 1.17.2 / Regulation 1.17.3**, using ModEngine2 in offline single-player. **New in-game text is Simplified Chinese only.** English installation instructions do not provide an English in-game translation.

## Download and install

Open this repository's **Releases** section and download `Melina_Spirit_Ash_v1.1.0_zhCN_ME2_GitHub.zip`.

The player archive includes all required mod resources and MelinaIcons.dll. The separate repository/source archive and GitHub's automatically generated **Source code** downloads are for development, not direct installation. See [installation instructions](docs/INSTALLATION_EN.md) or [中文安装说明](docs/INSTALLATION_CN.md).

## Features

- Purchase from Twin Maiden Husks at Roundtable Hold for 10,000 runes, one per journey; no additional story-unlock flag.
- Summon for 132 FP under ordinary spirit-ash restrictions.
- Upgrade through +10 with Ghost Glovewort and Great Ghost Glovewort.
- Reuse original Morgott-battle Melina appearance, moves, combat AI and incantations. Perception, follow and target-selection settings are adapted for ordinary spirit-ash use.
- Independent item/summon records retain the original story Melina and other ashes.
- Custom small/detail icon data without original image collections or install-time reconstruction of those collections.

## Requirements and compatibility

[ModEngine2](https://github.com/soulsmods/ModEngine2/releases) is installed separately. Add both the resource directory and icon DLL to its existing configuration, then use the original `launchmod_eldenring.bat`. No Vortex/FOMOD installer or Seamless Co-op compatibility is provided.

Other regulation, Simplified Chinese message and common-layout modifications require merging. Icon ID 65000 must remain unique. The icon helper checks the exact supported stock executable/native interfaces; other or modified executables are unsupported. No additional ERNativeUI host DLL is needed.

## Repository contents

- `src/melina_icons/`: the accepted icon-helper C sources, contract test, build script and MinHook dependency.
- `config/balance.json`: public numeric configuration, without the original workbook, account information or workstation paths.
- `tools/`: parameter/text preparation, original-row verification, resource packing and custom-only UI publishing.
- `assets/ui/`: two Melina image payloads and two layout-metadata binders. No stock texture archive or compiled DLL.
- `spec/accepted_runtime.json`: checksums for the accepted player build.
- `docs/BUILD.md`: tools, working-copy layout, rebuild instructions and validation limits.

Original game data, game-file extraction results, development saves, logs, account details, tool binaries and build caches are excluded. Supply your own compatible game-resource copies for a resource rebuild.

## Verification and support

Purchase, complete upgrades, FP/duplicate-summon restrictions, ordinary-enemy/Boss aggro, persistent stock, native NG replenishment/rebuy and inventory/detail/hotbar/original-icon display were manually accepted. Live +10 HP and resistance thresholds were also checked. See [validation scope](docs/VALIDATION.md).

Every spell/healing trigger, elemental damage/negation/status-buildup case, spirit death and story state was not individually isolated. When reporting a problem, include the game versions, language, installation method, conflicting mods and relevant diagnostic text. Do not attach saves or account credentials to public reports.

## AI disclosure, credits and permissions

The in-game icon, code and parts of the documentation were produced with generative AI, revised under user direction and manually tested in game. This is not a claim that every source rebuild has been runtime-tested.

Third-party notices are in [LICENSES](LICENSES). See [credits](CREDITS.md) and [permissions](PERMISSIONS.md). No blanket open-source license has been selected for all mod-specific code/data/artwork; third-party components retain their own licenses.
