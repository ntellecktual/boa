"""Extract original IIFE inner content from nfl_draft.html before it's overwritten."""
path = r'boaapp\templates\boaapp\nfl_draft.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# IIFE opens at line 740 (index 739), inner content is 741..last-3
# Find the exact boundaries dynamically
iife_start = None
iife_end = None
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == "(function(){'use strict';" and iife_start is None:
        iife_start = i + 1  # first line INSIDE the IIFE
    if stripped == '})();' and iife_start is not None:
        iife_end = i       # stop before this line
        break

inner = lines[iife_start:iife_end]
with open('nfl_orig_inner.tmp', 'w', encoding='utf-8') as f:
    f.writelines(inner)

print(f"Saved {len(inner)} lines ({iife_start+1}..{iife_end}) to nfl_orig_inner.tmp")
