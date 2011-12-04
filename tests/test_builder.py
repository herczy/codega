from unittest import TestCase

from codega.builder.base import TaskBase, phase
from codega.builder.builder import Builder
from codega.decorators import get_mark

class TestBuild(TestCase):
    def test_phase(self):
        @phase('a', depends = ('b', 'c'))
        def x():
            pass

        self.assertEqual(get_mark(x, 'task_phase'), ('a', ('b', 'c')))

    def test_task_base(self):
        okay = set()
        class TestTask(TaskBase):
            @phase('a')
            def phase_a(self, jid, force):
                okay.add(self.phase_a)

            @phase('b', depends = ('a',))
            def phase_b(self, jid, force):
                okay.add(self.phase_b)

        task = TestTask(None)

        self.assertEqual(set(task.list_supported_phases()), set(['a', 'b']))

        task.build('a')
        self.assertEqual(okay, set([task.phase_a]))
        okay = set()

        task.build('b')
        self.assertEqual(okay, set([task.phase_a, task.phase_b]))
        okay = set()

        task.build('b', skip = ['a'])
        self.assertEqual(okay, set([task.phase_b]))
        okay = set()

    def test_builder(self):
        okay = set()
        class TestTask(TaskBase):
            value = 0

            @phase('a')
            def phase_a(self, jid, force):
                okay.add(self)

        builder = Builder()
        expected = set()
        for i in xrange(100):
            task = TestTask(None)
            task.value = i
            expected.add(task)
            builder.push_task(task)

        builder.build('a')
        self.assertEqual(okay, expected)
