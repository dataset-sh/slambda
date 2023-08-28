---
title: "Guide"
description: Slambda Usage Guide
sidebar_position: 2
---

# Guide

:::tip
You can enable code block warp in this guide by clicking this button
![Code Block Warp Button](/img/code-block-wrap-button.png)
:::

## Concepts

In sLambda, functions are defined by instruction and examples. This library can create a normal python function using only a natural
language instruction, a set of
example input/output pairs. For example:

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
# Output: 'Schopenhauer did not deny that the external world exists empirically, but he followed Kant in claiming that our knowledge and experience of the world are always indirect.'
```

in this guide, we will first introduce the core concepts in sLambda:

1. **Instruction**
2. **Example**
3. **Function(`LmFunction`)**

We hope by looking at the examples we provide in this guide, you will be able to implement your own slambda function for
your own problem.

We will also share some tips for more advanced sLambda usage.

### Instruction

Instructions are simply natural language commands, for example:

```python
instruction = "Fix grammar and spelling errors for user"
```

### Example

The `Example` class is defined as below and will be served as one/few shots learning example during inference:

```python
class Example(BaseModel):
    input: Optional[FunctionInput] = None
    output: FunctionOutput

    def __init__(self, input=None, output=None, **kwargs):
        super().__init__(input=input, output=output, **kwargs)
```

The `input` field of `Example` can be one of `None`, a `str` value, a `dict` object.
The `output` field of `Example` can be a  `str` value or a `dict`/`list` object.

If input is a `dict`, all value in `input.values()` must be able to render as a string with f-string i.e. `f"{value}"`

```python title="Input: String Output:String"
from slambda import Example

# String to String
Example("food is great", "positive")

# Empty input to String
Example(output='some output value')

# String to JSON List
Example("food is great", [{"sentiment": "positive", "aspect": "food"}])

# Empty input to JSON Object
Example(input="food is great", output={"aspects": [
    {"sentiment": "positive", "aspect_name": "food"}
]})
```

### Function

`LmFunction`s in sLambda are standard python functions, it takes an input and maps it to an output according to some
internal
logic.
But instead of writing python statements inside the function body as the transformation logic, we use **Instruction**
and **Example** to create such logic.

Instruction and Examples will be translated into ChatCompletion API call automatically with a similar implementation of this [OpenAI cookbook](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb).

#### Input

You can call a `LmFunction` with:

* no arguments: `f()`
* a single `str` [positional argument](https://docs.python.org/3/glossary.html#term-argument): `f("some value")`
* [keyword
  arguments](https://docs.python.org/3/glossary.html#term-argument): `f(k="some value")`, `f(k="some value", k2="value2"")`

The acceptable calling style is determined by the example you provided.
All examples you provided to one function must share the same input arguments format.
However, if `default_args` are provided, you can mix `None` input with positional or keyword input format.

#### Output

`LmFunction` will return a string or a dict/list object based on the examples you provided.

If you provided dict/list output in your examples, the output of the resulting function will also be parsed
automatically.

However, due to the limitation of the current Language Models, we can not guarantee its output will always be in valid json format.


If we cannot parse the output, an `LmOutputCastingError` will be thrown, and you can access the raw language model output
from it.

All examples provided to a single function must share the same output format.

#### Define

You can create `LmFunction` using the following API:

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

* **strict_no_args**: if True, this function will be a nullary function, however, this value will be ignored
  if examples contain non-None input.
* **default_args**: If a default_args is provided, this function can be called with no arguments, and
  the provided value will be used as default arguments instead.
* **message_template**: if message_template is provided, it will be used to render the outgoing message by
  running `message_template.format(**kwargs)` . Otherwise, value
  of `"\n".join([f"{k}: {v}" for k, v in kwargs.items()])` will be used.
* **required_args**: list of required keyword args. If this value is missing and message_template is provided,
  we will calculate required_args based on the value of message_template.
* **gpt_opts**: inference parameters for ChatCompletion API.

#### Common Patterns

##### Json Output

If you provide `dict` or `list` in your examples, the output of this function will be automatically parsed using `json.loads`, for example:

```python title="Enable JSON Output"
from slambda import Example, LmFunction, GptApiOptions

extract_entities = LmFunction.create(
    instruction="Extract all companies' name mention in the news title.",
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
# Output: True
```

```python title="Catching LLMOutputCastingError"
try:
    out = f("some input")
except LLMOutputCastingError as e:
    print(e.llm_output)
    # This is the original language model output value.
```

##### Keyword Function

A keyword function can only be called by keyword arguments, for
example: `f(k="some value")`, `f(k="some value", k2="value2"")`

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

##### Keyword Function With Default Args

When provided with `default_args`, the keyword function can also be called with no arguments.

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
# This will be equivalent to
# generate_essay(
#     title="Why I want to pursue a master's degree in computer science",
#     work_experience="actor, bartender",
#     education_experience="Bachelor's degree in English",
# )
```

##### Unary Function

A unary function can only be called by a single string positional arguments, for example: `f("some value")`.

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
# Output: hello world

```

##### Unary Function With Default Args

When provided with `default_args`, the unary function can also be called with no arguments.

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
    default_args="No input was given.", 
)

