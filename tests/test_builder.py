from unittest import TestCase

import re
import os
import os.path
from lxml import etree

import codega

from codega.config import *
from codega.builder.base import TaskBase, job
from codega.builder.builder import Builder
from codega.decorators import get_mark

class TestBuild(TestCase):
    def test_job(self):
        @job('a', depends = ('b', 'c'))
        def x():
            pass

        self.assertEqual(get_mark(x, 'task_job'), ('a', ('b', 'c')))

    def test_task_base(self):
        okay = set()
        class TestTask(TaskBase):
            @job('a')
            def job_a(self, jid, force):
                okay.add(self.job_a)

            @job('b', depends = ('a',))
            def job_b(self, jid, force):
                okay.add(self.job_b)

        task = TestTask(None)

        self.assertEqual(set(task.list_supported_jobs()), set(['a', 'b']))

        task.build('a')
        self.assertEqual(okay, set([task.job_a]))
        okay = set()

        task.build('b')
        self.assertEqual(okay, set([task.job_a, task.job_b]))
        okay = set()

        task.build('b', skip = ['a'])
        self.assertEqual(okay, set([task.job_b]))
        okay = set()

    def test_builder(self):
        okay = set()
        class TestTask(TaskBase):
            value = 0

            @job('a')
            def job_a(self, jid, force):
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
