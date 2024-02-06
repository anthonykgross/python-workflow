=============
Tutorial
=============

This tutorial introduces **python-workflow** by means of example - we will walk through how to
create a simple crawler for images. Our crawler will fetch images from https://picsum.photos/ and resize them.

Getting started
===============

Before we start, we have to install **python-workflow**.

.. code-block::

    $ python -m pip install python-workflow

.. warning:: Only for this tutorial, we will install `Pillow <https://pypi.org/project/pillow/>`_ and `Requests <https://requests.readthedocs.io/en/latest/>`_

    .. code-block::

        $ python -m pip install pillow requests


We have to create a ``main.py`` file and import **python-workflow**.

.. note:: You can see our examples on `Github <https://github.com/anthonykgross/python-workflow/tree/main/examples/>`_

Defining our tasks
======================

First we will create 2 types of :class:`~python_workflow.Task` : ``CrawlerTask`` and ``ResizerTask``

.. code-block:: python

    # main.py
    import gevent
    import requests
    from PIL import Image

    from python_workflow import Task, Step, Workflow


    class CrawlerTask(Task):
        def __init__(self, index=0):
            super().__init__('MyCrawlerTask')
            self.index = index

        def run(self):
            r = requests.get(
                'https://picsum.photos/600/400'
            )

            if r.status_code == 200:
                with open('output/%s-image.png' % self.index, "wb") as f:
                    f.write(r.content)


    class ResizerTask(Task):
        def __init__(self, index=0):
            super().__init__('MyResizerTask')
            self.index = index

        def run(self):
            filename = 'output/%s-image.png' % self.index
            final_filename = 'output/%s-thumbnail.png' % self.index

            base_width = 100
            img = Image.open(filename)
            w_percent = (base_width / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(w_percent)))
            img = img.resize((base_width, hsize), Image.LANCZOS)
            img.save(final_filename)
            # We are slowing down the resizing process for watching threads
            gevent.sleep(1)


Defining our steps
======================

| Now we have our tasks, we will group them as Step. All tasks in a Step are threaded.
| **By default**, tasks are processed in stack of 4. You can change it with **nb_thread** kwargs. See :func:`~python_workflow.Step.__init__`

.. code-block:: python

    # main.py
    #
    # ....
    #
    tasks = []
    for i in range(0, 10):
        tasks.append(
            CrawlerTask(i)
        )
    step1 = Step(
        'CrawlingStep',
        tasks=tasks,
    )

    tasks = []
    for i in range(0, 10):
        tasks.append(
            ResizerTask(i)
        )
    step2 = Step(
        'ResizingStep',
        tasks=tasks
    )

Defining our workflow
======================

Finally, define :class:`~python_workflow.Step` in our Workflow with :func:`~python_workflow.Workflow.__init__`.

.. code-block:: python

    # main.py
    #
    # ....
    #
    w = Workflow(
        'ExampleCrawlerWorkflow',
        steps=[
            step1,
            step2
        ]
    )
    w.start()

Running our workflow !
======================

Execute ``main.py``

.. code-block:: bash

    $ python main.py

.. code-block:: bash

     [2024-02-22T16:15:16.246620][ExampleCrawlerWorkflow        ] Workflow is starting ...                           args=(), kwargs={}
     [2024-02-22T16:15:16.246708][CrawlingStep                  ] Step is starting ...                               args=(), kwargs={}
     [2024-02-22T16:15:16.247516][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:16.248300][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:16.248688][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:16.248991][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:18.011087][                 MyCrawlerTask] CrawlerTask completed (1.7636s.)                   args=(), kwargs={}
     [2024-02-22T16:15:18.011287][                 MyCrawlerTask] CrawlerTask completed (1.763s.)                    args=(), kwargs={}
     [2024-02-22T16:15:18.011369][                 MyCrawlerTask] CrawlerTask completed (1.7627s.)                   args=(), kwargs={}
     [2024-02-22T16:15:18.011433][                 MyCrawlerTask] CrawlerTask completed (1.7625s.)                   args=(), kwargs={}
     [2024-02-22T16:15:18.011621][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:18.012474][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:18.013083][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:18.013424][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:20.132523][                 MyCrawlerTask] CrawlerTask completed (2.1209s.)                   args=(), kwargs={}
     [2024-02-22T16:15:20.132687][                 MyCrawlerTask] CrawlerTask completed (2.1203s.)                   args=(), kwargs={}
     [2024-02-22T16:15:20.132769][                 MyCrawlerTask] CrawlerTask completed (2.1197s.)                   args=(), kwargs={}
     [2024-02-22T16:15:20.132841][                 MyCrawlerTask] CrawlerTask completed (2.1195s.)                   args=(), kwargs={}
     [2024-02-22T16:15:20.133016][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:20.133872][MyCrawlerTask                 ] CrawlerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:20.886846][                 MyCrawlerTask] CrawlerTask completed (0.7539s.)                   args=(), kwargs={}
     [2024-02-22T16:15:20.887034][                 MyCrawlerTask] CrawlerTask completed (0.7532s.)                   args=(), kwargs={}
     [2024-02-22T16:15:20.887185][                  CrawlingStep] Step completed (4.6405s.)                          args=(), kwargs={}
     [2024-02-22T16:15:20.887246][ResizingStep                  ] Step is starting ...                               args=(), kwargs={}
     [2024-02-22T16:15:20.887408][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:20.887528][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:20.887592][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:20.887651][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:21.901267][                 MyResizerTask] ResizerTask completed (1.0139s.)                   args=(), kwargs={}
     [2024-02-22T16:15:21.906071][                 MyResizerTask] ResizerTask completed (1.0186s.)                   args=(), kwargs={}
     [2024-02-22T16:15:21.910313][                 MyResizerTask] ResizerTask completed (1.0228s.)                   args=(), kwargs={}
     [2024-02-22T16:15:21.914607][                 MyResizerTask] ResizerTask completed (1.027s.)                    args=(), kwargs={}
     [2024-02-22T16:15:21.914725][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:21.914773][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:21.914801][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:21.914828][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:22.924639][                 MyResizerTask] ResizerTask completed (1.01s.)                     args=(), kwargs={}
     [2024-02-22T16:15:22.932236][                 MyResizerTask] ResizerTask completed (1.0175s.)                   args=(), kwargs={}
     [2024-02-22T16:15:22.937866][                 MyResizerTask] ResizerTask completed (1.0231s.)                   args=(), kwargs={}
     [2024-02-22T16:15:22.942050][                 MyResizerTask] ResizerTask completed (1.0273s.)                   args=(), kwargs={}
     [2024-02-22T16:15:22.942173][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:22.942226][MyResizerTask                 ] ResizerTask is starting ...                        args=(), kwargs={}
     [2024-02-22T16:15:23.952175][                 MyResizerTask] ResizerTask completed (1.01s.)                     args=(), kwargs={}
     [2024-02-22T16:15:23.956687][                 MyResizerTask] ResizerTask completed (1.0145s.)                   args=(), kwargs={}
     [2024-02-22T16:15:23.956783][                  ResizingStep] Step completed (3.0696s.)                          args=(), kwargs={}
     [2024-02-22T16:15:23.956816][        ExampleCrawlerWorkflow] Workflow completed (7.7102s.)                      args=(), kwargs={}

