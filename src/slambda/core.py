import json
import warnings
from string import Formatter

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
    KEYWORD = 'keyword'
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
    output: Union[Dict, str] = None

    def __init__(self, input=None, output=None, **kwargs):
        super().__init__(input=input, output=output, **kwargs)

    def to_str_pair(self, definition: 'Definition'):
        output = self.output
        if self.is_str_output:
            output = self.output
        elif self.is_json_output:
            output = json.dumps(self.output)

        if self.is_empty_input:
            return definition.default_message, output
        if self.is_str_input:
            return self.input, output
        elif self.is_dict_input:
            if TextFunctionMode.KEYWORD not in definition.mode:
                definition.mode.append(TextFunctionMode.KEYWORD)
            if definition.message_template is not None:
                return definition.message_template.format(**self.input), output
            else:
                return "\n".join([f"{k}: {v}" for k, v in self.input.items()]), output

    @property
    def is_json_output(self):
        return isinstance(self.output, dict)

    @property
    def is_str_output(self):
        return isinstance(self.output, str)

    @property
    def is_dict_input(self):
        return isinstance(self.input, dict)

    @property
    def is_str_input(self):
        return isinstance(self.input, str)

    @property
    def is_empty_input(self):
        return self.input is None

    def match_call_mode(self, mode_list: List[TextFunctionMode]):
        if self.is_dict_input:
            return TextFunctionMode.KEYWORD in mode_list
        if self.is_str_input:
            return TextFunctionMode.POS in mode_list
        if self.is_empty_input:
            return TextFunctionMode.NO_ARGS in mode_list

    def match_output_mode(self, is_json):
        if self.is_str_output:
            return is_json is False
        if self.is_json_output:
            return is_json is True


class GptApiOptions(BaseModel):
    """
    GptApiOptions used in OpenAI's ChatCompletion API.
    See [OpenAI's API reference](https://platform.openai.com/docs/api-reference/chat/create)

    Args:
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


class Definition(BaseModel):
    """
    Definition is an ChatGPT API call template.

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
        json_output: if output is in json format or string.
        examples: call examples.
        gpt_opts: Inference parameters for ChatCompletion API.
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
    json_output: bool = False

    examples: List[Example] = Field(default_factory=list)

    # OpenAI parameters
    gpt_opts: GptApiOptions = Field(default_factory=GptApiOptions)

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
                # We don't need to check if message template is none, if template is missing, we will simply print one
                # kv pair per line.
                return TextFunctionMode.KEYWORD
        else:
            if kw_count == 0:
                if TextFunctionMode.POS not in self.mode:
                    raise ValueError('Calling with positional args is not allowed.')
                return TextFunctionMode.POS
            else:
                raise ValueError('Function is called with both positional and keyword args.')

    def from_instruction(self, instruction, examples: Optional[List[Example]] = None):
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

    def fn(self) -> 'TextFunction':
        return TextFunction(self)


class TextFunction:
    RESERVED_KEYWORDS = ['return_json', 'extra_messages', '__override', 'return_resp_obj']
    """
    RESERVED_KEYWORDS: reserved keywords:
    return_json: parse output as json.
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
    return_resp_obj: if set to true, the response from ChatCompletion API will be returned directly                
    """

    definition: Definition

    def __init__(self, definition):
        self.definition = definition

    def __call__(self, *args, **kwargs):
        """
        Execute the function call based on the provided template

        :param template:
        :param args:
        :param kwargs:
        :return:
        """
        template = self.definition
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
            if not isinstance(m, Message):
                raise ValueError('message in extra_messages must be an instance of slambda.Message')
            messages.append(m)

        call_mode = template.find_call_mode(*args, **kwargs)

        if call_mode == TextFunctionMode.NO_ARGS:
            messages.append(Message.user(template.default_message))
        elif call_mode == TextFunctionMode.POS:
            if len(args) == 1:
                messages.append(Message.user(args[0]))
            else:
                raise ValueError(f'Multiple positional arguments are provided')
        elif call_mode == TextFunctionMode.KEYWORD:
            if template.message_template is not None:
                msg_text = template.message_template.format(**kwargs)
                messages.append(Message.user(msg_text))
            else:
                msg_text = "\n".join([f"{k}: {v}" for k, v in kwargs.items()])
                messages.append(Message.user(msg_text))

        override_params = ctrl_kws.get('__override', {})

        model = override_params.get('model', template.gpt_opts.model)
        n = override_params.get('n', template.gpt_opts.n)
        temperature = override_params.get('temperature', template.gpt_opts.temperature)
        top_p = override_params.get('top_p', template.gpt_opts.top_p)
        stream = override_params.get('stream', template.gpt_opts.stream)
        stop = override_params.get('stop', template.gpt_opts.stop)
        max_tokens = override_params.get('max_tokens', template.gpt_opts.max_tokens)
        presence_penalty = override_params.get('presence_penalty', template.gpt_opts.presence_penalty)
        frequency_penalty = override_params.get('frequency_penalty', template.gpt_opts.frequency_penalty)
        logit_bias = override_params.get('logit_bias', template.gpt_opts.logit_bias)
        user = override_params.get('user', template.gpt_opts.user)

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

        return_resp_obj = ctrl_kws.get('return_resp_obj', False) or stream is True
        if return_resp_obj:
            return resp

        if n is None or n == 1:
            ret = resp['choices'][0]['message']['content']
            if self.definition.json_output and ctrl_kws.get('return_json', True):
                ret = try_parse_json(ret)
                return ret
            else:
                return ret
        else:
            if self.definition.json_output and ctrl_kws.get('return_json', True):
                return [try_parse_json(c['message']['content']) for c in resp['choices']]
            else:
                return [c['message']['content'] for c in resp['choices']]


