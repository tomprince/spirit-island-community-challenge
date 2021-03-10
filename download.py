import csv
import requests
import json
from pathlib import Path
from typing import Any, Dict


def format_json(value: Dict[Any, Any]) -> str:
    return (
        json.dumps(value, indent=2, separators=(",", ": "), ensure_ascii=False) + "\n"
    )


URL = "https://docs.google.com/spreadsheets/d/1hu4NUC_p6u5TkVBSVUE0o8ZV99LBt0m70CLTrxSKJEQ/export?format=csv&gid=0"  # noqa: E501

# fmt: off
HEADERS = ['URL', '#', 'Week', 'Date']
EXPANSION_HEADERS = ['Spirit 1', 'Aspect', 'Board', 'Spirit 2', 'Aspect', 'Board', 'Board Setup', 'Scenario', 'Adversary', 'Beg', 'Int', 'Adv', 'Expert (+ second adversary)', '', '', '', 'Notes']  # noqa: E501
BASE_HEADERS = ['Spirit 1', 'Board', 'Spirit 2', 'Board', 'Board Setup', 'Scenario', 'Adversary', 'Beg', 'Int', 'Adv', 'Expert (+ second adversary)', '', '', '', 'Notes']  # noqa: E501
# fmt: on

resp = requests.get(URL)
reader = csv.reader(resp.iter_lines(decode_unicode=True))
next(reader)  # "Load in Tabletop Simulator"
version_line = next(reader)
header_line = next(reader)

assert version_line[4] == "Expansion Content" and version_line[21] == "Base Game"
assert header_line == HEADERS + EXPANSION_HEADERS + BASE_HEADERS


def process_expansion(
    spirit_1,
    aspect_1,
    board_1,
    spirit_2,
    aspect_2,
    board_2,
    board_setup,
    scenario,
    adversary_1,
    beg_1,
    int_1,
    adv_1,
    exp_1,
    plus,
    adversary_2,
    exp_2,
    notes,
):
    if not spirit_1:
        return
    assert plus in ("", "+")
    return {
        "numPlayers": 2,
        "boardLayout": board_setup,
        "boards": [board_1, board_2],
        "extra_board": False,
        "adversary": adversary_1,
        "adversary2": "None",
        "adversaryLevel2": 0,
        "scenario": scenario or "None",
        # FIXME - order
        "spirits": {
            spirit_1: aspect_1,
            spirit_2: aspect_2,
        },
        "bnc": False,
        "je": False,
        "difficulties": {
            "Beginner": {"adversaryLevel": int(beg_1)},
            "Intermediate": {"adversaryLevel": int(int_1)},
            "Advanced": {"adversaryLevel": int(adv_1)},
            "Expert": {"adversaryLevel": int(exp_1)}
            if plus == ""
            else {
                "adversaryLevel": int(exp_1),
                "adversary2": adversary_2,
                "adversaryLevel2": int(exp_2),
            },
        },
    }


def process_base(
    spirit_1,
    board_1,
    spirit_2,
    board_2,
    board_setup,
    scenario,
    adversary_1,
    beg_1,
    int_1,
    adv_1,
    exp_1,
    plus,
    adversary_2,
    exp_2,
    notes,
):
    if not spirit_1:
        return
    assert plus in ("", "+")
    return {
        "numPlayers": 2,
        "boardLayout": board_setup,
        "boards": [board_1, board_2],
        "extra_board": False,
        "adversary": adversary_1,
        "adversary2": "None",
        "adversaryLevel2": 0,
        "scenario": scenario or "None",
        # FIXME - order
        "spirits": {
            spirit_1: "",
            spirit_2: "",
        },
        "bnc": False,
        "je": False,
        "difficulties": {
            "Beginner": {"adversaryLevel": int(beg_1)},
            "Intermediate": {"adversaryLevel": int(int_1)},
            "Advanced": {"adversaryLevel": int(adv_1)},
            "Expert": {"adversaryLevel": int(exp_1)}
            if plus == ""
            else {
                "adversaryLevel": int(exp_1),
                "adversary2": adversary_2,
                "adversaryLevel2": int(exp_2),
            },
        },
    }


index = []
for line in reader:
    url, number, week, date = line[:4]
    assert week == number
    expansion = process_expansion(*line[4:21])
    base = process_base(*line[21:40])
    variants = []
    path = Path(str(week))
    path.mkdir(exist_ok=True)
    if base:
        path.joinpath("base.json").write_text(format_json(base), encoding="utf-8")
        variants.append("Base")
    if expansion:
        path.joinpath("expansion.json").write_text(
            format_json(expansion), encoding="utf-8"
        )
        variants.append("Expansion")
    index.append(
        {
            "number": int(number),
            "date": date,
            "url": url,
            "variants": variants,
        }
    )

Path("index.json").write_text(format_json(index), encoding="utf-8")
