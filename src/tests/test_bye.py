import os
import sys

from distest import TestCollector
from distest import run_dtest_bot

TESTER = os.getenv('Tester')
# The tests themselves

test_collector = TestCollector()
created_channel = None

@test_collector()
async def test_shutdown(interface):
    await interface.send_message("./bye")
    await interface.get_delayed_reply(3, interface.assert_message_contains, "Shutting Down")





# Actually run the bot
if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