def try_parse_json(js):
    try:
        dict_ret = json.loads(js)
        return dict_ret
    except ValueError as e:
        warnings.warn(f"Cannot parse output as json: \n{js}")
        return js


def create_function(
        instruction: str,
        examples: Optional[List[Example]] = None,
        gpt_opts: Optional[GptApiOptions] = None,

        allow_no_arg: bool = False,
        default_message: Optional[str] = None,

        allow_pos: bool = False,

        allow_keyword: bool = False,
        message_template: Optional[str] = None,
        required_args: Optional[List[str]] = None,

        json_output=None,
):
    t = Definition()

    t.json_output = json_output

    if gpt_opts is not None:
        t.gpt_opts = gpt_opts

    if allow_no_arg:
        t.default_message = default_message if default_message is not None else instruction
        t.mode.append(TextFunctionMode.NO_ARGS)

    if allow_keyword and allow_pos:
        raise ValueError('allow_keyword and allow_pos cannot both be true')

    if True not in [allow_no_arg, allow_keyword, allow_pos]:
        raise ValueError('at least one of allow_no_arg, allow_keyword, allow_pos must be true')

    if allow_pos:
        t.mode.append(TextFunctionMode.POS)

    if allow_keyword:
        t.message_template = message_template
        t.required_args = required_args
        if message_template is not None:
            if t.required_args is None:
                t.required_args = extract_required_keywords(message_template)
        t.mode.append(TextFunctionMode.KEYWORD)

    t.from_instruction(instruction, examples)
    json_output = inspect_examples(examples, t.mode, json_output)
    t.json_output = json_output
    return t.fn()


def inspect_examples(examples: Optional[List[Example]], mode_list: List[TextFunctionMode], json_output=None):
    json_output_provided = json_output is not None
    if len(mode_list) == 0:
        raise ValueError('Call mode list is empty')

    if examples is None:
        return json_output

    for example in examples:
        if not example.match_call_mode(mode_list):
            raise ValueError(f'Example cannot be used in call mode [{", ".join(mode_list)}]')

        if json_output is None:
            json_output = example.is_json_output
        else:
            if not example.match_output_mode(json_output):
                if json_output_provided:
                    if json_output:
                        raise ValueError('Example output is str, but dict(json)')
                    else:
                        raise ValueError('Example output is dict(json), but string is expected')
                else:
                    raise ValueError('Example output has a mixed list of string and dict.')

    return json_output


class NullaryFunction:
    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            default_message: Optional[str] = None,

            json_output=None,
    ):
        return create_function(
            instruction, examples,
            gpt_opts=gpt_opts,
            default_message=default_message,
            json_output=json_output,
            allow_no_arg=True,
        )


class UnaryFunction:
    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            allow_no_arg: bool = False,
            default_message: Optional[str] = None,

            json_output=None,
    ):
        return create_function(
            instruction, examples,
            gpt_opts=gpt_opts,
            default_message=default_message,
            json_output=json_output,
            allow_no_arg=allow_no_arg,
            allow_pos=True,
        )


class KeywordFunction:
    @staticmethod
    def from_instruction(
            instruction: str,
            examples: Optional[List[Example]] = None,
            gpt_opts: Optional[GptApiOptions] = None,

            message_template: Optional[str] = None,

            allow_no_arg: bool = False,
            default_message: Optional[str] = None,

            json_output=None,
    ):
        return create_function(
            instruction, examples,
            gpt_opts=gpt_opts,
            default_message=default_message,
            json_output=json_output,
            allow_no_arg=allow_no_arg,
            message_template=message_template,
            allow_keyword=True,
        )


def extract_required_keywords(template_str):
    """
    Extract named keywords from a string template.
    :param template_str: string template
    :return: list of named keywords
    """
    return [fn for _, fn, _, _ in Formatter().parse(template_str) if fn is not None]
