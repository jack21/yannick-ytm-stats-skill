#!/usr/bin/env bash
# 此檔保留為向後相容 wrapper。實際邏輯已遷移到 scan.py（純 Python 標準函式庫實作）。
# 直接執行 `python3 scan.py` 與本檔效果相同。
exec python3 "$(dirname "$0")/scan.py" "$@"
