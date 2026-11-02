"""Encrypt the validated generic BND using ER's published CBC container format.

Keeps the original binder version; no version marker is downgraded or falsified.
Only accepts project-local inputs and outputs.
"""
from pathlib import Path
import shutil
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[1]
KEY = bytes.fromhex("99BFFC366A6BC8C6F5827D093602D676C42892A01C207FB024D3AF4E493FEF99")


def decrypt(data):
    dec = Cipher(algorithms.AES(KEY), modes.CBC(data[:16])).decryptor()
    return dec.update(data[16:]) + dec.finalize()


def main():
    source = ROOT / "work" / "melina-build" / "melina_param.bnd.dcx"
    output = ROOT / "build" / "melina_ashes" / "mod" / "regulation.bin"
    assert source.resolve().is_relative_to(ROOT) and output.resolve().is_relative_to(ROOT)
    original = ROOT / "work" / "vanilla" / "regulation.bin"
    assert decrypt(original.read_bytes()).startswith(b"DCX\0"), "Cipher must match the original format"
    plain = source.read_bytes()
    assert plain.startswith(b"DCX\0")
    iv = bytes(16)
    padded = plain + bytes((-len(plain)) % 16)
    enc = Cipher(algorithms.AES(KEY), modes.CBC(iv)).encryptor()
    encrypted = iv + enc.update(padded) + enc.finalize()
    assert decrypt(encrypted)[:len(plain)] == plain
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encrypted)
    check_dir = ROOT / "work" / "melina-roundtrip"
    check_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output, check_dir / "regulation.bin")
    print(f"Created encrypted regulation copy ({len(encrypted)} bytes), round-trip cipher verified.")


if __name__ == "__main__":
    main()
