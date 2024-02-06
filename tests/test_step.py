from gevent import time
import unittest
from python_workflow import Task, Step


class TestStep(unittest.TestCase):
    def test_start_many_threads(self):
        class MyTask1(Task):
            def __init__(self, delay):
                super().__init__('my_task_1')
                self.delay = delay

            def run(self):
                time.sleep(self.delay)
                return 'It works 1!'

        class MyTask2(Task):
            def __init__(self, delay):
                super().__init__('my_task_2')
                self.delay = delay

            def run(self):
                time.sleep(self.delay)
                return 'It works 2!'

        step = Step(
            'my_step',
            tasks=[
                MyTask1(1),
                MyTask1(1),
                MyTask2(2),
            ],
            nb_thread=8
        )
        step.start()

        self.assertEqual(step.name, 'my_step')
        self.assertEqual(
            step.value,
            {
                'my_task_1-0': 'It works 1!',
                'my_task_1-1': 'It works 1!',
                'my_task_2-2': 'It works 2!'
            }
        )
        task = step.tasks[0]
        self.assertEqual(round(task.duration), 1)
        task = step.tasks[1]
        self.assertEqual(round(task.duration), 1)
        task = step.tasks[2]
        self.assertEqual(round(task.duration), 2)
        self.assertEqual(round(step.duration), 2)

    def test_start_1_thread(self):
        class MyTask1(Task):
            def __init__(self, delay):
                super().__init__('my_task_1')
                self.delay = delay

            def run(self):
                time.sleep(self.delay)
                return 'It works 1!'

        class MyTask2(Task):
            def __init__(self, delay):
                super().__init__('my_task_2')
                self.delay = delay

            def run(self):
                time.sleep(self.delay)
                return 'It works 2!'

        step = Step(
            'my_step',
            tasks=[
                MyTask1(1),
                MyTask1(1),
                MyTask2(2),
            ],
            nb_thread=1
        )
        step.start()

        task = step.tasks[0]
        self.assertEqual(round(task.duration), 1)
        task = step.tasks[1]
        self.assertEqual(round(task.duration), 1)
        task = step.tasks[2]
        self.assertEqual(round(task.duration), 2)
        self.assertEqual(round(step.duration), 4)

    def test_start_raise_errors(self):
        class MyTask1(Task):
            def __init__(self):
                super().__init__('my_task_1')

            def run(self):
                raise Exception('Error')

        class MyTask2(Task):
            def __init__(self, *args, **kwargs):
                super().__init__('my_task_2', *args, **kwargs)

            def run(self):
                return 'It works 2!'

        class CustomStep(Step):
            def on_error(self, *args, **kwargs):
                pass

        step = CustomStep(
            'my_step',
            tasks=[
                MyTask1(),
                MyTask1(),
                MyTask2(),
            ],
            raise_error=False
        )
        step.start()
        self.assertEqual(
            step.value,
            {
                'my_task_1-0': None,
                'my_task_1-1': None,
                'my_task_2-2': 'It works 2!'
            }
        )

        step = CustomStep(
            'my_step',
            tasks=[
                MyTask1(),
                MyTask1(),
                MyTask2(),
            ],
            raise_error=True
        )
        step.start()
        self.assertEqual(
            step.value,
            None
        )
