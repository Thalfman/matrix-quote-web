#!/usr/bin/env bash
# Spin up a trimmed, dedicated demo repo at ../matrix-quote-web-demo/.
#
# Run this from inside a clone of matrix-quote-web, checked out on the
# claude/setup-demo-branch-qcep6 branch. Produces a sibling directory with
# only the files the Vercel demo needs, fresh-inits git, and leaves you
# ready to `git remote add origin` + `git push`.
#
# Usage:
#   git checkout claude/setup-demo-branch-qcep6
#   git lfs pull                      # critical: hydrate joblib bundles before copy
#   bash scripts/migrate_to_demo_repo.sh
set -euo pipefail

SRC="$(git rev-parse --show-toplevel)"
DEST="${SRC}/../matrix-quote-web-demo"

if [[ -e "$DEST" ]]; then
  echo "Destination already exists: $DEST"
  echo "Remove it first (rm -rf) or move it aside, then rerun."
  exit 1
fi

# Guard: joblib bundles must be hydrated (LFS pulled), not pointer stubs.
SAMPLE="$SRC/demo_assets/models/me10_actual_hours_v1.joblib"
if [[ ! -f "$SAMPLE" ]] || [[ "$(wc -c <"$SAMPLE")" -lt 100000 ]]; then
  echo "demo_assets/models/*.joblib looks like LFS pointer stubs."
  echo "Run: git lfs install && git lfs pull"
  exit 1
fi

echo "[migrate] copying source tree to $DEST"
cp -r "$SRC" "$DEST"

echo "[migrate] stripping backend-only files"
cd "$DEST"
rm -rf \
  backend tests docs data models \
  Dockerfile railway.json .dockerignore .env.example \
  requirements.txt pyproject.toml \
  .github .git \
  frontend/node_modules frontend/dist

# Restore docs/ — needed for Claude Code skills (design/, superpowers/)
cp -r "$SRC/docs" "$DEST/docs"

# Cache junk
find . \( -name __pycache__ -o -name .ruff_cache -o -name .pytest_cache \) -exec rm -rf {} + 2>/dev/null || true
find . -name '*.pyc' -delete 2>/dev/null || true

# Swap in the demo-focused README
if [[ -f DEMO_README.md ]]; then
  mv DEMO_README.md README.md
fi

# Drop this migration script itself — it doesn't belong in the new repo
rm -f scripts/migrate_to_demo_repo.sh

echo "[migrate] fresh git init (main branch)"
git init -b main -q
git lfs install --local >/dev/null
git add .
git commit -q -m "initial commit: Vercel demo fork of matrix-quote-web"

echo
echo "[migrate] done."
echo "  files committed: $(git ls-files | wc -l)"
echo "  total size:      $(du -sh . | awk '{print $1}')"
echo
echo "Next steps:"
echo "  1. Create an empty repo on GitHub named matrix-quote-web-demo (no README/license)."
echo "  2. cd $(basename "$DEST")"
echo "  3. git remote add origin git@github.com:<owner>/matrix-quote-web-demo.git"
echo "  4. git push -u origin main"
echo "  5. git lfs push origin main"
echo "  6. Import the new repo in Vercel; enable Git LFS; Production Branch = main."
