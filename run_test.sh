#!/usr/bin/env bash

python src/bot.py -t &

sleep 5s

coverage run -m src/tests/test_basic -c "$Channel_ID" --run all "$Target_ID" "$Tester"
