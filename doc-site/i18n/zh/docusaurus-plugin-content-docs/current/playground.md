---
title: Playground（实验版本）
description: 如何使用 Slambda Playground（实验版本）
sidebar_position: 7
---

# Playground (实验版本)

我们还提供了一个Playground网页应用，作为您的slambda函数的简单Web界面。

启动Playground应用:

```bash title='命令行开启'
# 将 ~/.openai.key 更改为您的 OPENAI_API_KEY_PATH，或使用 OPENAI_API_KEY 变量
OPENAI_API_KEY_PATH=~/.openai.key python -m slambda.playground
```

```python title='程序中开启'
# slambda playground 是基于 Flask 构建的，可能不适用于类似jupyter等环境，我们建议在一个独立的 Python 脚本中运行。

import os
from dotenv import load_dotenv
import openai

# 有关如何使用 dotenv，请参阅 https://slambda.dataset.sh/docs/tips/apikey
load_dotenv(dotenv_path='.env.local')
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

## 界面

假设您的Playground应用正在运行在 `http://127.0.0.1:6767`

该应用使用hash router，因此所有的URL看起来像这样 `http://127.0.0.1:6767/#/`
或者 `http://127.0.0.1:6767/#/playground?name=entail.entail`。

### 主页

在Playground主页上，您可以看到在此Playground中可用的function（函数）列表。

![Playground Home Page](/screenshots/home.png)

### Nullary Function（无参函数）

如果您选择的函数是一个Nullary Function，您会看到类似下面的界面。
您可以点击 `RUN` 按钮来运行您的函数，输出将会显示在下方。

![Playground Nullary Function](/screenshots/nullary.png)

### Unary Function（单参数函数）

如果您选择的函数是一个Unary Function，您会看到类似下面的界面。
您可以在文本输入框中输入您的参数，然后点击 `SUBMIT` 按钮来运行您的函数，输出将会显示在下方。

![Playground Unary Function](/screenshots/unary.png)

### Keyword Function（关键词函数）

如果您选择的函数是一个Keyword Function，您会看到类似下面的界面。
您可以在文本输入框中为必填参数提供值，然后点击 `SUBMIT` 按钮来运行您的函数，输出将会显示在下方。

![Playground Keyword Function](/screenshots/kw.png)

您还可以点击 `NEW KEYWORD ARGUMENT` 按钮来添加更多的参数。

![Playground Keyword Function Expand](/screenshots/kw-expand.png)

### Menu（菜单）

您可以使用右上角的菜单来查看所有函数或者检查函数的执行日志。

![Playground Menu](/screenshots/menu.png)

### Logs（日志）

您可以在日志列表页面查看您的执行日志。

![Playground Logs](/screenshots/logs.png)
