#!/usr/bin/env bash

coverage run src/bot.py -t &

sleep 5s

python src/tests/test_basic.py -c "$Channel_ID" --run all "$Target_ID" "$Tester"
python src/tests/test_sql.py -c "$Channel_ID" --run all "$Target_ID" "$Tester"

#test_bye should always be last test
python src/tests/test_bye.py -c "$Channel_ID" --run all "$Target_ID" "$Tester"

sleep 10s

