import sys

from app.models.maze import Model

from autonomous import log


class TestApp:
    def test_model(self):
        m = Model(name="test")
        m.save()
        log(m.pk)
        assert m.pk
