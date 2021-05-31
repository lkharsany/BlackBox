import sys

import discord
from distest import TestCollector
from distest import run_dtest_bot
import os

TESTER = os.getenv('Tester')
# The tests themselves

test_collector = TestCollector()
created_channel = None

@test_collector()
async def test_add_reaction(interface):
    await interface.add_reaction("👍")
    await interface.get_delayed_reply(2, interface.assert_message_equals, 'Reaction has been added to message')

@test_collector()
async def test_remove_reaction(interface):
    await interface.remove_reaction("👍")
    await interface.get_delayed_reply(2, interface.assert_message_equals, 'Reaction has been removed from message')


if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)