import sys
from distest import TestCollector
from distest import run_dtest_bot
from dotenv import load_dotenv
import os

load_dotenv()

TESTER = os.getenv('Tester')
# The tests themselves

test_collector = TestCollector()
created_channel = None


@test_collector()
async def test_scrum(interface):
    response = await interface.assert_reply_contains("./Scrum", "Master")
    assert response.content == "Master"


@test_collector()
async def test_cool(interface):
    response = await interface.assert_reply_contains("./CoolBot", "This bot is cool. :)")
    assert response.content == "This bot is cool. :)"


@test_collector()
async def test_ping(interface):
    response = await interface.assert_reply_contains("ping", "Pong!")
    assert response.content == "Pong!"


@test_collector()
async def test_cheers(interface):
    response = await interface.assert_reply_contains("hi", "Hello there")
    assert response.content == "Hello there"


# Actually run the bot

if __name__ == "__main__":
    run_dtest_bot(sys.argv, test_collector)
