import datetime
import json
import sqlite3
import uuid
from enum import Enum
from typing import Dict, Union, Optional, List, Tuple
from pydantic import BaseModel, Field
from flask import Flask, jsonify, request

from slambda import TextFunction, Definition
import openai


class ValueType(str, Enum):
    json = 'json'
    string = 'string'
    none = 'none'


class NamedDefinition(BaseModel):
    name: str
    definition: Definition


class PlayGroundStatus(BaseModel):
    has_key: bool
    fns: List[NamedDefinition]


class FnResult(BaseModel):
    value: Optional[Union[str, Dict]] = None


class FnRequest(BaseModel):
    name: str
    input: Optional[Union[str, Dict]] = None


class LogEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input_type: ValueType
    output_type: ValueType
    input_data: Optional[Union[str, Dict]] = None
    output_data: Optional[Union[str, Dict]] = None
    ts: datetime.datetime

    def normalize_to_db_entry(self) -> 'LogEntry':
        input_data, input_type = to_string_or_none(self.input_data, self.input_type)
        output_data, output_type = to_string_or_none(self.output_data, self.output_type)
        return LogEntry(
            entry_id=self.entry_id,
            input_data=input_data, input_type=input_type,
            output_data=output_data, output_type=output_type,
            ts=self.ts
        )


def try_cast(value, value_type: ValueType):
    if value_type == ValueType.json:
        pass
    elif value_type == ValueType.string:
        pass
    elif value_type == ValueType.none:
        pass


def to_string_or_none(value, value_type: ValueType) -> Tuple[Optional[str], ValueType]:
    if value_type == ValueType.json:
        if isinstance(value, dict):
            return json.dumps(value), ValueType.string
        if isinstance(value, dict):
            return json.dumps(value), ValueType.string

    elif value_type == ValueType.string:
        return value, ValueType.string
    elif value_type == ValueType.none:
        return value, ValueType.string


class LogEntryController:

    def __init__(self, dp_path=None, conn=None):
        if conn is not None:
            self.conn = conn
        else:
            if dp_path is None:
                dp_path = '.slambda-playground-log.db'
            self.conn = sqlite3.connect(dp_path)
        self.create_table()

    def create_table(self):
        """
        Create the log entry table if it does not exist
        """
        query = '''
        CREATE TABLE IF NOT EXISTS log_entries (
            entry_id TEXT PRIMARY KEY,
            input_type TEXT,
            output_type TEXT,
            input_data TEXT,
            output_data TEXT,
            ts TIMESTAMP
        );
        '''
        self.conn.execute(query)
        self.conn.commit()

    def add_log_entry(self, entry: LogEntry):
        """
        Add a log entry to the database
        :param entry: LogEntry object
        """
        query = '''
        INSERT INTO log_entries (entry_id, input_type, output_type, input_data, output_data, ts)
        VALUES (?, ?, ?, ?, ?, ?);
        '''
        values = (
            entry.entry_id,
            entry.input_type.value,
            entry.output_type.value,
            entry.input_data,
            entry.output_data,
            entry.ts
        )
        self.conn.execute(query, values)
        self.conn.commit()

    def list_log_entries(self, page: int, entries_per_page: int = 20) -> List[LogEntry]:
        """
        List log entries, sorted by `ts`
        :param page: Page number
        :param entries_per_page: Number of entries per page
        :return: List of LogEntry objects
        """
        query = '''
        SELECT entry_id, input_type, output_type, input_data, output_data, ts
        FROM log_entries
        ORDER BY ts DESC
        LIMIT ? OFFSET ?;
        '''
        offset = (page - 1) * entries_per_page
        values = (entries_per_page, offset)
        cursor = self.conn.execute(query, values)
        entries = [
            LogEntry(
                entry_id=row[0],
                input_type=ValueType(row[1]),
                output_type=ValueType(row[2]),
                input_data=row[3],
                output_data=row[4],
                ts=row[5]
            )
            for row in cursor.fetchall()
        ]
        return entries

    def remove_log_entries(self, entry_id_list: List[str]):
        """
        Remove specified log entries from the database
        :param entry_id_list: List of entry IDs to be removed
        """
        if not entry_id_list:
            return

        placeholders = ','.join(['?'] * len(entry_id_list))
        query = f'DELETE FROM log_entries WHERE entry_id IN ({placeholders});'
        self.conn.execute(query, tuple(entry_id_list))
        self.conn.commit()


class PlayGroundApp:
    fns: Dict[str, TextFunction]

    def __init__(self, fns):
        self.fns = fns
        self.app = Flask(__name__)
        self.add_routes()

    def add_routes(self):
        app = Flask(__name__, static_folder='app', static_url_path="/app")

        @self.app.route('/api/inference', methods=['POST'])
        def inference():
            item_data = request.json
            fn_request = FnRequest(**item_data)
            fn = self.fns.get(fn_request.name, None)
            out = None
            if fn_request.input is None:
                out = fn()
            elif isinstance(fn_request.input, dict) is None:
                out = fn(**fn_request.input)
            elif isinstance(fn_request.input, str) is None:
                out = fn(fn_request.input)

            return jsonify(FnResult(value=out).model_dump(mode='json')), 200

        @self.app.route('/api/status', methods=['GET'])
        def get_system_status():
            has_key = openai.api_key is not None or openai.api_key_path is not None
            status = PlayGroundStatus(
                has_key=has_key,
                fns=[NamedDefinition(nname=n, definition=f.definition) for n, f in self.fns.items()]
            )
            return jsonify(status.model_dump(mode='json')), 200

        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            page = int(request.args.get('page', '1'))
            has_key = openai.api_key is not None or openai.api_key_path is not None
            status = PlayGroundStatus(
                has_key=has_key,
                fns=[NamedDefinition(nname=n, definition=f.definition) for n, f in self.fns.items()]
            )
            return jsonify(status.model_dump(mode='json')), 200

        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def catch_all(path):
            return self.app.send_static_file("index.html")

    def run(self, **kwargs):
        if 'port' not in kwargs:
            kwargs['port'] = 6767
        self.app.run(**kwargs)
