import gevent.monkey
gevent.monkey.patch_thread()

import logging
import math
from datetime import datetime
from time import time
from gevent.pool import Pool

logger = logging.getLogger('python-workflow')


VERSION = (1, 0, 3)


def get_version():
    return ".".join(map(str, VERSION))


__version__ = get_version()


class Task:
    """

    :param name: The name of the task
    :type name: str

    :param start_at: time at the task is started
    :type start_at: float | None

    :param stop_at: time at the task is completed
    :type stop_at: float | None

    :param value: the value returns from the :func:`~python_workflow.Task.run`
    :type value: *

    :param _args: not used. It will be available from :func:`~python_workflow.Task.run`
    :type _args: list, optional

    :param _kwargs: not used. It will be available from :func:`~python_workflow.Task.run`
    :type _kwargs: dict, optional
    """
    def __init__(self, name=None, *args, **kwargs):
        """
        Create a threadable Task

        :param name: The name of the Task, useful for logging.
        """

        self._name = name
        self._start_at = None
        self._stop_at = None
        self._value = None
        self._args = args
        self._kwargs = kwargs

    def is_completed(self):
        """
        **Default** : ``False``

        Returns ``True`` when the Task is completed without any errors.

        :rtype: bool
        """
        return self._stop_at is not None

    def run(self):
        """
        | **This method must be overridden.**
        | Its content will be executed in a thread and the return will be caught by the :class:`~python_workflow.Step`.
        """

    def on_start(self):
        """
        | This method is called **before** calling :func:`~python_workflow.Task.run`. By default, it writes logs.
        | Mostly, I override it to send notifications to Slack or somewhere else.
        """
        message = '%s is starting ...' % (self.__class__.__name__)

        logger.debug(' [%s][%s] %s args=%s, kwargs=%s' % (
            datetime.now().isoformat(),
            str(self._name).ljust(30),
            message.ljust(50),
            self._args,
            self._kwargs
        ))

    def on_complete(self):
        """
        | This method is called **after** calling :func:`~python_workflow.Task.run`. By default, it writes logs.
        | Mostly, I override it to send notifications to Slack or somewhere else.
        """
        message = '%s completed (%ss.)' % (
            self.__class__.__name__,
            math.ceil(self.duration * 10000) / 10000
        )

        """ Must be implemented """
        logger.debug(' [%s][%s] %s args=%s, kwargs=%s' % (
            datetime.now().isoformat(),
            str(self._name).rjust(30),
            message.ljust(50),
            self._args,
            self._kwargs
        ))

    def on_error(self, *args, **kwargs):
        """
        Raise the first args.
        """
        raise args[0]

    def reset(self):
        """
        Restart timers to None. ``duration`` become ``0``
        """
        self._start_at = None
        self._stop_at = None

    def start(self):
        """
        Starts the task, initializes timers and writes logs.
        Catch :func:`~python_workflow.Task.run`. exceptions and throw them.

        :return: the value returned from :func:`~python_workflow.Task.run`
        :exception: :class:`~Exception`
        """
        if self._start_at is None:
            self._start_at = time()

        self.on_start()

        try:
            self._value = self.run()
        except Exception as e:
            self.on_error(e)

        self.stop()
        self.on_complete()
        return self._value

    def stop(self):
        """
        Stop the timers and return its value

        :rtype: :class:`float`
        """
        if self._stop_at is None:
            self._stop_at = time()
        return self._stop_at

    @property
    def duration(self):
        """
        **Default** : ``None``

        Return the duration of the Task when its completed.

        :rtype: :class:`float` or :class:`None`
        """
        if self._stop_at is not None and self._start_at is not None:
            return self._stop_at - self._start_at

    @property
    def name(self):
        return self._name

    @property
    def stop_at(self):
        return self._stop_at

    @property
    def start_at(self):
        return self._start_at

    @property
    def value(self):
        return self._value


class Step(Task):
    """

    :param tasks:
    :type tasks: Task[]

    :param nb_thread:
    :type nb_thread: float

    :param raise_error:
    :type raise_error: bool
    """

    gevent.hub.Hub.NOT_ERROR = (Exception,)

    def __init__(self, name=None, tasks=None, *args, **kwargs):
        """

        :param name: the name of the Step
        :type name: str

        :param tasks:
        :type tasks: Task[]

        :param args: not used. It will be available from :func:`~python_workflow.Task.run`
        :type args: list, optional

        :param kwargs: not used. It will be available from :func:`~python_workflow.Task.run`
        :type kwargs: dict, optional

        :param nb_thread: Number of threads running at the same time.
        :type nb_thread: float, default 4

        :param raise_error: Step should stop if one of task failed.
        :type raise_error: bool, default True

        """
        super().__init__(name, *args, **kwargs)

        if not isinstance(tasks, list):
            raise Exception('`tasks` must be a instance of List')

        for task in tasks:
            if not isinstance(task, Task):
                raise Exception('`task` must be a instance of Task')
        self.tasks = tasks
        self.nb_thread = kwargs.get('nb_thread', 4)
        self.raise_error = kwargs.get('raise_error', True)

    def run(self):
        """
        | The return will be caught by the :class:`~python_workflow.Workflow`.

        :return: Values of :class:`~python_workflow.Task`\[\]
        """
        value = {}
        pool = Pool(size=self.nb_thread)
        jobs = [pool.spawn(task.start) for task in self.tasks]
        gevent.joinall(jobs, raise_error=self.raise_error)

        for idx, task in enumerate(self.tasks):
            value[
                '%s-%s' % (task.name, idx)
            ] = jobs[idx].value
        return value

    def reset(self):
        """
        Reset its timers > its :class:`~python_workflow.Task` timers
        """
        super().reset()
        for task in self.tasks:
            task.reset()


class Workflow(Task):
    """

    :param steps:
    :type steps: Step[]
    """

    def __init__(self, name=None, steps=None, *args, **kwargs):
        """

        :param name: the name of the Workflow
        :type name: str

        :param steps:
        :type steps: Step[]

        :param args: not used. It will be available from :func:`~python_workflow.Task.run`
        :type args: list, optional

        :param kwargs: not used. It will be available from :func:`~python_workflow.Task.run`
        :type kwargs: dict, optional
        """
        super().__init__(name, *args, **kwargs)

        if not isinstance(steps, list):
            raise Exception('`steps` must be a instance of List')

        for step in steps:
            if not isinstance(step, Step):
                raise Exception('`step` must be a instance of Step')
        self.steps = steps

    def run(self):
        """

        :return: Values of :class:`~python_workflow.Step`\[\]
        """
        value = {}
        for idx, step in enumerate(self.steps):
            value[
                '%s-%s' % (step.name, idx)
            ] = step.start()
        return value

    def reset(self):
        """
        Reset its timers > its :class:`~python_workflow.Step` timers > its :class:`~python_workflow.Task` timers
        """
        super().reset()
        for step in self.steps:
            step.reset()
