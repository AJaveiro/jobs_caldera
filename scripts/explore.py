import json
from pprint import pprint 

with open("data/candidates.jsonl", "r", encoding="utf-8") as f:
    first = json.loads(next(f))

pprint(first, depth=3)
