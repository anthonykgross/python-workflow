[![Python Application](https://github.com/anthonykgross/python-workflow/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/anthonykgross/python-workflow/actions/workflows/main.yml)

# python-workflow


## Install
**From PyPI**
```commandline
pip install python-workflow
```

**From source**
```commandline
rm build/ python_workflow.egg-info dist -Rf
python3 setup.py bdist_wheel
pip3 install -I dist/python_workflow-*-py3-none-any.whl
```
## How it works
```mermaid
sequenceDiagram
    Workflow->>+Step: Step1 is starting ...
    Step->>+Task: Task1 is starting ...
    Step->>+Task: Task2 is starting ...
    Task->>-Step: Task2 is done
    Task->>-Step: Task1 is done
    Step->>+Task: Task3 is starting ...
    Task->>-Step: Task3 is done
    Step->>-Workflow: Step1 is done
    Note right of Step: Tasks are running in concurrency (thread)
    Note right of Workflow: Step is done when all its tasks are done
```
Each Step is running when the previous one is done.
A Step is done when all its tasks are completed or raise exceptions.
Workflow will be stopped when a Step crashes or complete them.

| kwargs      | default | description                                                                                |
|-------------|---------|--------------------------------------------------------------------------------------------|
| nb_thread   | 4       | The number of tasks to execute simultaneously. <br/>e.g. : 10 tasks on 2 threads = 5 loops |
| raise_error | True    | If one of tasks crashes, the whole Step is considered as failed.                           |

## How to use
```python
from python_workflow import Task, Step, Workflow

class MyTask1(Task):
    def __init__(self):
        super().__init__('my_task_1')

    def run(self):
        return 'It works 1!'
   
class MyTask2(Task):
    def __init__(self):
        super().__init__('my_task_2')

    def run(self):
        return 'It works 2!'

class MyTask3(Task):
    def __init__(self):
        super().__init__('my_task_3')

    def run(self):
        return 'It works 3!'
    
step1 = Step(
    'my_step_1', tasks=[
        MyTask1(),
        MyTask2(),
        MyTask3(),
    ],
    nb_thread=2
)

workflow = Workflow('my_workflow', steps=[step1])
workflow.start()

workflow.duration
# 3
workflow.steps[0].duration
# 3
workflow.steps[0].tasks[0].duration
# 2
workflow.steps[0].tasks[1].duration
# 1
workflow.steps[0].tasks[2].duration
# 1
```

## Contributors
**Anthony K GROSS**
- <https://anthonykgross.fr>
- <https://twitter.com/anthonykgross>
- <https://github.com/anthonykgross>

## Copyright and license
Code and documentation copyright 2024. Code released under [the MIT license](https://github.com/anthonykgross/python-workflow/blob/main/LICENSE).