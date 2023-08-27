import sqlite3
import unittest
from datetime import datetime
from unittest import TestCase

from slambda.playground import LogEntryController, LogEntry, ValueType, try_cast, to_string_or_none


class TestLogEntryController(TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')  # Create an in-memory database for testing
        self.controller = LogEntryController(conn=self.conn)

    def tearDown(self):
        self.conn.close()

    def test_create_table(self):
        self.controller.create_table()
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        self.assertIn('log_entries', tables)

    def test_add_log_entry(self):
        entry = LogEntry(
            fn_name='fn',
            input_type=ValueType.json,
            output_type=ValueType.string,
            input_data={"key": "value"},
            output_data='result',
            ts=datetime.now()
        )
        self.controller.add_log_entry(entry)
        cursor = self.conn.execute("SELECT COUNT(*) FROM log_entries;")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)

    def test_list_log_entries(self):
        entry = LogEntry(
            fn_name='fn',
            input_type=ValueType.json,
            input_data={"key": "value"},
            output_type=ValueType.string,
            output_data='result',
            ts=datetime.now()
        )
        self.controller.add_log_entry(entry)
        entries = self.controller.list_log_entries(page=1, entries_per_page=10)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].input_type, ValueType.json)

    def test_remove_log_entries(self):
        entry = LogEntry(
            fn_name='fn',

            input_type=ValueType.json,
            input_data={"key": "value"},

            output_type=ValueType.string,
            output_data='result',
            ts=datetime.now()
        )
        self.controller.add_log_entry(entry)
        cursor = self.conn.execute("SELECT entry_id FROM log_entries;")
        entry_id = cursor.fetchone()[0]
        self.controller.remove_log_entries([entry_id])
        cursor = self.conn.execute("SELECT COUNT(*) FROM log_entries;")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 0)


class TestCasting(TestCase):
    def test_try_cast(self):
        casted = try_cast(None, ValueType.json)
        self.assertEqual(casted, None)

        casted = try_cast("{}", ValueType.json)
        self.assertEqual({}, casted)

        casted = try_cast({}, ValueType.json)
        self.assertEqual({}, casted)

        casted = try_cast(None, ValueType.string)
        self.assertEqual(casted, '')

        casted = try_cast("{}", ValueType.string)
        self.assertEqual('{}', casted)

        casted = try_cast({}, ValueType.string)
        self.assertEqual('{}', casted)

        casted = try_cast(None, ValueType.none)
        self.assertEqual(casted, None)

        casted = try_cast("{}", ValueType.none)
        self.assertEqual(casted, None)

        casted = try_cast({}, ValueType.none)
        self.assertEqual(casted, None)

    def test_to_string_or_none(self):
        v = to_string_or_none({}, ValueType.json)
        self.assertEqual(v, '{}')


if __name__ == '__main__':
    unittest.main()
