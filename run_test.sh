#!/usr/bin/env bash

coverage run src/bot.py -t &

sleep 5s

python src/tests/test_basic.py -c "$Channel_ID" --run all "$Target_ID" "$Tester"


coverage report
