from dataclasses import dataclass

import openai

from typing import Optional, List, Union, Dict
from pydantic import BaseModel, Field
from enum import Enum


class Role(str, Enum):
    """
    Role for chat message
    https://platform.openai.com/docs/api-reference/chat/create#chat/create-role
    """
    system = 'system'
    user = 'user'
    assistant = 'assistant'
    function = 'function'


class Message(BaseModel):
    """Chat Model Message

    Args:
        role: (Role for chat message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-role]
        content: (The contents of the message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-content]
        name: (The name of the author of this message)[https://platform.openai.com/docs/api-reference/chat/create#chat/create-name]
    """
    role: Role
    content: str
    name: Optional[str] = None

    @staticmethod
    def user(content, name=None):
        return Message(role=Role.user, content=content, name=name)

    @staticmethod
    def assistant(content, name=None):
        return Message(role=Role.assistant, content=content, name=name)

    @staticmethod
    def system(content, name=None):
        return Message(role=Role.system, content=content, name=name)

    @staticmethod
    def example_user(content):
        return Message(role=Role.system, content=content, name='example_user')

    @staticmethod
    def example_assistant(content):
        return Message(role=Role.system, content=content, name='example_assistant')


class TextFunctionMode(str, Enum):
    """
    TextFunctionMode control how a text function can be called.
    """
    KEYWORD = 'kw'
    """
    KEYWORD allows calling with keyword arguments, e.g. f(a=10)
    """
    POS = 'pos'
    """
    POS allows calling with positional arguments, e.g. f(10)
    """
    NO_ARGS = 'no_args'
    """
    NO_ARGS allows calling with no arguments, e.g. f()
    """


class Example(BaseModel):
    input: Optional[Union[Dict, str]] = None
    output: str

    def __init__(self, input=None, output=None, **kwargs):
        super().__init__(input=input, output=output, **kwargs)

    def to_str_pair(self, template: 'Template'):
        if self.input is None:
            return template.default_message, self.output
        if isinstance(self.input, str):
            return self.input, self.output
        elif isinstance(self.input, dict):
            return template.message_template.format(**self.input), self.output


class Template(BaseModel):
    """
    Template is an ChatGPT API call template.
    Check [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create)

    When executing the call, all message from init_messages will be appended to the message list, and then
        * if no arguments is provided, the default message will be appended to the message list
        * if positional arguments is provided, all the positional arguments will be appended to the message list
            if multiple positional arguments are provided, they will be joined by a comma.
        * if keyword arguments is provided, message_template will be rendered and appended to the message list

    Args:
        name: optional name of this template.
        description: an optional description for the template.
        mode: what call modes are allowed. See (TextFunctionMode)[#TextFunctionMode] for detail.
        init_messages: A list of messages comprising the conversation so far, this can be used for providing.
        default_message: this message will be sent if no args are provided.
        message_template: this message will be rendered with keyword arguments if kwargs are provided.
        required_args: list of required keyword args.
        examples: call examples
        model: which model to use, the model must be compatible with [OpenAI's chatCompletion API](https://platform.openai.com/docs/models/model-endpoint-compatibility)
        temperature: What sampling temperature to use, between 0 and 2. See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        n: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        top_p: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        stream: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        stop: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        max_tokens: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        presence_penalty: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        frequency_penalty: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        logit_bias: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
        user: See [OpenAI's API Reference](https://platform.openai.com/docs/api-reference/chat/create)
    """
    # Template Information
    name: Optional[str] = None
    description: str = ''
    mode: List[TextFunctionMode] = Field(default_factory=list)

    # Message Config
    init_messages: List[Message] = Field(default_factory=list)
    default_message: Optional[str] = None
    message_template: Optional[str] = None
    required_args: Optional[List[str]] = None
    examples: List[Example] = Field(default_factory=list)

    # OpenAI parameters
    model: str = 'gpt-3.5-turbo'
    temperature: Optional[float] = None
    n: Optional[int] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = None
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[int, int]] = None
    user: Optional[str] = None

    def model_post_init(self, __context):
        """
        Auto adjust available modes if not provided.
        :param __context:
        :return:
        """
        if self.mode is None or len(self.mode) == 0:
            self.mode = []
            if self.default_message is not None:
                self.mode.append(TextFunctionMode.NO_ARGS)
            if self.message_template is not None:
                self.mode.append(TextFunctionMode.KEYWORD)
            if len(self.mode) == 0:
                self.mode.append(TextFunctionMode.POS)

        if self.required_args is not None and len(self.required_args) > 0:
            if len(self.mode) != 1 and TextFunctionMode.KEYWORD not in self.mode:
                raise Warning('required_args is provided, self.mode will be set to [TextFunctionMode.KEYWORD] '
                              'and default_message will be ignored')
                self.mode = [TextFunctionMode.KEYWORD]

    def find_call_mode(self, *args, **kwargs) -> TextFunctionMode:
        """
        Return the appropriate call mode for the given positional and keyword arguments.

        :param args: positional arguments
        :param kwargs: keyword arguments
        :return: Appropriate call mode
        """
        pos_count = len(args) if args is not None else 0
        kw_count = len(kwargs) if kwargs is not None else 0
        if pos_count == 0:
            if kw_count == 0:
                if TextFunctionMode.NO_ARGS not in self.mode:
                    raise ValueError('Calling with no args is not allowed.')
                if self.default_message is None:
                    raise ValueError('Function cannot be called with no args, because default_message is None.')
                return TextFunctionMode.NO_ARGS
            else:
                if TextFunctionMode.KEYWORD not in self.mode:
                    raise ValueError('Calling with keyword args is not allowed.')
                if self.message_template is None:
                    raise ValueError('Function cannot be called with keyword args, because message_template is None.')
                return TextFunctionMode.KEYWORD
        else:
            if kw_count == 0:
                if TextFunctionMode.POS not in self.mode:
                    raise ValueError('Calling with positional args is not allowed.')
                return TextFunctionMode.POS
            else:
                raise ValueError('Function is called with both positional and keyword args.')

    def follow_instruction(self, instruction, examples: Optional[List[Example]] = None):
        """
        Using instruction and examples to create init_messages list.
        Instruction will be loaded into the first system message, and each input/output in examples list will be
        appended to the init_messages list with example_user and example_assistant respectively

        :param instruction:
        :param examples:
        :return:
        """
        self.init_messages = [
            Message.system(instruction)
        ]

        if examples is not None:
            for example in examples:
                assert isinstance(example, Example), "example must be an instance of Example"
                input_, output = example.to_str_pair(self)
                self.init_messages.append(
                    Message.example_user(input_)
                )
                self.init_messages.append(
                    Message.example_assistant(output)
                )
            self.examples = examples

        return self


