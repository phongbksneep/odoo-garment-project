#!/usr/bin/env python3
"""Find untranslated Vietnamese strings."""
import re
import sys
sys.path.insert(0, '/Users/mac/Documents/projectFree/odoo-garment-project')

# Read the translations dict from generate_en_po.py
with open('/Users/mac/Documents/projectFree/odoo-garment-project/generate_en_po.py') as f:
    src = f.read()
# Extract just the TRANSLATIONS dict
start = src.index('TRANSLATIONS = {')
end = src.index('\n}', start) + 2
exec(src[start:end])

with open('/tmp/all_vi.txt') as f:
    all_vi = [l.strip() for l in f if l.strip()]

untranslated = []
for s in all_vi:
    stripped = re.sub(r'^[^\w\s<(]+\s*', '', s)
    if s not in TRANSLATIONS and stripped not in TRANSLATIONS:
        untranslated.append(s)

for s in sorted(untranslated):
    print(s)
