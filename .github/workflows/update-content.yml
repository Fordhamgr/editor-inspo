name: Update Content

on:
  schedule:
    - cron: '0 6 * * *'   # runs at 6 AM UTC every day
  workflow_dispatch:       # lets you run it manually

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install feedparser
      - name: Run aggregator
        run: python aggregator.py
      - name: Commit and push if changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add content.json
          git diff --quiet && git diff --staged --quiet || git commit -m "Update content"
          git push
