#!/bin/bash
set -e

BASE_DIR="/Users/dantrinh0_0/PycharmProjects/Python"

cd "$BASE_DIR" || exit 1

# activate venv
source "$BASE_DIR/.venv/bin/activate"

echo "===== START PIPELINE $(date) ====="


# 1. Crawl TopDev
python3 -m src.crawls.crawl_data_top_dev

# 2. Run pipeline
python3 main.py

echo "===== DONE PIPELINE $(date) ====="
