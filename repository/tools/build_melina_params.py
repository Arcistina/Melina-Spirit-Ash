"""Build independent Melina rows from public balance configuration and local game copies."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import math
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work" / "vanilla" / "regulation-bin"
BUILD = ROOT / "work" / "melina-build" / "regulation-bin"
OUTPUT = ROOT / "build" / "melina_ashes"
TABLES = ["NpcParam", "NpcThinkParam", "BuddyParam", "EquipParamGoods", "SpEffectParam", "ShopLineupParam"]
IDS = {"goods_base": 280000, "summon_effect_base": 280000, "buddy": 28000000,
       "npc": 121801000, "think": 121801000, "growth_effect_base": 1280000,
       "spirit_common_effect": 1280100, "shop_row": 101882, "shop_stock_flag": 280820}

# Reuse Tiche's ordinary spirit perception, target memory and return behavior.
# Animation IDs, navigation capabilities, jumps, sounds and battle goal remain
# Melina's: those fields can refer to motions absent from her character bundle.
TICHE_THINK_ADAPT_FIELDS = [
    "searchEye_dist", "searchEye_angY", "searchEye_angX", "eye_dist", "ear_dist",
    "ear_soundcut_dist", "ear_listenLevel", "nose_dist", "eye_angX", "eye_angY",
    "eye_BackOffsetDist", "eye_BeginDist", "disableDark", "isUpdateBattleSight",
    "battleEye_updateDist", "battleEye_updateAngX", "battleEye_updateAngY",
    "searchTargetLv1ForgetTime", "searchTargetLv2ForgetTime", "SightTargetForgetTime",
    "SoundTargetForgetTime", "MemoryTargetForgetTime", "BattleStartDist",
    "BackHomeLife_OnHitEneWal", "maxBackhomeDist", "backhomeDist", "backhomeBattleDist",
    "BackHome_LookTargetTime", "BackHome_LookTargetDist", "targetSys_DmgEffectRate",
    "TeamAttackEffectivity", "searchThreshold_Lv0toLv1", "searchThreshold_Lv1toLv2",
    "goalAction_ToCaution", "goalAction_ToCautionImportant", "goalAction_ToSearchLv1",
    "goalAction_ToSearchLv2", "goalAction_ToDisappear", "actTypeOnFailedPath",
    "actTypeOnNonBtlFailedPath", "disableLocalSteering", "platoonReplyTime",
    "platoonReplyAddRandomTime", "callHelp_ActionAnimId", "callHelp_CallActionId",
    "callHelp_MyPeerId", "callHelp_CallPeerId", "callHelp_CallValidMinDistTarget",
    "callHelp_CallValidRange", "callHelp_ForgetTimeByArrival", "callHelp_MinWaitTime",
    "callHelp_MaxWaitTime", "callHelp_ReplyBehaviorType",
]


def guarded(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f"Write outside project forbidden: {resolved}")
    return resolved


def write_json(path, data):
    guarded(path).parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_xml(name):
    tree = ET.parse(SOURCE / f"{name}.param.xml")
    root = tree.getroot()
    defaults = {f.get("name"): f.get("defaultValue") for f in root.findall("./fields/field")}
    rows = {int(r.get("id")): r for r in root.findall("./rows/row")}
    return {"tree": tree, "root": root, "defaults": defaults, "rows": rows,
            "original_attrs": {i: dict(r.attrib) for i, r in rows.items()}, "new_ids": []}


def number(value):
    if isinstance(value, str):
        return value
    if not math.isfinite(value):
        raise ValueError("Non-finite parameter value")
    return str(value) if isinstance(value, int) else format(value, ".9g")


def clone(table, source_id, new_id, label, changes):
    if new_id in table["rows"]:
        raise ValueError(f"Parameter ID collision: {new_id}")
    new = deepcopy(table["rows"][source_id])
    new.set("id", str(new_id))
    new.set("paramdexName", label)
    for key, value in changes.items():
        if key not in table["defaults"]:
            raise ValueError(f"Unknown parameter field {key}")
        new.set(key, number(value))
    table["root"].find("rows").append(new)
    table["rows"][new_id] = new
    table["new_ids"].append(new_id)
    return new


def build_spirit_think(table):
    value = lambda row, field: table["rows"][row].get(field, table["defaults"][field])
    changes = {field: value(121000000, field) for field in TICHE_THINK_ADAPT_FIELDS}
    changes.update({"logicId": 10000, "battleGoalID": 218000, "isBuddyAI": 1})
    think = clone(table, 21800000, IDS["think"], "[MelinaAsh] Tiche spirit behavior / Melina battle", changes)
    for field in ["battleGoalID", "idAttackCannotMove", "rangedAttackId", "spEffectId_RangedAttack",
                  "shiftAnimeId_RangedAttack", "enableJumpMove", "enableJumpMove_onBattle",
                  *(f"soundBehaviorId{i:02}" for i in range(1, 9))]:
        assert think.get(field, table["defaults"][field]) == value(21800000, field), field
    write_json(OUTPUT / "ai-adaptation-report.json", {
        "reference_think": 121000000, "melina_original_think": 21800000,
        "adapted_think": IDS["think"], "battle_goal_preserved": 218000,
        "all_adapted_fields_match_tiche": True,
        "selected_fields": {field: value(121000000, field) for field in TICHE_THINK_ADAPT_FIELDS},
        "changes_from_morgott_profile": {
            field: {"before": value(21800000, field), "after": value(121000000, field)}
            for field in TICHE_THINK_ADAPT_FIELDS if value(21800000, field) != value(121000000, field)
        },
        "incoming_target_priority_effect": {"id": 296010, "targetPriority": -0.5,
                                            "note": "Same additive target priority adjustment as Tiche; not a guaranteed percentage of aggro or forced target switching."},
        "retained_original_npc_marker": {
            "effect_id": 440, "stateInfo": 371,
            "community_state_label": "NPC Transparency Disable",
            "community_reference": "https://github.com/vawser/Smithbox/blob/main/src/Smithbox.Data/Assets/PARAM/ER/Param%20Enums/SP_EFFECT_TYPE.json",
            "reason": "Retained from source Melina following the user's explicit request to restore effect 440. Runtime restoration regression is recorded separately.",
            "direct_aggro_mechanism_confirmed": False,
        },
        "scope": "Only this new spirit's NPC and Think rows change; enemy/boss parameters, original Melina and Tiche rows are unchanged.",
        "runtime_validation": "See runtime-verification.json; this report describes configured values only.",
    })
    return think


def normalize():
    config = json.loads((ROOT / "config/balance.json").read_text(encoding="utf-8"))
    assert config["ids"] == IDS, "Review both the code and configuration before changing IDs"
    records = deepcopy(config["records"])
    assert len(records) == 21 and all(len(r["growth"]) == 10 for r in records)
    for record in records:
        if record["category"] == "抗性" and record["immunity_mode"] == "免疫":
            continue
        vals = [record["base"], *record["growth"]]
        if any(not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 for x in vals):
            raise ValueError(f"Missing or invalid inputs: {record['metric']}")
        if record["category"] == "减伤" and any(record["base"] * g > 1 for g in [1, *record["growth"]]):
            raise ValueError(f"Damage negation exceeds 100%: {record['metric']}")
    return records


def main():
    records = normalize()
    selected_icon = {"icon_id": 65000, "version": 3}
    tables = {name: load_xml(name) for name in TABLES}
    for path in [BUILD, OUTPUT / "mod"]:
        guarded(path).mkdir(parents=True, exist_ok=True)
    # Copy only into the project; no unpacker is pointed at the game directory.
    def ignore(_directory, names):
        wanted = {"_witchy-bnd4.xml", *(f"{n}.param.xml" for n in TABLES)}
        return [n for n in names if n.endswith(".xml") and n not in wanted]
    shutil.copytree(SOURCE, guarded(BUILD), dirs_exist_ok=True, ignore=ignore)

    npc_changes = {"hp": int(records[0]["base"]), "teamType": 47,
                   "spEffectID3": 0, "GameClearSpEffectID": 0, "dlcGameClearSpEffectID": -1,
                   "spEffectID20": 440,
                   "getSoul": 0}
    # Effect 440 uses state 371, labeled NPC Transparency Disable by current
    # Smithbox data (the bundled older dictionary calls it Unknown).
    # Keep the source NPC effect as explicitly requested by the user, together
    # with the model/phantom VFX and the accepted Tiche perception profile.
    neg_fields = ["neutralDamageCutRate", "slashDamageCutRate", "blowDamageCutRate", "thrustDamageCutRate",
                  "magicDamageCutRate", "fireDamageCutRate", "thunderDamageCutRate", "darkDamageCutRate"]
    for field, record in zip(neg_fields, records[6:14]):
        npc_changes[field] = 1 - record["base"]
    resistance_fields = ["resist_poison", "resist_desease", "resist_blood", "resist_freeze",
                         "resist_sleep", "resist_madness", "resist_curse"]
    for field, record in zip(resistance_fields, records[14:]):
        if record["immunity_mode"] == "数值":
            npc_changes[field] = int(record["base"])
    npc = clone(tables["NpcParam"], 21801034, IDS["npc"], "[MelinaAsh] Melina independent spirit", npc_changes)
    # Keep her original golden phantom shader and character VFX; add spirit lifecycle hooks.
    occupied = {int(npc.get(f"spEffectID{i}", tables['NpcParam']['defaults'].get(f"spEffectID{i}", '-1')))
                for i in range(32)}
    for effect_id in [IDS["spirit_common_effect"], 297000, 297200, 296010]:
        if effect_id in occupied:
            continue
        for i in range(32):
            key = f"spEffectID{i}"
            value = int(npc.get(key, tables["NpcParam"]["defaults"].get(key, "-1")))
            if value <= 0:
                npc.set(key, str(effect_id))
                occupied.add(effect_id)
                break
        else:
            raise ValueError("No free NPC effect slot")

    build_spirit_think(tables["NpcThinkParam"])
    buddy_changes = {"triggerSpEffectId": IDS["summon_effect_base"], "npcParamId": IDS["npc"],
                     "npcThinkParamId": IDS["think"]}
    buddy_changes.update({f"dopingSpEffect_lv{i}": IDS["growth_effect_base"] + i for i in range(11)})
    clone(tables["BuddyParam"], 20000000, IDS["buddy"], "[MelinaAsh] Melina", buddy_changes)

    # Add the intended acquisition route early so the prototype is testable through
    # normal gameplay; no item-injection utility is required to obtain it.
    shop = tables["ShopLineupParam"]
    assert not any(int(r.get("eventFlag_forStock", shop["defaults"].get("eventFlag_forStock", "0")))
                   == IDS["shop_stock_flag"] for r in shop["rows"].values()), "Shop stock flag collision"
    clone(shop, 101800, IDS["shop_row"], "[MelinaAsh] Twin Maiden Husks / Melina", {
        "equipId": IDS["goods_base"], "value": 10000, "eventFlag_forStock": IDS["shop_stock_flag"],
        "eventFlag_forRelease": 0, "sellQuantity": 1, "equipType": 3, "costType": 0,
        "setNum": 1,
    })

    # Neutralize the generic spirit damage corrections so the supplied target values
    # are not silently multiplied by an extra 0.25 output or 0.5 incoming modifier.
    common_changes = {f"{side}{target}DmgCorrectRate_{element}": 1
                      for side in ["def", "atk"] for target in ["Enemy", "Player"]
                      for element in ["Physics", "Magic", "Fire", "Thunder", "Dark"]}
    clone(tables["SpEffectParam"], 296000, IDS["spirit_common_effect"], "[MelinaAsh] Spirit common / neutral damage corrections", common_changes)

    attack_fields = ["physicsAttackPowerRate", "magicAttackPowerRate", "fireAttackPowerRate",
                     "thunderAttackPowerRate", "darkAttackPowerRate"]
    res_growth_fields = ["registPoizonChangeRate", "registDiseaseChangeRate", "registBloodChangeRate",
                         "registFreezeChangeRate", "registSleepChangeRate", "registMadnessChangeRate", "registCurseChangeRate"]
    level_summary = []
    for level in range(11):
        factor = lambda r: 1 if level == 0 else r["growth"][level - 1]
        goods_changes = {"refId_default": IDS["summon_effect_base"] + level,
                         "consumeMP": 132, "consumeHP": -1,
                         "reinforceGoodsId": IDS["goods_base"] + level + 1 if level < 10 else -1,
                         "compTrophySedId": -1, "trophySeqId": -1,
                         "sortId": 61420 + level}
        if selected_icon:
            goods_changes["iconId"] = selected_icon["icon_id"]
        clone(tables["EquipParamGoods"], 200000 + level, IDS["goods_base"] + level,
              f"[MelinaAsh] 梅琳娜的骨灰 +{level}", goods_changes)
        clone(tables["SpEffectParam"], 200000 + level, IDS["summon_effect_base"] + level,
              f"[MelinaAsh] Summon +{level}", {})
        growth_changes = {"maxHpRate": factor(records[0])}
        growth_changes.update({field: record["base"] * factor(record)
                               for field, record in zip(attack_fields, records[1:6])})
        growth_changes.update({field: factor(record) if record["immunity_mode"] == "数值" else 1
                               for field, record in zip(res_growth_fields, records[14:])})
        # Elemental received-damage corrections implement the target negation ratio.
        phys_ratios = [(1 - r["base"] * factor(r)) / (1 - r["base"]) if r["base"] < 1 else 1
                       for r in records[6:10]]
        if max(phys_ratios) - min(phys_ratios) > 1e-8:
            raise ValueError("Different per-physical-type growth needs a separate implementation")
        incoming = [phys_ratios[0]] + [(1 - r["base"] * factor(r)) / (1 - r["base"]) if r["base"] < 1 else 1
                                      for r in records[10:14]]
        for element, ratio in zip(["Physics", "Magic", "Fire", "Thunder", "Dark"], incoming):
            for target in ["Enemy", "Player"]:
                growth_changes[f"def{target}DmgCorrectRate_{element}"] = ratio
        clone(tables["SpEffectParam"], 290000, IDS["growth_effect_base"] + level,
              f"[MelinaAsh] Growth +{level}", growth_changes)
        level_summary.append({"level": level, "hp_unrounded": records[0]["base"] * factor(records[0]),
                              "attack_coefficients": [r["base"] * factor(r) for r in records[1:6]],
                              "target_negations": [r["base"] * factor(r) for r in records[6:14]],
                              "resistances": ["免疫" if r["immunity_mode"] == "免疫" else r["base"] * factor(r)
                                              for r in records[14:]]})

    for name, table in tables.items():
        assert all(dict(table["rows"][i].attrib) == original for i, original in table["original_attrs"].items()), name
        rows_node = table["root"].find("rows")
        rows_node[:] = sorted(list(rows_node), key=lambda r: int(r.get("id")))
        table["tree"].write(guarded(BUILD / f"{name}.param.xml"), encoding="utf-8", xml_declaration=True)
    report = {"status": "parameter specification; packed validation and runtime status are recorded separately in build-verification.json",
              "ids": IDS, "added_rows": {n: t["new_ids"] for n, t in tables.items()},
              "original_rows_unchanged": True, "levels": level_summary,
              "implementation_notes": [
                  "Original Melina character, battle goal and motion IDs retained; perception, target memory, search and return settings copied from Tiche in an independent Think row.",
                  "Native spirit target-priority effect 296010 added to the new NPC, matching Tiche's -0.5 additive correction; no enemy or boss AI changed.",
                  "Source effect 440 restored to the new spirit at the user's request. Current Smithbox labels state 371 NPC Transparency Disable; a direct aggro mechanism has not been established.",
                  "Leyndell/NG scaling removed only from the new NPC; original NPC and all original parameter rows remain unchanged.",
                  "Original golden phantom shader and character VFX retained; blue spirit-color override not added.",
                  "Generic outgoing/incoming spirit damage corrections neutralized for this new spirit so supplied targets remain direct.",
                  "Fixed defense, stamina, healing rules and resistance-increase-on-proc behavior retain original NPC values.",
                  (f"Approved Melina icon v{selected_icon['version']} uses independent icon ID {selected_icon['icon_id']} at all levels."
                   if selected_icon else "Goods temporarily reuse Tiche icon; final user icon pending.") + " Chinese text is built by build_item_text.py.",
              ]}
    write_json(OUTPUT / "parameter-build-report.json", report)
    print(json.dumps({"build_dir": str(BUILD), "output": str(OUTPUT),
                      "added_counts": {n: len(t["new_ids"]) for n, t in tables.items()},
                      "level_10": level_summary[-1], "original_rows_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
