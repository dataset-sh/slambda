---
title: 使用指南
description: Slambda使用指南
sidebar_position: 2
---

# 指南

:::tip
你可以通过点击此按钮在这个指南中启用代码展开（Code Block Warp Button）功能。
![Code Block Warp Button](/img/code-block-wrap-button.png)
:::

## 相关概念

在 sLambda 中，函数由"instruction"（指令）和 "example"（例子）定义。我们可以您使用自然语言指令和一系列例子的input/output（输入/输出）来创建一个普通的 Python 函数。例如：

```python
from slambda import Example, LmFunction

fix_grammar = LmFunction.create(
    instruction="Fix grammar and spelling errors for user",
    examples=[
        Example("I eat three applr yesteday.", "I ate three apples yesterday."),
    ]
)

fix_grammar(
    "Schopenhaur did not deny that the external world exists empiracle, but he followed Kant in claimin' that our knowledge and experiense of the world are always indirekt.")
# 输出：'Schopenhauer did not deny that the external world exists empirically, but he followed Kant in claiming that our knowledge and experience of the world are always indirect.'
```

在本指南中，我们首先将介绍 sLambda 中的核心概念：

1. **自然语言指令（Instruction）**
2. **例子（Example）**
3. **函数 (`LmFunction`)**

我们希望通过查看本指南中提供的例子，您将能够为自己的问题实现您自己的 sLambda 函数。

我们还将分享一些更高级的 sLambda 使用技巧。

### 自然语言指令 Instruction

Instruction是自然语言的命令，例如:

```python
instruction = "Fix grammar and spelling errors for user"
```

### 例子 Example

`Example` 类的定义如下，它将在inference过程中被用作one shot/few shots learning的例子:

```python
class Example(BaseModel):
    input: Optional[FunctionInput] = None
    output: FunctionOutput

    def __init__(self, input=None, output=None, **kwargs):
        super().__init__(input=input, output=output, **kwargs)
```

`Example`的 `input` 字段可以是 `None`、一个 `str` 值或一个 `dict` 对象。
`Example`的 `output` 字段可以是一个 `str` 值，也可以是一个 `dict`/`list` 对象。

如果输入是一个 `dict`，则 `input.values()` 中的所有值都必须能够使用 f-string 渲染为字符串，例如 `f"{value}"`。


```python title="Input: String Output:String"
from slambda import Example

# 字符串到字符串
Example("food is great", "positive")

# 空输入到字符串
Example(output='some output value')

# 字符串到 JSON 列表 ———— 是的您没有看错，python和GPT都可以混合处理中英文(unicode)
Example("food is great", [{"sentiment": "positive", "aspect": "food"}])

# 空输入到 JSON 对象
Example(input="food is great", output={"aspects": [
    {"sentiment": "positive", "aspect_name": "food"}
]})
```

### 函数 Function

sLambda 中的 `LmFunction` 是标准的 Python function(函数)，它接受一个input(输入)，并根据一些内部逻辑将其映射为一个output(输出)。
但是，与其在函数体内部编写 Python 语句作为转换逻辑，我们使用 **Instruction** 和 **Example** (指令,例子)来创建这样的逻辑。

Instruction和Example将被自动翻译为 ChatCompletion API 调用，其实现方式类似于这里的描述[OpenAI cookbook](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb).

#### 函数输入 Input

您可以使用以下方式调用创建的`LmFunction`实例：