echo()  # This will success
# Output: No input was given.
echo('hello world')  
# Output: hello world

```

##### Nullary Function

A nullary function can also be called with no arguments.

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

motivate_me() # This will success

motivate_me('hello') # This will throw exception

```

## Tips

### Json Output

By providing Example with `dict`/`list` output, and `json_output=True`, you can make you function return a `dict`.

```python
from slambda import Example, LmFunction, GptApiOptions

find_tickers = LmFunction.create(
    instruction="Extract all companies' tickers mention in the news title.",
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
# Output: {'tickers': ['KEYS', 'FTCH', 'XPEV', 'TSLA', 'DE']}
```

However, LLM will some time generate syntactically incorrect json, in that case, the function will return string
instead.

### Controlling Inference Parameters

You can also control the inference parameters such as `temperature` with `GptApiOptions`

```python
from slambda import LmFunction, Example, GptApiOptions

motivate_me = LmFunction.create(
    instruction='Generate motivational messages.',
    examples=[
        Example(
            output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)
```

GptApiOptions Args (See [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create)):

* **model**: which model to use, the model must be compatible
  with [OpenAI's chatCompletion API](https://platform.openai.com/docs/models/model-endpoint-compatibility)
* **temperature**: What sampling temperature to use, between 0 and 2.
  See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **n**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **top_p**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **stream**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **stop**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **max_tokens**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **presence_penalty**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **frequency_penalty**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **logit_bias**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
* **user**: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)

### Overriding Inference Parameters

If you wish to override some inference parameters per-call basis, you can use `__override` keyword as following:

```python
from slambda import LmFunction, Example, GptApiOptions

motivate_me = LmFunction.create(
    instruction='Generate motivational messages.',
    examples=[
        Example(
            output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)
motivate_me(__override={'temperature': 1.0})
motivate_me(return_resp_obj=True)
```

### Access Raw OpenAI Response

You can use `return_resp_obj=True` keyword when calling your slambda function, which will force the function to return
the raw OpenAI response object.

Note that `return_resp_obj=True` by default when `stream=True`.

```python
from slambda import LmFunction, Example, GptApiOptions

motivate_me = LmFunction.create(
    instruction='Generate motivational messages.',
    examples=[
        Example(
            output="Embrace each new day as a fresh opportunity to chase your dreams and create the life you envision. Challenges may arise, but remember, they are stepping stones on your path to success. Believe in your abilities, stay focused on your goals, and let your determination shine brighter than any obstacles. You have the power to turn your aspirations into reality – keep moving forward with unwavering courage and a positive spirit. Your journey is unique, and every step you take brings you closer to the extraordinary success that awaits. Keep pushing, keep believing, and keep thriving!"
        )
    ],
    gpt_opts=GptApiOptions(temperature=1.5)
)

motivate_me(return_resp_obj=True)
```

### Temperature Value

`Temperature` controls the randomness of output by controlling the sampling temperature during inference.

For generation tasks such as writing, you may want a slightly higher temperature.
For classification and extraction tasks where there exists a correct answer for each input, you should consider using a
lower temperature, such as 0.

### Behind the scene

Instruction and Examples are translated into `system` messages similar to this
[Cookbook Recipe](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb).
Our documentation of existing functions contains a visualization of its message stack that may help you understand what
is happening behind the scene, for
example see [writing.essay](/docs/functions/writing/essay).

