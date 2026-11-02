"""Add Chinese item names/descriptions without changing any original text entry."""
from pathlib import Path
import json
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BINDER_STEMS = ["item", "item_dlc01", "item_dlc02"]
TEXT_NAMES = ["GoodsName", "GoodsInfo", "GoodsInfo2", "GoodsCaption"]
SOURCE_ROOT = ROOT / "work" / "resources-vanilla" / "msg" / "zhocn"
BUILD_ROOT = ROOT / "work" / "melina-msg"
CAPTION = """寄宿着旅伴记忆的骨灰。
能召唤梅琳娜的灵魂。

身披旅行装束的少女，
以短刀与黄金的祈祷协助战斗。

她曾与褪色者订下约定，
在通往黄金树的漫长路途上，
陪伴那仍未停下的脚步。"""


def build_binder(stem):
    source = SOURCE_ROOT / f"{stem}-msgbnd-dcx"
    build = BUILD_ROOT / f"{stem}-msgbnd-dcx"
    assert build.resolve().is_relative_to(ROOT)
    shutil.copytree(source, build, dirs_exist_ok=True)
    translate = str.maketrans("0123456789", "０１２３４５６７８９")
    for name in TEXT_NAMES:
        tree = ET.parse(build / f"{name}.fmg.xml")
        entries = tree.getroot().find("entries")
        old = {int(e.get("id")): e.text for e in entries}
        for level in range(11):
            ident = 280000 + level
            assert ident not in old
            if name == "GoodsName":
                text = "梅琳娜的骨灰" + ("＋" + str(level).translate(translate) if level else "")
            elif name == "GoodsInfo":
                text = "能召唤梅琳娜的灵魂"
            elif name == "GoodsInfo2":
                # Vanilla spirit health-bar names omit the upgrade suffix here.
                text = "梅琳娜"
            else:
                text = CAPTION
            ET.SubElement(entries, "text", {"id": str(ident)}).text = text
        entries[:] = sorted(entries, key=lambda e: int(e.get("id")))
        assert all(e.text == old[int(e.get("id"))] for e in entries if int(e.get("id")) in old)
        tree.write(build / f"{name}.fmg.xml", encoding="utf-8", xml_declaration=True)
    return {"binder": f"{stem}.msgbnd.dcx", "added_entries": 11 * len(TEXT_NAMES), "original_entries_unchanged": True}


def main():
    # Current ER reads the DLC02 container. Each container includes its own
    # base GoodsName/Info/Caption FMGs, so patching item.msgbnd alone is insufficient.
    result = [build_binder(stem) for stem in BINDER_STEMS]
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
