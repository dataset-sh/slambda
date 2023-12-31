---
title: Getting Started
description: Getting Started With Slambda
sidebar_position: 1
---

# Getting Started

:::tip
You can enable code block warp in this guide by clicking this button
![Code Block Warp Button](/img/code-block-wrap-button.png)
:::

## What does slambda do?

Integrating language model such as GPT into your code can be a difficult process. sLambda simplifies the process by 
translating natural language instructions and examples into ready-to-use **Python functions**.

## Install

```bash
pip install slambda
```

## Prerequisite

Currently, sLambda only supports OpenAI's ChatCompletion API, so you will need an OpenAI API key in order to use this
package.

<details><summary>How to load OpenAI API Key</summary>

Please check [OpenAI's documentation: Authentication](https://platform.openai.com/docs/api-reference/authentication) if
you need to create a new API key.  [Create an OpenAI API Key Here](https://platform.openai.com/account/api-keys).

If you have encountered this error:

```
AuthenticationError: No API key provided. You can set your API key in code using 'openai.api_key = <API-KEY>', 
or you can set the environment variable OPENAI_API_KEY=<API-KEY>). If your API key is stored in a file, 
you can point the openai module at it with 'openai.api_key_path = <PATH>'. You can generate API keys in the OpenAI web 
interface. See https://platform.openai.com/account/api-keys for details.
```

It means that you need to supply `OPENAI_API_KEY` somewhere in your code. Check out our guide
on [Loading API key](/docs/tips/apikey) for best practices.

```python
import os
import openai

# We highly recommend you to load OPENAI_API_KEY via environmental variable 

if not os.getenv("OPENAI_API_KEY"):
    print(
        "You need to set environmental variable OPENAI_API_KEY, consider using dotenv."
        "See more on https://slambda.dataset.sh/docs/tips/apikey"
    )

openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------or---------

# You can also do it by providing value directly
openai.api_key = "sk-ThIsIsAFaKeKEY12345678990...."
# But we consider to be a security risk, please read our guide on how to load api key for more details. 
```

</details>

## Define your own functions

`sLambda` will help you implement common NLP tasks using OpenAI's ChatCompletion api, including but not limited to

* extraction
    * named entity
    * events
    * relation
    * ...
* classification
    * sentiment
    * topic
    * ...
* generation
    * summarization
    * paraphrasing
    * translation
    * essay writing
    * ...

In order to implement your function, All you need to do is the following steps:

1. Write an instruction about your task
2. Provide several example using `slambda.Example` class.

```python title='Example: Hello World'
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
# Output: Hello World
```

```python title='Example: Named Entity Recognition'
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
# Output: TriNet Group, Inc.
```

### Extraction

```python title="Extract Stock Tickers"
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

```python title="Extract Wikipeida Links"
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

# If the example out is a dict or list object, the function will also return a dict or list object instead of string.
extract_wiki_links(
    "Without negative feedback, and optionally positive feedback for regeneration, an op amp acts as a comparator.")

# Output (this output is a list of python dict):  
# [{'name': 'negative feedback',
#  'url': 'https://en.wikipedia.org/wiki/Negative_feedback'},
# {'name': 'positive feedback',
#  'url': 'https://en.wikipedia.org/wiki/Positive_feedback'},
# {'name': 'op amp',
#  'url': 'https://en.wikipedia.org/wiki/Operational_amplifier'},
# {'name': 'comparator', 'url': 'https://en.wikipedia.org/wiki/Comparator'}]
```

### Generation

```python title="Grammar and Spelling Error Correction"
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
# Output: 'Schopenhauer did not deny that the external world exists empirically, but he followed Kant in claiming that our knowledge and experience of the world are always indirect.'

```

```python title="Generate Essay"
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

# Output:
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

### Classification

```python title="Binary Sentiment Classifier"
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
# Output: positive
```

## Use existing functions

```py

from slambda.contrib.sentiment import sentiment

print(sentiment('the food is great!') == 'positive')
# Output: True
```

See [Functions](/docs/category/builtin-functions) for existing function implementations.

## Project Status

The basic functionalities of this package have been reasonably tested (coverage: 100%), and you should have no problems
creating your own
functions.

Function implementations in `slambda.contrib` should have a reasonable output quality. However, since they are powered
by a language model, you should conduct your own evaluation/testing within your problem domain to ensure that the
model's performance meeting your requirements.

We plan to add more functions to `slambda.contrib` and provide a more thorough evaluation report for each function
implementation in the near future.