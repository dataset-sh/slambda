---
title: 开始使用 slambda
description: 开始使用 slambda
sidebar_position: 1
---

# 开始使用 slambda

:::tip
你可以通过点击此按钮在这个指南中启用代码展开（Code Block Warp Button）功能。
![Code Block Warp Button](/img/code-block-wrap-button.png)
:::

## sLambda 是做什么的？

将语言模型（如 GPT）集成到您的代码中可能是一个复杂的过程。通过 sLambda，我们帮助您将自然语言指令和示例转化为由语言模型实现的**python函数**。

## 安装

```bash
pip install slambda
```

## 需要什么

目前，sLambda 仅支持 OpenAI 的 ChatCompletion API，因此您需要一个 OpenAI API 密钥才能使用。

<details><summary>如何加载OpenAI API Key</summary>

如果您需要创建新的 API 密钥，请查看 OpenAI 的身份验证文档[OpenAI's documentation: Authentication](https://platform.openai.com/docs/api-reference/authentication) if
您可以参考创建 OpenAI API 密钥：[Create an OpenAI API Key Here](https://platform.openai.com/account/api-keys).

如果您遇到了这个错误:

```
AuthenticationError: No API key provided. You can set your API key in code using 'openai.api_key = <API-KEY>', 
or you can set the environment variable OPENAI_API_KEY=<API-KEY>). If your API key is stored in a file, 
you can point the openai module at it with 'openai.api_key_path = <PATH>'. You can generate API keys in the OpenAI web 
interface. See https://platform.openai.com/account/api-keys for details.
```

这意味着您需要在代码中提供 `OPENAI_API_KEY`。请查看我们的指南[Loading API key](/docs/tips/apikey)了解关于加载 API 密钥的最佳实践。

```python
import os
import openai

# 我们强烈建议您通过环境变量加载 OPENAI_API_KEY

if not os.getenv("OPENAI_API_KEY"):
    print(
        "You need to set environmental variable OPENAI_API_KEY, consider using dotenv."
        "See more on https://slambda.dataset.sh/docs/tips/apikey"
    )

openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------或者---------

# 您还可以直接提供值进行设置
openai.api_key = "sk-ThIsIsAFaKeKEY12345678990...."
# 但我们认为这可能会带来安全风险，请阅读我们的指南以了解如何加载 API 密钥的更多细节。
```
</details>


## 定义您自己的Python函数

`sLambda` 将帮助您使用 OpenAI 的 ChatCompletion API 实现常见的自然语言处理（NLP）任务，包括但不限于：

* 信息提取
  * 命名实体识别
  * 事件提取
  * 关系提取
  * ...
* 分类
  * 情感分析
  * 主题分类
  * ...
* 生成
  * 文本摘要总结
  * 重述
  * 翻译
  * 写作文章
  * ...

为了实现您的function（函数），您只需要按照以下步骤进行操作：

1. 编写关于您任务的instruction（指令）
2. 使用 `slambda.Example` 类提供一些example（示例）。

```python title='例子： Hello World'
from slambda import Example, LmFunction, GptApiOptions

hello_world = LmFunction.create(
    instruction="Print Hello World",
    examples=[
        Example(output="Hello World")
    ],
    gpt_opts=GptApiOptions(temperature=0),
    default_args="Print Hello World"
)

hello_world()
# 输出: Hello World
```

```python title='Example: 命名实体识别'
from slambda import Example, LmFunction, GptApiOptions

extract_entities = LmFunction.create(
    instruction="Extract all companies' name mentioned in the news title.",
    examples=[
        Example(input="Why Kroger, Albertsons need to merge immediately to compete with Walmart",
                output="Kroger, Albertsons, Walmart")
    ],
    gpt_opts=GptApiOptions(temperature=0)
)

extract_entities("TriNet Group, Inc. Commences a Fixed Price Tender Offer to Repurchase up to 5,981,308 Shares")
# 输出：TriNet Group, Inc.
```

### 文本信息提取

```python title="提取股票代号"
from slambda import Example, LmFunction, GptApiOptions

find_tickers = LmFunction.create(
    instruction="Extract all companies' tickers mentioned in the news title.",
    examples=[
        Example(
            input="Why Kroger, Albertsons need to merge immediately to compete with Walmart",
            output="$KR, $ACI, $WMT",
        )
    ],
    gpt_opts=GptApiOptions(temperature=0)
)

find_tickers("These Stocks Are Moving the Most Today: Keysight, Farfetch, XPeng, Tesla, Deere, and More")
# Output: '$KEYS, $FTCH, $XPEV, $TSLA, $DE'
```

```python title="提取维基百科链接"
from slambda import Example, LmFunction, GptApiOptions

extract_wiki_links = LmFunction.create(
    instruction="Extract all wikipedia entities mentioned in the text and format them in JSON as following [{name: '', url: ''}].",
    examples=[
        Example(
            input="An analog computer or analogue computer is a type of computer that uses the continuous variation"
                  "aspect of physical phenomena such as electrical, mechanical, or hydraulic quantities (analog signals) "
                  "to model the problem being solved.",
            output=[
                {
                    "name": "computer",
                    "url": "https://en.wikipedia.org/wiki/Computation",

                },
                {
                    "name": "electrical",
                    "url": "https://en.wikipedia.org/wiki/Electrical_network",
                },
                {
                    "name": "mechanical",
                    "url": "https://en.wikipedia.org/wiki/Mechanics",
                },
                {
                    "name": "hydraulic",
                    "url": "https://en.wikipedia.org/wiki/Hydraulics",
                },
                {
                    "name": "analog signals",
                    "url": "https://en.wikipedia.org/wiki/Analog_signal",
                }
            ]
        )
    ],
    gpt_opts=GptApiOptions(temperature=0)
)

# 如果Example output是 dict 或 list 对象，函数将返回 dict 或 list 对象而不是str。

extract_wiki_links(
    "Without negative feedback, and optionally positive feedback for regeneration, an op amp acts as a comparator.")

# 输出（此输出是 a list of python dict）:  
# [{'name': 'negative feedback',
#  'url': 'https://en.wikipedia.org/wiki/Negative_feedback'},
# {'name': 'positive feedback',
#  'url': 'https://en.wikipedia.org/wiki/Positive_feedback'},
# {'name': 'op amp',
#  'url': 'https://en.wikipedia.org/wiki/Operational_amplifier'},
# {'name': 'comparator', 'url': 'https://en.wikipedia.org/wiki/Comparator'}]
```

### 文本生成

```python title="语法和拼写错误纠正"
from slambda import Example, LmFunction

fix_grammar = LmFunction.create(
    instruction="Fix grammar and spelling errors for user",
    examples=[
        Example(
            input="I eat three applr yesteday.",
            output="I ate three apples yesterday."
        ),
    ]
)

fix_grammar(
    "Schopenhaur did not deny that the external world exists empiracle, but he followed Kant in claimin' that our knowledge and experiense of the world are always indirekt.")
# 输出: 'Schopenhauer did not deny that the external world exists empirically, but he followed Kant in claiming that our knowledge and experience of the world are always indirect.'

```

```python title="生成文章"
from slambda import Example, LmFunction

generate_essay = LmFunction.create(
    instruction="Write an grad school application essay about 250 words using the given information",
    examples=[
        Example(
            input={
                "title": " Why I want to apply for master degree in computer science",
                "work_experience": "electrician, financial analyst",
                "education_experience": "Bachelor degree in english",
                # simple typo such as bachelor (should be bachelor’s) should normally be ok. 
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
    title=" Why I want to apply for master degree in computer science",
    work_experience="actor, bartender",
    education_experience="Bachelor degree in english",
    age=60  # Yes, it is possible to customize and add more input parameters on the fly 
)

# 输出:
# As a non-traditional applicant, my decision to pursue a Master's degree in Computer Science stems from a combination
# of my diverse work experiences and my passion for embracing new challenges at the age of 60. Having worked as an actor 
# and bartender, I have always been comfortable in dynamic and fast-paced environments, traits that align 
# well with the ever-evolving field of technology.
# 
# Although my Bachelor's degree in English may seem unrelated, it has sharpened my critical thinking and analytical 
# skills, which are essential in problem-solving and logical reasoning, both foundational elements in computer science. 
# Additionally, my degree has honed my communication abilities, allowing me to effectively convey complex concepts 
# to diverse audiences.
# 
# Despite being a senior applicant, I have a strong motivation to contribute to the field of computer science. 
# With a growing interest in areas such as big data, artificial intelligence, and programming, 
# I am eager to acquire the technical skills and knowledge necessary to engage in meaningful research and innovation. 
# I firmly believe that age should never be a barrier to pursuing one's passions, and I am determined to prove that 
# age can be an asset in terms of experience, wisdom, and a unique perspective.
# 
# Moreover, my life experiences have taught me the value of adaptability, resilience, and a growth mindset. I am 
# prepared to face the challenges and demands of a rigorous Master's program, fully committed to embracing new 
# technologies and pushing the boundaries of my own capabilities.
# 
# In sum, my diverse work experiences, coupled with my Bachelor's degree in English, have paved the way for my decision 
# to pursue a Master's degree in Computer Science. My age only strengthens my resolve to contribute to the field, 
# armed with a lifetime of experiences and a relentless pursuit of knowledge.

```

### 文本分类

```python title="情感识别"
from slambda import Example, LmFunction, GptApiOptions

sentiment = LmFunction.create(
    instruction='Detect sentiment of the given text, answer positive for positive sentiment, negative for negative sentiment, otherwise neutral.',
    examples=[
        Example(
            input="Absolutely love this self licking ice cream cone! The self-licking feature is a game-changer for ice cream lovers like me. No more melty messes, just pure enjoyment. A must-have for summer!",
            output="positive"
        ),
        Example(
            input="Bought this new HyperMultiFunctionGadget 16 X and what a disappointment! It feels cheap, doesn't work as advertised, and the battery life is a joke. Save your money and avoid this one.",
            output="negative"
        ),
        Example(
            input="I ate at this restaurant yesterday.",
            output="neutral"
        )
    ],
    gpt_opts=GptApiOptions(temperature=0),
)
sentiment("The food is pretty, pretty, pretty, pretty good.")
# 输出: positive
```

## 现有函数

```py

from slambda.contrib.sentiment import sentiment

print(sentiment('Food is gread.') == 'positive')
# 输出: True
```

点击这里[Functions](/docs/category/builtin-functions) 查看现有的函数实现。

## 项目状态

这个包的基本功能已经经过了合理的测试（覆盖率：100%），您创建自己的函数过程中应该不会有问题。

`slambda.contrib` 中实现的功能应该有相对准确的准确度。然而，由于它们是基于语言模型实现的，您应该在自己的应用过程中自行进行评估和测试，以确保模型的性能符合您的要求。

我们计划在不久的将来向 `slambda.contrib` 中添加更多的函数，并为每个函数实现提供更全面的评估报告。