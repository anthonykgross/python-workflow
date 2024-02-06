import logging
import os
import sys
import gevent
import requests
from PIL import Image

logger = logging.getLogger('python-workflow')
logger.setLevel(logging.DEBUG)

fh = logging.StreamHandler(sys.stdout)
fh.setLevel(logger.level)
logger.addHandler(fh)

sys.path.insert(0, os.path.abspath("../.."))
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
        gevent.sleep(1)
        filename = 'output/%s-image.png' % self.index
        final_filename = 'output/%s-thumbnail.png' % self.index

        base_width = 100
        img = Image.open(filename)
        w_percent = (base_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, hsize), Image.LANCZOS)
        img.save(final_filename)


if __name__ == '__main__':
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

    w = Workflow(
        'ExampleCrawlerWorkflow',
        steps=[
            step1,
            step2
        ]
    )
    w.start()
