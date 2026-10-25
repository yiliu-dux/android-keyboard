#!/usr/bin/env python3
"""
Packs rime-ice (https://github.com/iDvel/rime-ice) into a Chinese dictionary zip that FUTO Keyboard
can import (same format as the existing "Luna Pinyin" dictionary).

The bundled librime has no Lua plugin, so the Lua-free schemas from rime-ice's others/no_lua_schema
are used. An existing dictionary zip is used as a base so that Traditional (luna_pinyin), stroke
input, the OpenCC tables and the PYJJ/ST double pinyin schemes keep working; rime-ice is overlaid.

Usage:
    python tools/pack_rime_ice.py --rime-ice ../rime-ice --base ../zidian-v26.02.dict --out rime-ice-zh.zip
"""
import argparse
import datetime
import re
import sys
import zipfile
from pathlib import Path

# Schemas the app can select (see ChineseIME.kt) that rime-ice provides a Lua-free version of
RIME_ICE_DOUBLE_PINYIN = ["double_pinyin", "double_pinyin_abc", "double_pinyin_flypy", "double_pinyin_mspy"]

# Schemas listed in default.yaml: every schema needs to be listed, or it will not be compiled
SCHEMA_LIST = [
    "rime_ice",
    "luna_pinyin", "luna_pinyin_simp", "stroke",
    *RIME_ICE_DOUBLE_PINYIN,
    "double_pinyin_pyjj", "double_pinyin_st",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rime-ice", required=True, type=Path, help="path to a clone of rime-ice")
    ap.add_argument("--base", required=True, type=Path, help="existing FUTO Chinese dictionary zip")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--include-tencent", action="store_true",
                    help="include the very large tencent word list (slow to compile on the phone)")
    ap.add_argument("--name", help="dictionary name shown in the app (default: 'Rime Ice <date>')")
    args = ap.parse_args()

    ice: Path = args.rime_ice
    no_lua = ice / "others" / "no_lua_schema"
    for p in (ice / "rime_ice.dict.yaml", no_lua / "rime_ice.schema.yaml", args.base):
        if not p.exists():
            sys.exit(f"Missing {p}")

    files: dict[str, bytes] = {}

    # Base dictionary (luna pinyin, stroke, opencc, ...)
    with zipfile.ZipFile(args.base) as z:
        for info in z.infolist():
            if not info.is_dir():
                files[info.filename] = z.read(info)
    for meta in ("FUTOKeyboard_ChineseDictionary_Name", "FUTOKeyboard_ChineseDictionary_Version"):
        files.pop(meta, None)

    def add(rel: str, src: Path):
        files[rel] = src.read_bytes()

    # Schemas. The misspelling rules (自动纠错, up to the end of speller/algebra) are moved to
    # rime_ice.correction.txt, which ChineseIME.kt appends back only when the user enables them
    schema = (no_lua / "rime_ice.schema.yaml").read_text(encoding="utf-8")
    start = schema.find("    ### 自动纠错\n")
    if start < 0:
        sys.exit("Could not locate the 自动纠错 rules in rime_ice.schema.yaml")
    end = re.compile(r"^[^\s#]", re.M).search(schema, start)
    end = end.start() if end else len(schema)
    rules = re.findall(r"^\s+- (\S+)", schema[start:end], flags=re.M)
    files["rime_ice.schema.yaml"] = (schema[:start] + schema[end:]).encode("utf-8")
    files["rime_ice.correction.txt"] = "".join(f"{r}\n" for r in rules).encode("utf-8")
    for s in RIME_ICE_DOUBLE_PINYIN:
        add(f"{s}.schema.yaml", no_lua / f"{s}.schema.yaml")
    for f in ("melt_eng.schema.yaml", "melt_eng.dict.yaml", "radical_pinyin.schema.yaml",
              "radical_pinyin.dict.yaml", "symbols_v.yaml", "symbols_caps_v.yaml", "custom_phrase.txt"):
        add(f, ice / f)

    # Dictionaries
    dict_text = (ice / "rime_ice.dict.yaml").read_text(encoding="utf-8")
    cn = ["8105", "base", "ext", "others"] + (["tencent"] if args.include_tencent else [])
    if not args.include_tencent:
        dict_text = re.sub(r"^(\s*)- cn_dicts/tencent\b", r"\1# - cn_dicts/tencent", dict_text, flags=re.M)
    files["rime_ice.dict.yaml"] = dict_text.encode("utf-8")
    for n in cn:
        add(f"cn_dicts/{n}.dict.yaml", ice / "cn_dicts" / f"{n}.dict.yaml")
    for p in sorted((ice / "en_dicts").iterdir()):
        add(f"en_dicts/{p.name}", p)

    # OpenCC (emoji). The base already provides the s2t/t2s tables
    for n in ("emoji.json", "emoji.txt", "others.txt"):
        add(f"opencc/{n}", ice / "opencc" / n)

    # default.yaml: rime-ice's, with the schema list replaced to match what is actually shipped
    default = (ice / "default.yaml").read_text(encoding="utf-8")
    block = "schema_list:\n" + "".join(f"  - schema: {s}\n" for s in SCHEMA_LIST) + "\n\n"
    default, n = re.subn(r"^schema_list:\n(?:[ \t]+.*\n|#.*\n)*?(?=\n*^\S)", block, default, count=1, flags=re.M)
    if n != 1:
        sys.exit("Could not locate schema_list in default.yaml")
    files["default.yaml"] = default.encode("utf-8")

    # Check that every listed schema exists
    for s in SCHEMA_LIST:
        if f"{s}.schema.yaml" not in files:
            sys.exit(f"Schema {s} is listed but missing from the package")

    name = args.name or f"Rime Ice {datetime.date.today().isoformat()}"
    files["FUTOKeyboard_ChineseDictionary_Name"] = (name + "\n").encode("utf-8")
    files["FUTOKeyboard_ChineseDictionary_Version"] = b"1\n"
    files["README.md"] = (
        b"Rime Ice (https://github.com/iDvel/rime-ice, GPL-3.0) packaged for FUTO Keyboard, "
        b"with Luna Pinyin / stroke / OpenCC data from the base dictionary.\n"
        b"Lua-free schemas are used. All copyrights belong to their respective authors.\n")
    files["LICENSE.rime-ice"] = (ice / "LICENSE").read_bytes()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, data in sorted(files.items()):
            z.writestr(rel, data)

    print(f"Wrote {args.out} ({args.out.stat().st_size / 1e6:.1f} MB, {len(files)} files) as '{name}'")


if __name__ == "__main__":
    main()
