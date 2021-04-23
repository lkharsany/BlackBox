import sys
from distest import TestCollector
from distest import run_dtest_bot
import os
from time import sleep

TESTER = os.getenv('Tester')
# The tests themselves

test_collector = TestCollector()
created_channel = None

@test_collector()
async def test_shutdown(interface):
    sleep(1)
    await interface.assert_reply_equals("./bye", 'Shutting Down')




# Actually run the bot
if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
