#!/bin/bash
# Stage the public release of the flybrain project - evidence-package tier:
# the analysis scripts, the ledgers every number in the paper is re-derived from,
# and the deposited paper PDFs.
#
#   ./make_public_repo.sh            stage + commit (staging tree: ~/flybrain-public)
#   git -C ~/flybrain-public push    publish, once the remote repo exists
#
# Deliberate exclusions: the substrate implementation (evolution kernel, agent loop, task
# battery), malecns_graph.npz (90 MB), per-fly checkpoints (127-150 MB each), venv, and the
# 19 app-line ablation arms.
#
# Scrub policy: staged COPIES only - the working trees keep their real values, so no running
# job is affected. Ledgers are scanned and never rewritten: a ledger byte is evidence, so a
# ledger carrying a live key stops the release instead of being edited.
set -euo pipefail

SRC="$HOME/flybrain"
B195="$HOME/flybrain_195_data/flybrain"
PDF="$HOME/Downloads/flybrain-paper"
STAGE="$HOME/flybrain-public"

rm -rf "$STAGE"
mkdir -p "$STAGE/code" "$STAGE/data/mac/ctrl" "$STAGE/data/mac/apps" "$STAGE/data/195" "$STAGE/paper"

# ---------------- code: analysis + paper builder + graph provenance ----------------
cp "$SRC"/analyze_*.py "$STAGE/code/"
cp "$SRC"/paper_draft_v5.py "$SRC"/paper_draft_v5_zh.py "$STAGE/code/"
cp "$SRC"/build_graph.py "$STAGE/code/"
cp "$SRC"/make_public_repo.sh "$STAGE/code/"

# ---------------- ledgers: Mac-run experiment line ----------------
cp "$SRC/evolve_desire_select.json" "$SRC/evolve_desire_random.json" "$STAGE/data/mac/"
cp "$SRC"/ctrl/ctrl_*_evolve_desire_*.json "$STAGE/data/mac/ctrl/"
cp "$SRC"/ctrl/*_s11.log "$STAGE/data/mac/ctrl/" 2>/dev/null || true
cp -R "$SRC/apps/harvest" "$STAGE/data/mac/apps/harvest"
find "$STAGE/data/mac/apps/harvest" -name '*.npz' -delete
# The per-fly solution stores ship separately: no number in the paper is derived from them,
# and they quote a lab host on the LAN. The ledgers the paper DOES read ship byte-identical.
STORES=$(find "$STAGE/data/mac/apps/harvest" -name '*_store.json' -print -delete | wc -l | tr -d ' ')
echo "solution stores held back: $STORES"

# ---------------- ledgers: the 195 mirror ----------------
for f in cereb_llm5_s13_g40.json economy.json archA0.json archA0c.json archA1.json archA1c.json \
         archSkill.json evo_teach.json evo_teach2.json evo_t1_teach.json; do
  cp "$B195/$f" "$STAGE/data/195/"
done
cp "$B195"/harness_live_w2_g*.json "$STAGE/data/195/"

# ---------------- paper ----------------
cp "$PDF"/*.pdf "$STAGE/paper/" 2>/dev/null || true

# ---------------- README + LICENSE ----------------
cd "$STAGE"
cp "$SRC/README_public.md" README.md
cp "$SRC/LICENSE" LICENSE

# ---------------- scrub code copies ----------------
find "$STAGE/code" -type f \( -name '*.py' -o -name '*.sh' \) -print0 |
  xargs -0 sed -i '' -E \
    -e 's/sk-[A-Za-z0-9]{20,}/<REDACTED_KEY>/g' \
    -e 's/gh[pousr]_[A-Za-z0-9]{20,}/<REDACTED_TOKEN>/g' \
    -e 's/(Bearer )[A-Za-z0-9_.\-]{12,}/\1<REDACTED_TOKEN>/g' \
    -e 's/192\.168\.1\.[0-9]{1,3}/<LAN_HOST>/g' \
    -e 's/connect\.west[a-z]*\.seetacloud\.com/<CLOUD_HOST>/g' \
    -e 's/bk6CCvZNvn3X/<REDACTED_PASSWORD>/g' \
    -e 's#/srv/fast/flybrain#<DATA_ROOT>#g'

# ---------------- ledgers are scanned, never rewritten ----------------
LEDGER_HITS=$(grep -rlE 'sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}' "$STAGE/data" 2>/dev/null | wc -l | tr -d ' ' || true)
echo "ledgers held back by the secret scan: $LEDGER_HITS"
if [ "$LEDGER_HITS" != "0" ]; then
  grep -rlE 'sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}' "$STAGE/data"
  echo "refusing to publish: a ledger carries a live key - decide before committing" >&2
  exit 1
fi

# ---------------- repoint the paper builder at the repository layout ----------------
python3 - "$STAGE" <<'PY'
import os, re, sys
stage = sys.argv[1]
head = 'REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n'
OUTD = (r'^OUTD = os\.path\.expanduser\("~/Downloads/flybrain-paper"\)$',
        'OUTD = os.path.join(REPO, "paper", "figures")')
subs = {
    "paper_draft_v5.py": [
        (r'^BASE = os\.path\.expanduser\("~/flybrain"\)$',
         'BASE = os.path.join(REPO, "data", "mac")'),
        (r'^CTRLO = os\.path\.expanduser\("~/flybrain/ctrl"\)$',
         'CTRLO = os.path.join(REPO, "data", "mac", "ctrl")'),
        (r'^B195 = os\.path\.expanduser\("~/flybrain_195_data/flybrain"\)$',
         'B195 = os.path.join(REPO, "data", "195")'),
        OUTD,
    ],
    # the Chinese edition exec's the English data section, so it only carries OUTD
    "paper_draft_v5_zh.py": [OUTD],
}
for name in ("paper_draft_v5.py", "paper_draft_v5_zh.py"):
    path = os.path.join(stage, "code", name)
    text = open(path).read()
    for pat, rep in subs[name]:
        text, n = re.subn(pat, rep, text, flags=re.M)
        if n != 1:
            sys.exit(f"{name}: pattern {pat} matched {n} times, expected 1")
    text = text.replace('open(os.path.expanduser("~/flybrain/paper_draft_v5.py"))',
                        'open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_draft_v5.py"))')
    if "REPO = os.path.dirname" not in text:
        lines = text.split("\n")
        i = next(k for k, l in enumerate(lines) if l.startswith(("BASE = os.path.join(REPO", "OUTD = os.path.join(REPO")))
        lines.insert(i, head.rstrip("\n"))
        text = "\n".join(lines)
    os.makedirs(os.path.join(stage, "paper", "figures"), exist_ok=True)
    open(path, "w").write(text)
    print("repointed", name)
PY

# ---------------- git ----------------
cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.venv/
venv/
*.npz
*.safetensors
paper/figures/
EOF
git init -q -b main
git add -A
git -c user.name="Boxiang Luan" -c user.email="Mcking1983@users.noreply.github.com" \
  commit -q -m "flybrain evidence package: analysis code, ledgers, deposited paper

Every figure and table in paper/ is re-derivable from data/ by code/paper_draft_v5.py.
Preprint: DOI 10.5281/zenodo.23396756"
echo "staged $(find "$STAGE" -type f -not -path '*/.git/*' | wc -l | tr -d ' ') files, $(du -sh "$STAGE" | cut -f1)"