* 无参数：`f()`
* 单个 `str` [位置参数](https://docs.python.org/3/glossary.html#term-argument):`f("某个值")`
* [关键字参数](https://docs.python.org/3/glossary.html#term-argument): `f(k="some value")`, `f(k="some value", k2="value2")`

可接受的调用风格由您提供的例子确定。
您为一个函数提供的所有例子必须遵守相同的输入参数格式。
但是，如果提供了 `default_args`，您可以将 `None` 与位置参数或关键字参数格式混合使用。

#### 函数输出 Output

根据您提供的例子，`LmFunction` 将返回一个字符串或一个字典/列表(dict/list)对象。

如果在您的例子中提供了字典/列表输出，生成的函数的输出也将被自动解析。

然而，由于当前语言模型的限制，我们无法保证其输出始终是有效的 JSON 格式。如果我们无法解析输出，将抛出一个 `LmOutputCastingError`，您可以从中获取原始语言模型输出。

所有提供给某个function（函数）的example（例子）必须共享相同的输出格式。

#### 定义函数

您可以使用以下 API 创建 `LmFunction`:

```python
from slambda import LmFunction, Example

LmFunction.create(
    instruction="",
    examples=[Example('', '')],
    # name: Optional[str] = None,
    # strict_no_args: Optional[bool] = None,
    # default_args: Optional[FunctionInput] = None,
    # message_template: Optional[str] = None,
    # required_args: Optional[List[str]] = None,
    # gpt_opts: Optional[GptApiOptions] = None,
)
```

* **strict_no_args**: 如果为 True，则此函数将是一个无参数函数，但如果例子包含非 None 输入，则会忽略此值。
* **default_args**: 如果提供了 default_args，则可以以无参数的方式调用此函数，并使用提供的值作为默认参数。
* **message_template**: 如果提供了 message_template，则将使用`message_template.format(**kwargs)` 来渲染输出消息。否则，将使用`"\n".join([f"{k}: {v}" for k, v in kwargs.items()])` 的值。
* **required_args**: 需要的keyword参数的列表。如果缺少此值且提供了 message_template，则将基于 message_template 的值计算 required_args。
* **gpt_opts**: 用于 ChatCompletion API 的调用参数。

#### 常见实用范例

##### 关键字函数

Keyword function只能通过关键字参数进行调用，例如: `f(k="some value")`, `f(k="some value", k2="value 2")`

```python
from slambda import Example, LmFunction

generate_essay = LmFunction.create(
    instruction="Write an grad school application essay about 250 words using the given information",
    examples=[
        Example(
            input={
                "title": "Why I want to pursue a master's degree in computer science",
                "work_experience": "electrician, financial analyst",
                "education_experience": "Bachelor's degree in English",
            },
            output="""
Transitioning from being an electrician to a financial analyst, and equipped with a Bachelor's degree in English, I am driven to undertake a Master's degree in Computer Science. This decision arises from my diverse experiences, revealing the intersecting points between my past and the boundless possibilities of the tech world.
My time as an electrician cultivated problem-solving and precision skills, paralleling the demands of programming. Similarly, my role as a financial analyst exposed me to the potency of data analysis and technology-driven decision-making. Recognizing these common threads, I am keen to meld my existing expertise with the innovation fostered by computer science.
My Bachelor's degree in English endowed me with critical thinking and communication prowess, invaluable assets when navigating interdisciplinary collaborations and explaining intricate technicalities. By pursuing a Master's in Computer Science, I aspire to fuse my linguistic finesse with programming adeptness, enhancing my capacity to innovate and contribute effectively.
The evolving landscape of computer science intrigues my intellectual curiosity, from AI and machine learning to cybersecurity and software engineering. This fervor drives my academic pursuit, aiming to amplify my theoretical knowledge and hands-on skills, positioning me at technology's vanguard.
In conclusion, my journey – from electrician to financial analyst, fortified by a Bachelor's in English – has illuminated the transformative potential of computer science. With a burning desire to challenge and unite my experiences, I am resolute in my commitment to a Master's in Computer Science. This endeavor promises not only personal enrichment but also a chance to meaningfully influence the trajectory of technological advancement.        
            """.strip()),
    ]
)

generate_essay(
    title="Why I want to pursue a master's degree in computer science",
    work_experience="actor, bartender",
    education_experience="Bachelor degree in english",
    age=60  # Yes, it is possible to customize and add more input parameters on the fly 
)


```

##### 带默认参数的关键字函数

当提供了 `default_args` （默认参数）时，keyword function(关键字函数)还可以以无参数的方式进行调用。

```python
from slambda import Example, LmFunction

generate_essay = LmFunction.create(
    instruction="Write an grad school application essay about 250 words using the given information",
    examples=[
        Example(
            input={
                "title": "Why I want to pursue a master's degree in computer science",
                "work_experience": "electrician, financial analyst",
                "education_experience": "Bachelor's degree in English",
            },
            output="""
Transitioning from being an electrician to a financial analyst, and equipped with a Bachelor's degree in English, I am driven to undertake a Master's degree in Computer Science. This decision arises from my diverse experiences, revealing the intersecting points between my past and the boundless possibilities of the tech world.
My time as an electrician cultivated problem-solving and precision skills, paralleling the demands of programming. Similarly, my role as a financial analyst exposed me to the potency of data analysis and technology-driven decision-making. Recognizing these common threads, I am keen to meld my existing expertise with the innovation fostered by computer science.
My Bachelor's degree in English endowed me with critical thinking and communication prowess, invaluable assets when navigating interdisciplinary collaborations and explaining intricate technicalities. By pursuing a Master's in Computer Science, I aspire to fuse my linguistic finesse with programming adeptness, enhancing my capacity to innovate and contribute effectively.
The evolving landscape of computer science intrigues my intellectual curiosity, from AI and machine learning to cybersecurity and software engineering. This fervor drives my academic pursuit, aiming to amplify my theoretical knowledge and hands-on skills, positioning me at technology's vanguard.
In conclusion, my journey – from electrician to financial analyst, fortified by a Bachelor's in English – has illuminated the transformative potential of computer science. With a burning desire to challenge and unite my experiences, I am resolute in my commitment to a Master's in Computer Science. This endeavor promises not only personal enrichment but also a chance to meaningfully influence the trajectory of technological advancement.        
            """.strip()),
    ],
    default_args={
        "title": "Why I want to pursue a master's degree in computer science",
        "work_experience": "actor, bartender",
        "education_experience": "Bachelor's degree in English",
    }
)

generate_essay()
# 这和下面代码作用相同
# generate_essay(
#     title="Why I want to pursue a master's degree in computer science",
#     work_experience="actor, bartender",
#     education_experience="Bachelor's degree in English",
# )
```

##### 单一参数函数

Unary Function(单一参数函数)只能通过单个位置参数进行调用，例如：`f("some value")`。

```python
from slambda import LmFunction, Example

echo = LmFunction.create(
    instruction='Repeat user input.',
    examples=[
        Example(
            "hello", "hello"
        ),
        Example(
            "world", "world"
        ),
        Example(
            "Repeat user input", "Repeat user input"
        )
    ],
)

echo('hello world')
# 输出：hello world

```

##### 带默认参数的单一参数函数

当提供了 `default_args` (默认参数)时，Unary Function(单一参数函数)也可以以无参数的方式进行调用。

```python
from slambda import LmFunction, Example

from slambda import LmFunction, Example

echo = LmFunction.create(
    instruction='Repeat user input.',
    examples=[
        Example(
            "hello", "hello"
        ),
        Example(
            "world", "world"
        ),
        Example(
            "Repeat user input", "Repeat user input"
        )
    ],
    default_args="No input was given.",
)
echo()  # 这将成功执行
# 输出：No input was given.
echo('你好，世界')
# 输出：你好，世界

```

##### 无参数函数

Nullary Function(无参数函数)只能通过无参数的方式进行调用。

```python title="Nullary Function"
from slambda import LmFunction, Example

motivate_me = LmFunction.create(
    default_args="Generate a motivational message.",
    instruction='Generate motivational messages.',
    examples=[
        Example(
            output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
        )
    ],
    strict_no_args=True,
)


motivate_me()  # 这将成功执行

motivate_me('你好')  # 这将抛出异常

```

## 贴士

#### 启用 JSON 输出

如果你在例子中提供了 `dict` 或 `list`，这个函数的输出将会被自动用 `json.loads` 进行解析，例如:

```python title="Enable JSON Output"
from slambda import Example, LmFunction, GptApiOptions

extract_entities = LmFunction.create(
    instruction="Extract all companies' name mentioned in the news title.",
    examples=[
        Example(input="Why Kroger, Albertsons need to merge immediately to compete with Walmart",
                output=[
                    "Kroger",
                    "Albertsons",
                    "Walmart"
                ])
    ],
    gpt_opts=GptApiOptions(temperature=0)
)
["TriNet Group, Inc."] == extract_entities(
    "TriNet Group, Inc. Commences a Fixed Price Tender Offer to Repurchase up to 5,981,308 Shares")
# 输出: True
```

```python title="Enable JSON Output"
from slambda import Example, LmFunction, GptApiOptions

find_tickers = LmFunction.create(
    instruction="Extract all companies' tickers mentioned in the news title.",
    examples=[
        Example(
            input="Why Kroger, Albertsons need to merge immediately to compete with Walmart",
            output={
                "tickers": ["KR", "ACI"]
            })
    ],
    json_output=True,
    gpt_opts=GptApiOptions(temperature=0)
)

find_tickers("These Stocks Are Moving the Most Today: Keysight, Farfetch, XPeng, Tesla, Deere, and More")
# 输出: {'tickers': ['KEYS', 'FTCH', 'XPEV', 'TSLA', 'DE']}
```

然而，由于当前语言模型的限制，我们无法保证语言模型输出始终是有效的 JSON 格式。如果我们无法使用json.loads解析输出，将会抛出一个 LmOutputCastingError，你可以从中获取原始的语言模型输出值。

```python title="Catching LLMOutputCastingError"
try:
    out = f("some input")
except LLMOutputCastingError as e:
    print(e.llm_output)
    # 这是原始的语言模型输出值。
```

### 控制推断参数

你也可以使用  `GptApiOptions`控制inference(推断)参数，比如`temperature` 

```python
from slambda import LmFunction, Example, GptApiOptions

motivate_me = LmFunction.create(
    instruction='生成励志信息。',
    examples=[
        Example(
            output="坚持不懈，勇往直前，成功将属于你！"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)
```

GptApiOptions Args (参见 [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create)):

* **model**: 要使用的模型，该模型必须与 OpenAI 的 chatCompletion API 兼容  [OpenAI's chatCompletion API](https://platform.openai.com/docs/models/model-endpoint-compatibility)
* **temperature**: 采样温度，介于 0 和 2 之间。参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **n**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **top_p**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **stream**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **stop**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **max_tokens**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **presence_penalty**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **frequency_penalty**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **logit_bias**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **user**: 参见 OpenAI 的 API 参考 [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)

### 覆盖推断参数

如果你希望在每次调用时覆盖一些inference(推断)参数，你可以使用以下方式使用  `__override` 关键字：:

```python
from slambda import LmFunction, Example, GptApiOptions

motivate_me = LmFunction.create(
    instruction='生成励志信息。',
    examples=[
        Example(
            output="坚持不懈，勇往直前，成功将属于你！"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)
motivate_me(__override={'temperature': 1.0})
motivate_me(return_resp_obj=True)
```

### 返回原始OpenAI Response

在调用你的 slambda 函数时，你可以使用关键字`return_resp_obj=True` ，这将强制函数返回原始的 OpenAI Response对象。

注意，当`stream=True`时，我们会默认`return_resp_obj=True` 。

```python
from slambda import LmFunction, Example, GptApiOptions

motivate_me = LmFunction.create(
    instruction='生成励志信息。',
    examples=[
        Example(
            output="坚持不懈，勇往直前，成功将属于你！"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)

motivate_me(return_resp_obj=True)
```

### 采样温度 （Temperature Value）

`Temperature` 通过控制推理过程中的“采样温度”，来控制输出的随机性。

对于生成任务，比如写作，你可能希望稍微提高温度。
对于分类和抽取任务，由于存在正确答案，你应该考虑使用较低的温度，比如 0。

### 背后的原理

Instruction and Examples（指令和例子）会被翻译成类似于此[Cookbook Recipe](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb)中的实现方式。

我们现有函数的文档包含了其消息列表的可视化，这可能会帮助你理解背后发生的事情，比如查看[writing.essay](/docs/functions/writing/essay)。