builtin_templates = [
    Template(
        name="generate_idea",
        messages=[
            Message.system('You are a assistant that create random slideshow topic idea'),
            Message.example_user('Generate random lecture topic'),
            Message.example_assistant('How to build a landing page')
        ],
        default_message='Generate random lecture topic',
        temperature=1.8
    ),
    Template(
        name="generate_slide",
        message_template="Title: {title}\nPage Count: {page_count}",
        messages=[
            Message.system('You are a assistant that create a list of slide given a lecture topic in markdown format'),
            Message.example_user('Title: How to build a landing page\nPage Count: 5'),
            Message.example_assistant('''
{
 "slides": [
  {
   "title": "Introduction",
   "bulletPoints": [
    "Importance of a landing page for startups",
    "Purpose of a landing page"
   ]
  },
  {
   "title": "Defining Your Goal",
   "bulletPoints": [
    "Identify the main objective of your landing page",
    "Choose a specific call-to-action (CTA) to drive conversions",
    "Set measurable goals to track success"
   ]
  },
  {
   "title": "Compelling Content",
   "bulletPoints": [
    "Craft a captivating headline",
    "Write clear and concise copy",
    "Highlight the unique value proposition",
    "Include persuasive testimonials or case studies",
    "Use compelling visuals and videos"
   ]
  },
  {
   "title": "Effective CTA",
   "bulletPoints": [
    "Place the CTA prominently on the page",
    "Make the CTA visually appealing and action-oriented",
    "Use persuasive language in the CTA copy",
    "Ensure the CTA stands out from the rest of the page"
   ]
  },
  {
   "title": "Conclusion",
   "bulletPoints": [
    "Summarize key points",
    "Encourage visitors to take action"
   ]
  }
 ]
}
'''.strip())
        ],
    ),
    Template(
        name="generate_narration",
        messages=[
            Message.system('You are a assistant that create a script for instructor given a lecture slide'),
            Message.example_user("""
Topic: How to build a landing page
Title: Best Practices for Landing Page Creation
* Mobile Responsiveness - Ensure your landing page is mobile-friendly.
* Minimize Form Fields - Keep the form fields minimal to reduce friction.
* Engaging Copy - Use persuasive language and storytelling to captivate visitors.
* Trust Elements - Include testimonials, reviews, and trust symbols to build credibility.
            """.strip()),
            Message.example_assistant("""
Hello, everyone! We've covered some essential aspects of building an effective landing page for your startup, and now we'll dive into the best practices that can significantly enhance your landing page's performance. These practices will help you create landing pages that engage visitors and drive conversions. So, let's get started with the best practices for landing page creation.
The first practice we'll discuss is Mobile Responsiveness. It's crucial to ensure that your landing page is mobile-friendly. With an increasing number of users accessing websites from their mobile devices, a responsive landing page provides a seamless experience, boosting engagement and conversions.
Moving on, we have Minimize Form Fields. It's essential to keep the form fields minimal on your landing page. Lengthy forms can create friction and deter potential leads. By asking for only essential information, you make it easier for visitors to engage with your CTA and increase the chances of form completions.
Lastly, we have Trust Elements. Building credibility is crucial for gaining your visitors' trust. Include elements such as testimonials, reviews, and trust symbols to showcase the positive experiences of previous customers and reinforce the reliability of your product or service.
To sum up, incorporating these best practices into your landing page creation process will help you create high-performing, engaging, and conversion-driven landing pages. Remember, landing pages are powerful tools for connecting with your audience and achieving your startup's goals.
            """.strip())
        ],
    )
]


