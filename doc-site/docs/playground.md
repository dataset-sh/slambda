---
title: Playground (Experimental)
description: How to use Slambda Playground (Experimental)
sidebar_position: 7
---

# Playground (Experimental)

We also include a playground app as a simple web interface for you slambda functions.

To start a playground app:

```bash title='Command Line'
#change ~/.openai.key to your OPENAI_API_KEY_PATH or use the variable OPENAI_API_KEY 
OPENAI_API_KEY_PATH=~/.openai.key python -m slambda.playground
```

```python title='Programmatically'
# slambda playground is built on top of flask, which is not designed to run in 
# environment such as jupyter, we suggest running this in a standalone python script.

import os
from dotenv import load_dotenv
import openai

# See https://slambda.dataset.sh/docs/tips/apikey on how to use dotenv
load_dotenv(dotenv_path='.local.env')
openai.api_key = os.getenv('OPENAI_API_KEY')

from slambda.playground import PlaygroundApp

app = PlaygroundApp()
app.run()
```

```python title='Running a single function'
from slambda import LmFunction, Example
from slambda.playground import PlaygroundApp

hello_world_fn = LmFunction.create(
    'print hello world',
    default_args='print hello world',
    examples=[Example(output="hello world")]
)

app = PlaygroundApp.open(hello_world_fn)
app.run()
```

## Interface

Assuming your playground app is running at `http://127.0.0.1:6767`

The app uses hash router, so all url will look like this `http://127.0.0.1:6767/#/`
or `http://127.0.0.1:6767/#/playground?name=entail.entail`.

### Home Page

In the playground homepage, you can see the list of functions that are available in this playground.

![Playground Home Page](/screenshots/home.png)

### Nullary Function

If the function you selected is a Nullary Function, you will see a similar interface as the following.
You can click the `RUN` button to run your function, and the output will be displayed below.

![Playground Nullary Function](/screenshots/nullary.png)

### Unary Function

If the function you selected is a Unary Function, you will see a similar interface as the following.
You can put your argument in the text input box and click the `SUBMIT` button to run your function, and the output will be
displayed below.
![Playground Unary Function](/screenshots/unary.png)

### Keyword Function

If the function your selected is a Keyword Function, you will see a similar interface as following.
You can put values for the required arguments in the text input box and click the `SUBMIT` button to run your function and
the output will be
displayed below.

![Playground Keyword Function](/screenshots/kw.png)

You can also click the `NEW KEYWORD ARGUMENT` button to add more argument.

![Playground Keyword Function Expand](/screenshots/kw-expand.png)

### Menu

You can use the top-right menu to see all functions or check function execution logs.

![Playground Menu](/screenshots/menu.png)

### Logs

You can view your execution logs in the log listing page.

![Playground Logs](/screenshots/logs.png)
