import unittest
from unittest import TestCase
import unittest.mock as mock

from src.slambda.core import Template, TextFunction, TextFunctionMode, Message, Role, Example


def side_effect_function(**kwargs):
    # You can define your custom logic here based on kwargs
    # This is a simple example which returns different text based on the model
    if kwargs.get('n', 1) == 1:
        return {
            'choices': [
                {
                    'message': {
                        'content': f"ONLY MODEL OUTPUT"
                    }
                }
            ]
        }
    else:
        choices = []
        for i in range(kwargs['n']):
            choices.append(
                {
                    'message': {
                        'content': create_fake_response(i)
                    }
                }
            )

        return dict(choices=choices)


def create_fake_response(i):
    return f"MODEL OUTPUT #{i}"


class TestTextFunction(TestCase):

    @mock.patch('openai.ChatCompletion.create')
    def test_fun_no_args(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function

        f = TextFunction(Template(
            init_messages=[
                Message.system('A system message')
            ],
            default_message='this receive no arg'

        ))
        out = f()
        self.assertEqual('ONLY MODEL OUTPUT', out)

        out = f(__override={"n": 5})
        self.assertListEqual([create_fake_response(i) for i in range(5)], out)
        with self.assertRaises(ValueError) as context:
            f('', some_value=123)
        self.assertEqual('Function is called with both positional and keyword args.', str(context.exception))

        # self.assertDictEqual(, mock_openai_api.call_args_list[0])
        self.assertDictEqual(dict(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'A system message'},
                {'role': 'user', 'content': 'this receive no arg'}
            ],

        ), mock_openai_api.call_args_list[0].kwargs)

        self.assertDictEqual(dict(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'A system message'},
                {'role': 'user', 'content': 'this receive no arg'}
            ],
            n=5
        ), mock_openai_api.call_args_list[1].kwargs)

    @mock.patch('openai.ChatCompletion.create')
    def test_fun_pos_arg(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function

        f = TextFunction(Template(
            init_messages=[
                Message.system('A system message')
            ],
            default_message='this receive no arg',
            mode=[TextFunctionMode.POS]
        ))

        f('hello')

        self.assertEqual(1, len(mock_openai_api.call_args_list))
        self.assertEqual(1, mock_openai_api.call_count)

        self.assertDictEqual(dict(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'A system message'},
                {'role': 'user', 'content': 'hello'}
            ],
        ), mock_openai_api.call_args_list[0].kwargs)

    @mock.patch('openai.ChatCompletion.create')
    def test_fun_kwargs(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function
        f = TextFunction(Template(
            init_messages=[
                Message.system('A system message')
            ],
            message_template='arg 1: {name}, arg 2: {age}'
        ))
        f(name='Apple', age=10)

        self.assertEqual(1, mock_openai_api.call_count)
        self.assertEqual(1, len(mock_openai_api.call_args_list))

        self.assertDictEqual(dict(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'A system message'},
                {'role': 'user', 'content': 'arg 1: Apple, arg 2: 10'}
            ],
        ), mock_openai_api.call_args_list[0].kwargs)

    @mock.patch('openai.ChatCompletion.create')
    def test_decorator(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function

        t = Template(
            default_message='receives no arg',
        )

        @TextFunction.wrap(t)
        def f():
            pass

        f2 = TextFunction(t)
        self.assertEqual(f(), f2())


class TestTemplate(TestCase):
    def test_model_post_init_no_arg(self):
        t = Template(
            default_message='this receive no arg'
        )

        self.assertIn(TextFunctionMode.NO_ARGS, t.mode)
        self.assertEqual(1, len(t.mode))

        self.assertEqual(t.find_call_mode(), TextFunctionMode.NO_ARGS)

        with self.assertRaises(ValueError) as context:
            t.find_call_mode('')
        self.assertEqual('Calling with positional args is not allowed.', str(context.exception))

        with self.assertRaises(ValueError) as context:
            t.find_call_mode(a='')
        self.assertEqual('Calling with keyword args is not allowed.', str(context.exception))

        with self.assertRaises(ValueError) as context:
            t.find_call_mode('', a='123')
        self.assertEqual('Function is called with both positional and keyword args.', str(context.exception))

    def test_model_post_init_pos(self):
        t = Template(
            messages=list()
        )
        self.assertIn(TextFunctionMode.POS, t.mode)
        self.assertEqual(1, len(t.mode))

        self.assertEqual(t.find_call_mode(''), TextFunctionMode.POS)

        with self.assertRaises(ValueError) as context:
            t.find_call_mode()
        self.assertEqual('Calling with no args is not allowed.', str(context.exception))

        with self.assertRaises(ValueError) as context:
            t.find_call_mode(a='')
        self.assertEqual('Calling with keyword args is not allowed.', str(context.exception))

        with self.assertRaises(ValueError) as context:
            t.find_call_mode('', a='123')
        self.assertEqual('Function is called with both positional and keyword args.', str(context.exception))

    def test_model_post_init_kw(self):
        t = Template(
            message_template='arg 1: {name}, arg 2: {age}'
        )

        self.assertIn(TextFunctionMode.KEYWORD, t.mode)
        self.assertEqual(1, len(t.mode))

        self.assertEqual(t.find_call_mode(a=''), TextFunctionMode.KEYWORD)

        with self.assertRaises(ValueError) as context:
            t.find_call_mode()
        self.assertEqual('Calling with no args is not allowed.', str(context.exception))

        with self.assertRaises(ValueError) as context:
            t.find_call_mode('')
        self.assertEqual('Calling with positional args is not allowed.', str(context.exception))

        with self.assertRaises(ValueError) as context:
            t.find_call_mode('', a='123')
        self.assertEqual('Function is called with both positional and keyword args.', str(context.exception))

    def test_model_post_init_mix(self):
        t = Template(
            default_message='this receive no arg',
            message_template='arg 1: {name}, arg 2: {age}'
        )

        self.assertIn(TextFunctionMode.NO_ARGS, t.mode)
        self.assertIn(TextFunctionMode.KEYWORD, t.mode)
        self.assertEqual(2, len(t.mode))

        self.assertEqual(t.find_call_mode(), TextFunctionMode.NO_ARGS)
        self.assertEqual(t.find_call_mode(a=''), TextFunctionMode.KEYWORD)

        with self.assertRaises(ValueError) as context:
            t.find_call_mode('')
        self.assertEqual('Calling with positional args is not allowed.', str(context.exception))

        with self.assertRaises(ValueError) as context:
            t.find_call_mode('', a='123')
        self.assertEqual('Function is called with both positional and keyword args.', str(context.exception))

    def test_model_post_init_missing_default(self):
        with self.assertRaises(ValueError) as context:
            Template(
                mode=[TextFunctionMode.NO_ARGS]
            ).find_call_mode()

        self.assertEqual(
            'Function cannot be called with no args, because default_message is None.', str(context.exception))

        self.assertNotEqual(
            'Function because default_message is None.', str(context.exception))

    def test_model_post_init_missing_template(self):
        with self.assertRaises(ValueError) as context:
            Template(
                mode=[TextFunctionMode.KEYWORD]
            ).find_call_mode(a=10)
        self.assertEqual(
            'Function cannot be called with keyword args, because message_template is None.', str(context.exception))


class TestMessage(TestCase):
    def test_user(self):
        content = 'test_user content'
        name = 'test_user_user'
        expected = Message(role=Role.user, content=content, name=name)
        self.assertEqual(expected, Message.user(content, name=name))

    def test_assistant(self):
        content = 'test_assistant content'
        name = 'test_assistant_user'
        expected = Message(role=Role.assistant, content=content, name=name)
        self.assertEqual(expected, Message.assistant(content, name=name))

    def test_system(self):
        content = 'test_system content'
        name = 'test_system_user'
        expected = Message(role=Role.system, content=content, name=name)
        self.assertEqual(expected, Message.system(content, name=name))

    def test_example_user(self):
        content = 'test_example_user content'
        expected = Message(role=Role.system, content=content, name='example_user')
        self.assertEqual(expected, Message.example_user(content))

    def test_example_assistant(self):
        content = 'test_example_assistant content'
        expected = Message(role=Role.system, content=content, name='example_assistant')
        self.assertEqual(expected, Message.example_assistant(content))


if __name__ == '__main__':
    unittest.main()


class TestTemplate(TestCase):
    def test_shortcut_constructor(self):
        self.assertEqual(
            Message.system(content='A system message'),
            Message(role='system', content='A system message')
        )

        self.assertEqual(
            Message.user(content='A user message'),
            Message(role='user', content='A user message')
        )

        self.assertEqual(
            Message.assistant(content='A assistant message'),
            Message(role='assistant', content='A assistant message')
        )

        self.assertEqual(
            Message.example_user(content='A system message'),
            Message(role='system', content='A system message', name='example_user')
        )

        self.assertEqual(
            Message.example_assistant(content='A system message'),
            Message(role='system', content='A system message', name='example_assistant')
        )

    def test_follow_instruction(self):
        self.maxDiff = None
        t = Template(
            init_messages=[
                Message.system('A system message')
            ],
            default_message='this receive no arg'
        )

        self.assertListEqual(
            [Message(role='system', content='A system message')],
            t.init_messages
        )

        t.follow_instruction(
            'this is a instruction'
        )

        self.assertListEqual(
            [Message(role='system', content='this is a instruction')],
            t.init_messages
        )

        examples = [
            Example(f"i-{i}", f"o-{i}") for i in range(2)
        ]

        t.follow_instruction(
            'this is the 2nd instruction', examples
        )

        self.assertListEqual(
            [
                Message(role='system', content='this is the 2nd instruction'),
                Message(role='system', content='i-0', name='example_user'),
                Message(role='system', content='o-0', name='example_assistant'),
                Message(role='system', content='i-1', name='example_user'),
                Message(role='system', content='o-1', name='example_assistant'),
            ],
            t.init_messages
        )
