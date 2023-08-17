---
title: API Reference
sidebar_position: 4
---

# API Reference


### Template

Template is an ChatGPT API call template. Check [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create)
for more information.

```py
from slambda import Template

template = Template(
  name=...,  # name: Optional[str] = None
  description=...,  # description: str = ''
  mode=...,  # mode: List[TextFunctionMode] = Field(default_factory=list)

  # Message Config
  init_messages=...,  # init_messages: List[Message] = Field(default_factory=list)
  default_message=...,  # default_message: Optional[str] = None
  message_template=...,  # message_template: Optional[str] = None

  # OpenAI ChatComplemetion Endpoint parameters
  model=...,  # model: str = 'gpt-3.5-turbo'
  temperature=...,  # temperature: Optional[float] = None
  n=...,  # n: Optional[int] = None
  top_p=...,  # top_p: Optional[float] = None
  stream=...,  # stream: Optional[bool] = None
  stop=...,  # stop: Optional[Union[str, List[str]]] = None
  max_tokens=...,  # max_tokens: Optional[int] = None
  presence_penalty=...,  # presence_penalty: Optional[float] = None
  frequency_penalty=...,  # frequency_penalty: Optional[float] = None
  logit_bias=...,  # logit_bias: Optional[Dict[int, int]] = None
  user=...,  # user: Optional[str] = None
)
```
* **name**: optional name of this template.
* **description**: an optional description for the template.
* **mode**: what call modes are allowed. See (TextFunctionMode)[#TextFunctionMode] for detail.
* **init_messages**: A list of messages comprising the conversation so far, this can be used for providing.
* **default_message**: this message will be sent if no args are provided.
* **message_template**: this message will be rendered with keyword arguments if kwargs are provided.

When executing the call, all message from init_messages will be appended to the message list, and then
  * if **no arguments** is provided, the **default message** will be appended to the message list
  * if **positional arguments** is provided, all the positional arguments will be appended to the message list
      if multiple positional arguments are provided, they will be joined by a comma.
  * if **keyword arguments** is provided, **message_template** will be rendered and appended to the message list

#### Few Shot Learning / In Context Learning / Instruction Following

Template can also be constructed with instruction with or without examples using the `follow_instruction` api
```
from slambda import Template, Example
t = Template().follow_instruction(
  instruction = "Answer positive if sentence has positive general sentiment, otherwise answer negative.",
  examples = [
    Example("The food is great", "positive"),
    Example("The food is awful", "negative")
  ]
)
```



### TextFunction

```py
from slambda import TextFunction, Template

my_function = TextFunction(Template(default_message=''))
my_function()
```
#### Execution Mode: No Args

When `default_message` is provided, you can call the generated function without any arguments.

```py
nullary_function = TextFunction(Template(default_message='send this to ChatCompletion API'))
nullary_function()
```

#### Execution Mode: Keyword Args

```py
from slambda import TextFunction, Template

f = TextFunction(Template(message_template="send today's date: ({date}) to ChatCompletion API"))
f(date="2023-01-01")
```

##### Reserved Keywords
You cannot use `return_dict`, `extra_messages` or `__override` in your message template.

Those keywords are reserved for special purposes:

* **return_dict**: if set to true, the response from ChatCompletion API will be returned directly
* **extra_messages**: extra messages to be carried over, it will be appended after init_messages from template but
                before the final message
* **__override**: any parameters to be override, currently you can override the following:
  * n
  * top_p
  * stream
  * stop
  * max_tokens
  * presence_penalty
  * frequency_penalty
  * logit_bias
  * user
  * [see ChatCompletion API's reference for details](https://platform.openai.com/docs/api-reference/chat/create)


#### Execution Mode: Positional Args

If neither `default_message` nor `message_template` is provided, you can call the generated function with positional arguments.

```py
from slambda import TextFunction, Template

f = TextFunction(Template())
f('send this to ChatCompletion API')
f('send this to ChatCompletion API', "and this")
```


