#!/bin/bash
cd /Users/sunny/crypto-alert
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
/Users/sunny/crypto-alert/.venv/bin/python main.py >> alerts.log 2>&1
