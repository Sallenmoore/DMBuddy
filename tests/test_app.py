import time

import pytest
from autonomous import log
from autonomous.tasks import AutoTasks
from models import Character

# def test_character_task(app):
#     runner = AutoTasks()
#     result = runner.task(npcgentask)
#     log(result.status)
#     while result.status != "finished":
#         log(result.status)
#         time.sleep(1)
#     log(result.status)
#     log(result.return_value)
#     npc = NPC(**result.return_value)
#     assert npc.name
#     assert npc.backstory
