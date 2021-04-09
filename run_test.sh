#!/usr/bin/env bash

python src/bot.py -t &

sleep 5s

python src/tests/test_basic.py -c "$Channel_ID" --run all "$Target_ID" "$Tester"
coverage run -m src/tests/test_basic.py -c "$Channel_ID" --run all "$Target_ID" "$Tester"
