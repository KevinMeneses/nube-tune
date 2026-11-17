"""Busca identificadores que solo difieren en mayúsculas (EEL2 no las distingue: serían la misma variable)."""
import re, sys, pathlib, collections
src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "nube_tune.jsfx").read_text()
code = "\n".join(l for l in src.splitlines() if not l.startswith(("slider", "desc:", "//", "in_pin", "out_pin")))
code = re.sub(r'"[^"]*"', '""', code)            # sin strings
code = re.sub(r"//.*", "", code)
ids = collections.defaultdict(set)
for m in re.finditer(r"(?<![\w#$.'])[A-Za-z_]\w*", code):
    ids[m.group().lower()].add(m.group())
bad = {k: v for k, v in ids.items() if len(v) > 1}
for k, v in sorted(bad.items()): print("CHOQUE:", ", ".join(sorted(v)))
sys.exit(1 if bad else 0)