class TextFunction:
    RESERVED_KEYWORDS = ['return_dict', 'extra_messages', '__override']
    """
    RESERVED_KEYWORDS: reserved keywords:
    return_dict: if set to true, the response from ChatCompletion API will be returned directly
    extra_messages: extra messages to be carried over, it will be appended after init_messages from template but 
                    before the final message
    __override: any parameters to be override, currently you can override the following:
                    * n
                    * top_p
                    * stream
                    * stop
                    * max_tokens
                    * presence_penalty
                    * frequency_penalty
                    * logit_bias
                    * user
                (see here for details)[https://platform.openai.com/docs/api-reference/chat/create]
    """

    template: Template

    def __init__(self, template):
        self.template = template

    def __call__(self, *args, **kwargs):
        """
        Executing function call
        :param args:
        :param kwargs:
        :return:
        """
        return TextFunction._handle_call(self.template, *args, **kwargs)

    @staticmethod
    def wrap(template):
        """
        Return a decorator function that be used to construct a TextFunction.
        ```py
        @TextFunction.wrap(Template(...))
        def my_text_func():
            # function body will be discarded
            pass
        ```

        :param template: the template
        :return: a decorator function that be used to construct a TextFunction
        """

        def decorator(func):
            return TextFunction(template)

        return decorator

    @staticmethod
    def _handle_call(template, *args, **kwargs):
        """
        Execute the function call based on the provided template

        :param template:
        :param args:
        :param kwargs:
        :return:
        """
        all_kwargs = kwargs
        kwargs = {}
        ctrl_kws = {}
        for k, v in all_kwargs.items():
            if k in TextFunction.RESERVED_KEYWORDS:
                ctrl_kws[k] = v
            else:
                kwargs[k] = v

        if template.required_args is not None:
            for key in template.required_args:
                if key not in kwargs:
                    raise ValueError(f'{key} is required but not provided')

        messages = [
            m for m in template.init_messages
        ]

        for m in ctrl_kws.get('extra_messages', []):
            assert isinstance(m, Message), 'message in extra_messages must be an instance of slambda.Message'
            messages.append(m)

        call_mode = template.find_call_mode(*args, **kwargs)

        if call_mode == TextFunctionMode.NO_ARGS:
            messages.append(Message.user(template.default_message))
        elif call_mode == TextFunctionMode.POS:
            if len(args) == 1:
                messages.append(Message.user(args[0]))
            else:
                messages.append(Message.user(", ".join(args)))
        elif call_mode == TextFunctionMode.KEYWORD:
            messages.append(Message.user(template.message_template.format(**kwargs)))

        override_params = ctrl_kws.get('__override', {})

        model = override_params.get('model', template.model)
        n = override_params.get('n', template.n)
        temperature = override_params.get('temperature', template.temperature)
        top_p = override_params.get('top_p', template.top_p)
        stream = override_params.get('stream', template.stream)
        stop = override_params.get('stop', template.stop)
        max_tokens = override_params.get('max_tokens', template.max_tokens)
        presence_penalty = override_params.get('presence_penalty', template.presence_penalty)
        frequency_penalty = override_params.get('frequency_penalty', template.frequency_penalty)
        logit_bias = override_params.get('logit_bias', template.logit_bias)
        user = override_params.get('user', template.user)

        call_args_dict = dict(
            messages=[
                m.model_dump(exclude_none=True, mode='json') for m in messages
            ],
            model=model,
            n=n,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
            stop=stop,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            user=user
        )

        call_args_dict = {k: v for k, v in call_args_dict.items() if v is not None}
        resp = openai.ChatCompletion.create(**call_args_dict)

        return_dict = ctrl_kws.get('return_dict', False) or stream is True

        if return_dict:
            return resp

        if n is None or n == 1:
            ret = resp['choices'][0]['message']['content']
            return ret
        else:
            return [c['message']['content'] for c in resp['choices']]
