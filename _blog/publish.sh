#!/bin/zsh
# Build, commit, push to GitHub Pages, wait until the new URLs are live, then
# notify Bing/IndexNow. Usage: _blog/publish.sh "Commit message" [slug ...]
set -euo pipefail
cd "$(dirname "$0")/.."

msg=${1:?commit message required}
shift
slugs=("$@")

python3 _blog/build.py --check

git add -A
if git diff --cached --quiet; then
  echo "Nothing to commit."
else
  git commit -q -m "$msg"
fi
git push -q origin main

urls=("https://reb00t.app/blog/" "https://reb00t.app/sitemap.xml")
for s in "${slugs[@]}"; do urls+=("https://reb00t.app/blog/$s/"); done

# Wait for GitHub Pages to finish building the commit we just pushed (usually 30-90s).
head=$(git rev-parse HEAD)
for i in {1..40}; do
  build=$(gh api repos/rewiredrising/reb00t-legal/pages/builds/latest --jq '.status+" "+.commit' 2>/dev/null || true)
  [[ $build == "built $head" ]] && break
  [[ $build == errored* ]] && { echo "Pages build errored: $build"; exit 1; }
  sleep 8
done
echo "Pages: $build"
[[ $build == "built $head" ]] || { echo "Pages did not finish building $head"; exit 1; }

for s in "${slugs[@]}"; do
  u="https://reb00t.app/blog/$s/"
  for i in {1..30}; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$u?cb=$RANDOM")
    [[ $code == 200 ]] && break
    sleep 10
  done
  echo "$u -> $code"
  [[ $code == 200 ]] || { echo "NOT LIVE after 5 min: $u"; exit 1; }
done

key=$(cat _blog/indexnow-key)
json=$(python3 -c 'import json,sys; print(json.dumps({"host":"reb00t.app","key":sys.argv[1],"keyLocation":f"https://reb00t.app/{sys.argv[1]}.txt","urlList":sys.argv[2:]}))' "$key" "${urls[@]}")
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" -d "$json")
echo "IndexNow -> $code (200/202 = accepted)"
