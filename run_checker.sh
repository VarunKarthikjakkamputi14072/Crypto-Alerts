#!/bin/bash
cd /Users/varunkarthikjakkamputi/Documents/Crypto\ -\ Alert/crypto-alert
source ../crypto-alert-env/bin/activate
export $(grep -v '^#' .env | xargs)
python3 main.py >> alerts.log 2>&1

