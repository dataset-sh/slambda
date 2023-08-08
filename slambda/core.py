import openai

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class Role(str, Enum):
    system = 'system'
    user = 'user'
    assistant = 'assistant'
    function = 'function'


class Message(BaseModel):
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
    KEYWORD = 'kw'
    POS = 'pos'
    NO_ARGS = 'no_args'


class Template(BaseModel):
    """
    All init_messages will be passed to chatgpt api,
        and then if use has provided positional args, it will be sent as the last message
        otherwise if


    """
    init_messages: List[Message] = Field(default_factory=list)
    description: str = ''
    model: str = 'gpt-3.5-turbo'
    temperature: float = 1.0
    name: Optional[str] = None
    default_message: Optional[str] = None
    message_template: Optional[str] = None
    mode: List[TextFunctionMode] = Field(default_factory=list)

    def model_post_init(self, __context):
        if self.mode is None or len(self.mode) == 0:
            self.mode = []
            if self.default_message is not None:
                self.mode.append(TextFunctionMode.NO_ARGS)
            if self.message_template is not None:
                self.mode.append(TextFunctionMode.KEYWORD)
            if len(self.mode) == 0:
                self.mode.append(TextFunctionMode.POS)

    def find_call_mode(self, *args, **kwargs):
        pos_count = len(args)
        kw_count = len(kwargs)
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
    RESERVED_KEYWORDS = ['n', 'return_dict', 'extra_messages']
    template: Template

    def __init__(self, template):
        self.template = template

    def __call__(self, *args, **kwargs):
        return TextFunction._handle_call(self.template, *args, **kwargs)

    @staticmethod
    def wrap(template):
        def decorator(func):
            return TextFunction(template)

        return decorator

    @staticmethod
    def _handle_call(template, *args, **kwargs):
        all_kwargs = kwargs
        kwargs = {}
        ctrl_kws = {}
        for k, v in all_kwargs.items():
            if k in TextFunction.RESERVED_KEYWORDS:
                ctrl_kws[k] = v
            else:
                kwargs[k] = v

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

        n = ctrl_kws.get('n', 1)
        resp = openai.ChatCompletion.create(
            model=template.model,
            messages=[
                m.model_dump(exclude_none=True, mode='json') for m in messages
            ],
            temperature=template.temperature,
            n=n
        )

        if ctrl_kws.get('return_dict', False):
            return resp

        if n == 1:
            ret = resp['choices'][0]['message']['content']
            return ret
        else:
            return [c['message']['content'] for c in resp['choices']]
