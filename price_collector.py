name: Daily Batch Collector

on:
  schedule:
    - cron: '0 19 * * *'   # 매일 UTC 19:00 실행 (한국시간 새벽 4시)
  workflow_dispatch:        # 필요시 수동 실행도 가능

jobs:
  run-batch:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run price_collector.py
        run: |
          python price_collector.py

      - name: Commit & push generated JSON
        run: |
          git config --global user.name 'github-actions'
          git config --global user.email 'actions@github.com'
          git add daily_buytable_*.json
          git commit -m "📊 Daily buytable update" || echo "No changes to commit"
          git push