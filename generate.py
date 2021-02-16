import json
from pathlib import Path

INDEX = Path("index.json")
GENERATED = Path("generated/generated.json")

index = json.loads(INDEX.read_text(encoding="utf-8"))
generated = {}
for week in index:
    variants = {}
    path = Path(str(week['number']))
    for name in week['variants']:
        filename = name.lower().replace(" ", "-")
        variant_path = path.joinpath(filename).with_suffix(".json")
        print(f"Loading from {variant_path}")
        variants[name] = json.loads(variant_path.read_text(encoding="utf-8"))
    week['variants'] = variants
    week['variantNames'] = list(variants.keys())

GENERATED.write_text(json.dumps(index, ensure_ascii=False))
