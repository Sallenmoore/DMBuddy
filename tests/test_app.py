from autonomous import log
from tasks import mocktask, npcgentask
import time
from celery.result import AsyncResult
import pytest


def test_npcgen_task(app):
    task = npcgentask.delay()
    result = AsyncResult(task.id)
    log(result.status)
    result.ready()
    assert "name" in result.get()
    assert "backstory" in result.get()
