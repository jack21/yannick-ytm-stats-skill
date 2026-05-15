#!/usr/bin/env bash
# 把整個 repo 打包成 .skill 檔（其實就是 zip）。
# 用法：
#   ./scripts/package.sh              # 產出 dist/yannick-ytm-stats-skill.skill
#   ./scripts/package.sh out.skill    # 指定輸出檔名
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

OUTPUT="${1:-dist/yannick-ytm-stats-skill.skill}"
mkdir -p "$(dirname "$OUTPUT")"
rm -f "$OUTPUT"

# 刻意排除非 runtime 的檔案：dist 自己、範例、CI、開發說明、git 中繼資料
zip -r "$OUTPUT" . \
  -x "dist/*" \
     "examples/*" \
     ".github/*" \
     ".git/*" \
     "tests/*" \
     "README.md" \
     "CLAUDE.md" \
     "CONTRIBUTING.md" \
     "CHANGELOG.md" \
     "LICENSE" \
     ".gitignore" \
     "*.pyc" \
     "__pycache__/*" \
     ".DS_Store"

echo ""
echo "✅ 打包完成：$OUTPUT"
ls -lh "$OUTPUT"
