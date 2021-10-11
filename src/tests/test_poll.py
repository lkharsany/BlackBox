import sys

import discord
from distest import TestCollector
from distest import run_dtest_bot
from discord import Embed
import os

TESTER = os.getenv('Tester')
test_collector = TestCollector()
created_channel = None

@test_collector()
async def test_poll(interface):
    message = './poll "does the poll test work?" yes no'
    reactions = ['✅', '❌']
    options = ['yes','no']

    description = []
    for x, option in enumerate(options):
        description += '\n{} {}'.format(reactions[x], option)
    embed = Embed(title='does the poll test work?', description=''.join(description))

    await interface.assert_reply_embed_equals(message,embed)



# Actually run the bot
if __name__ == "__main__":
     run_dtest_bot(sys.argv, test_collector)
