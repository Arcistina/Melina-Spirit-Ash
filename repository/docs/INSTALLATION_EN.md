# Melina Spirit Ash 1.1.0

For unmodified Steam PC Elden Ring App 1.17.2 / Regulation 1.17.3, offline single-player. **Set the game text language to Simplified Chinese:** other translations for the new item are not included.

Adds a standalone Melina spirit ash using her original Morgott-battle appearance, moves and AI. Buy one per journey from Twin Maiden Husks for 10,000 runes. Summoning costs 132 FP and follows ordinary spirit-ash restrictions. Upgrade with Ghost Glovewort to +10.

This release contains only the custom Melina small/detail image data. It does not ship or locally reconstruct the original image archives. Original icons are read from your installed game. Gameplay parameters and Chinese text are unchanged from the accepted 1.0 build.

## ModEngine2 installation

Extract the included `mod/MelinaAshes` directory into ModEngine2. Add this entry inside the existing `[extension.mod_loader]` `mods` array:

```toml
{ enabled = true, name = "MelinaAshes", path = "mod/MelinaAshes" }
```

Add `"mod/MelinaAshes/MelinaIcons.dll"` to the existing `[modengine]` `external_dlls` array. Keep your other DLL entries and existing save-isolation settings. The loader must have `enabled = true` and `loose_params = false`. Do not create duplicate TOML sections/keys or overwrite your whole configuration with the snippet.

Launch with ModEngine2's original `launchmod_eldenring.bat`. Do not copy files into the game's Game directory. ModEngine2, Alt Saves, merchant mods, saves and account data are not included.

The icon helper is required. It checks the exact supported stock executable and native interfaces before installing its icon-only hooks. Other executable versions and modified executables are unsupported. It does not change gameplay, saves or game files. It needs no ERNativeUI host DLL. A diagnostic `MelinaIcons.log` may be created beside the helper.

## Upgrade and removal

Replace the entire old MelinaAshes directory with this version after exiting the game. Do not retain the old `01_common.tpf.dcx`, `00_solo.tpfbhd`, `00_solo.tpfbdt`, or experimental `05_dummy.tpf.dcx` overrides.

To disable, set the resource entry to `enabled = false` and remove the icon helper from `external_dlls`. Preserve your save redirection and other mods. Do not rename a mod save over an original online save.

Other regulation, message or common-layout mods require merging; merely enabling both is insufficient. Icon ID 65000 must be unique in your merged setup. Seamless Co-op compatibility is not provided.

Purchase, upgrades, summoning restrictions, ordinary/Boss aggro, stock persistence and native NG replenishment were manually accepted. Inventory, detail, hotbar and other original icons passed the new custom-only loader test. Every individual spell/heal trigger, story state and final per-element damage/negation/status buildup case was not separately tested.

The icon, code and parts of the documentation were produced with generative AI and manually tested in game. Native image-interface/ownership research derives from Flammrock's ERNativeUI (MIT); hooks use MinHook (BSD). See the repository LICENSES, src/melina_icons and docs/BUILD.md for notices, source and build instructions. No ERNativeUI host is bundled or required. See PERMISSIONS.md for mod-specific permissions; third-party code retains its own licenses.
