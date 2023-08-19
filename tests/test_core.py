import json
import unittest
from unittest import TestCase
import unittest.mock as mock

from src.slambda.core import Definition, TextFunction, TextFunctionMode, Message, Role, Example, \
    extract_required_keywords, try_parse_json


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


def side_effect_json_function(**kwargs):
    # You can define your custom logic here based on kwargs
    # This is a simple example which returns different text based on the model
    if kwargs.get('n', 1) == 1:
        return {
            'choices': [
                {
                    'message': {
                        'content': json.dumps({'k': 0})
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
                        'content': json.dumps({'k': i})
                    }
                }
            )

        return dict(choices=choices)


def create_fake_response(i):
    return f"MODEL OUTPUT #{i}"


class TestTextFunction(TestCase):
    @mock.patch('openai.ChatCompletion.create')
    def test_missing_kws(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function
        fd = Definition(
            messages=list(),
            mode=[TextFunctionMode.KEYWORD],
            required_args=['age', 'name']
        )

        f = fd.fn()
        f(age=12, name='jack')
        f(age=12, name='jack', msg='hello')
        with self.assertRaises(ValueError) as context:
            f('')
        with self.assertRaises(ValueError) as context:
            f(age='')

    @mock.patch('openai.ChatCompletion.create')
    def test_str_message(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function
        fd = Definition(
            messages=list(),
            mode=[TextFunctionMode.POS],
        )

        f = fd.fn()

        with self.assertRaises(ValueError) as context:
            f('', extra_messages=['hello'])

        f('', extra_messages=[Message.system('123')])

    @mock.patch('openai.ChatCompletion.create')
    def test_multiple_pos_args(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function
        fd = Definition(
            messages=list(),
            mode=[TextFunctionMode.POS],
        )

        f = fd.fn()

        with self.assertRaises(ValueError) as context:
            f('', '123')

        f('')

    @mock.patch('openai.ChatCompletion.create')
    def test_fun_no_args(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function

        f = TextFunction(Definition(
            init_messages=[
                Message.system('A system message')
            ],
            default_message='this receive no arg',
            mode=[TextFunctionMode.NO_ARGS]
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

        out = f(return_resp_obj=True)
        self.assertEqual(dict(choices=[
            {
                'message': {
                    'content': f"ONLY MODEL OUTPUT"
                }
            }
        ]), out)

        out = f(return_resp_obj=True, __override={"n": 2})
        self.assertEqual(dict(choices=[
            {
                'message': {
                    'content': "MODEL OUTPUT #0"
                }
            },
            {
                'message': {
                    'content': "MODEL OUTPUT #1"
                }
            }
        ]), out)

    @mock.patch('openai.ChatCompletion.create')
    def test_fun_pos_arg(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function

        f = TextFunction(Definition(
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
        f = TextFunction(Definition(
            init_messages=[
                Message.system('A system message')
            ],
            message_template='arg 1: {name}, arg 2: {age}',
            mode=[TextFunctionMode.KEYWORD]
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
    def test_json_out(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_json_function
        f = TextFunction(Definition(
            mode=[TextFunctionMode.POS],
            json_output=True
        ))

        self.assertTrue(f.definition.json_output)

        out = f('hello')
        self.assertDictEqual({'k': 0}, out)

        out = f('hello', __override={"n": 2})
        self.assertListEqual([
            {'k': 0},
            {'k': 1}
        ], out)

    @mock.patch('openai.ChatCompletion.create')
    def test_json_out_failed(self, mock_openai_api):
        mock_openai_api.side_effect = side_effect_function
        f = TextFunction(Definition(
            mode=[TextFunctionMode.POS],
            json_output=True
        ))

        self.assertTrue(f.definition.json_output)

        with self.assertWarns(UserWarning) as context:
            out = f('hello')
            self.assertEqual('ONLY MODEL OUTPUT', out)


class TestDefinition(TestCase):
    def test_model_post_init_no_arg(self):
        t = Definition(
            default_message='this receive no arg',
            mode=[TextFunctionMode.NO_ARGS]
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
        t = Definition(
            messages=list(),
            mode=[TextFunctionMode.POS]
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
        t = Definition(
            message_template='arg 1: {name}, arg 2: {age}',
            mode=[TextFunctionMode.KEYWORD]
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
        t = Definition(
            default_message='this receive no arg',
            message_template='arg 1: {name}, arg 2: {age}',
            mode=[TextFunctionMode.NO_ARGS, TextFunctionMode.KEYWORD]
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
            Definition(
                mode=[TextFunctionMode.NO_ARGS]
            ).find_call_mode()

        self.assertEqual(
            'Function cannot be called with no args, because default_message is None.', str(context.exception))

        self.assertNotEqual(
            'Function because default_message is None.', str(context.exception))

    def test_fn(self):
        fd = Definition(
            messages=list(),
            mode=[TextFunctionMode.POS]
        )

        f = fd.fn()
        f1 = TextFunction(fd)
        self.assertEqual(f1.definition, f.definition)


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


class TestUtils(TestCase):
    def test_extract_required_keywords(self):
        ns = extract_required_keywords('{name} is {age} years old.')
        self.assertListEqual(['name', 'age'], ns)

    def test_try_parse_json(self):
        d = try_parse_json('{"k": 0}')
        self.assertDictEqual({"k": 0}, d)


if __name__ == '__main__':
    unittest.main()
