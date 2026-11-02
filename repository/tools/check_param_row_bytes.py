"""Verify that adding independent rows preserved every original row's bytes."""
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
NAMES = ["NpcParam", "NpcThinkParam", "BuddyParam", "EquipParamGoods", "SpEffectParam", "ShopLineupParam"]


def read_rows(path):
    data = path.read_bytes()
    assert data[0x2C] == 0, "Expected little-endian PC PARAM"
    flags = data[0x2D]
    count = struct.unpack_from("<H", data, 0x0A)[0]
    is_long = bool(flags & 4)
    expanded = is_long or bool(flags & 1 and flags & 2)
    start = 0x40 if expanded else 0x30
    width = 24 if is_long else 12
    pointers = []
    for i in range(count):
        pos = start + width * i
        ident = struct.unpack_from("<i", data, pos)[0]
        offset = struct.unpack_from("<q" if is_long else "<I", data, pos + (8 if is_long else 4))[0]
        pointers.append((ident, offset))
    assert len(pointers) >= 2
    size = pointers[1][1] - pointers[0][1]
    assert size > 0
    assert all(b[1] - a[1] == size for a, b in zip(pointers, pointers[1:]))
    return size, {i: data[offset:offset + size] for i, offset in pointers}


def main():
    result = {}
    for name in NAMES:
        old_size, old = read_rows(ROOT / "work" / "vanilla" / "regulation-bin" / f"{name}.param")
        new_size, new = read_rows(ROOT / "work" / "melina-build" / "regulation-bin" / f"{name}.param")
        assert old_size == new_size, (name, old_size, new_size)
        changed = [i for i, raw in old.items() if new.get(i) != raw]
        assert not changed, (name, "Original row bytes changed", changed[:12])
        result[name] = {"row_bytes": old_size, "original_rows_identical": len(old), "added_rows": len(new) - len(old)}
    out = ROOT / "build" / "melina_ashes" / "original-row-byte-verification.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
