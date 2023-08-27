import unittest
from unittest import TestCase
from slambda import Role, Message


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
