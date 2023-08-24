import datetime
import importlib
import json
import sqlite3
import uuid
import zipfile
from enum import Enum
from typing import Dict, Union, Optional, List, Tuple
from pydantic import BaseModel, Field
from flask import Flask, jsonify, request, Response
import importlib.resources as pkg_resources
import mimetypes

from slambda import TextFunction, Definition
import openai

from slambda.core import try_parse_json


def load_fn_by_name(module_name, function_name):
    full_import_path = f"slambda.contrib.{module_name}"
    fn_module = importlib.import_module(full_import_path)
    return getattr(fn_module, function_name)


DEFAULT_FNS = [
    "sentiment:sentiment",
    "entail:entail",
    "summarize:summarize",
    "motivate:motivate_me",
    "wiki_link:extract_wiki_links",
    "writing.grammar:fix_grammar",
    "writing.essay:generate_essay"
]


def build_default_playground_fns():
    ret = {}
    for item in DEFAULT_FNS:
        module_name, function_name = item.split(':')
        fn = load_fn_by_name(module_name, function_name)
        ret[f"{module_name}.{function_name}"] = fn
    return ret


class ValueType(str, Enum):
    json = 'json'
    string = 'string'
    none = 'none'

    @staticmethod
    def of_value(value):
        if value is None:
            return ValueType.none
        elif isinstance(value, str):
            return ValueType.string
        elif isinstance(value, dict):
            return ValueType.json


class NamedDefinition(BaseModel):
    name: str
    definition: Definition


class PlayGroundStatus(BaseModel):
    has_key: bool
    fns: List[NamedDefinition]


class FnResult(BaseModel):
    type: ValueType
    value: Optional[Union[str, Dict, List]] = None

    @staticmethod
    def from_value(value):
        return FnResult(value=value, type=ValueType.of_value(value))


class FnRequest(BaseModel):
    name: str
    input: Optional[Union[str, Dict]] = None


class LogEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    fn_name: str
    input_type: ValueType
    output_type: ValueType
    input_data: Optional[Union[str, Dict]] = None
    output_data: Optional[Union[str, Dict, List]] = None
    ts: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())

    def normalize_to_db_entry(self) -> 'LogEntry':
        """
        Case input and output to string.
        :return:
        """
        input_data, input_type = to_string_or_none(self.input_data, self.input_type)
        output_data, output_type = to_string_or_none(self.output_data, self.output_type)
        return LogEntry(
            fn_name=self.fn_name,
            entry_id=self.entry_id,
            input_data=input_data, input_type=input_type,
            output_data=output_data, output_type=output_type,
            ts=self.ts
        )

    def normalize_to_api_entry(self) -> 'LogEntry':
        """
        Case input and output according to its value type.
        :return:
        """
        input_data, input_type = try_cast(self.input_data, self.input_type)
        output_data, output_type = try_cast(self.output_data, self.output_type)
        return LogEntry(
            fn_name=self.fn_name,
            entry_id=self.entry_id,
            input_data=input_data, input_type=self.input_type,
            output_data=output_data, output_type=self.output_type,
            ts=self.ts
        )


class LogEntryListingResult(BaseModel):
    entries: List[LogEntry]


def try_cast(value, value_type: ValueType) -> Tuple[Optional[Union[str, Dict]], ValueType]:
    """
    Case value according to its value_type.

    :param value:
    :param value_type:
    :return:
    """
    if value_type == ValueType.json:
        if value is None:
            v = None
            return v, ValueType.of_value(v)
        elif isinstance(value, str):
            v = try_parse_json(value)
            return v, ValueType.of_value(v)
        elif isinstance(value, dict):
            v = value
            return v, ValueType.of_value(v)

    elif value_type == ValueType.string:
        if value is None:
            return '', ValueType.string
        elif isinstance(value, str):
            return value, ValueType.string
        elif isinstance(value, dict):
            return json.dumps(value), ValueType.string

    elif value_type == ValueType.none:
        if value is None:
            return None, ValueType.none
        elif isinstance(value, str):
            return None, ValueType.none
        elif isinstance(value, dict):
            return None, ValueType.none


def to_string_or_none(value, value_type: ValueType) -> Tuple[Optional[str], ValueType]:
    """
    Encode value to string
    :param value:
    :param value_type:
    :return:
    """
    if value_type == ValueType.json:
        if isinstance(value, dict):
            return json.dumps(value), value_type
        if isinstance(value, list):
            return json.dumps(value), value_type

    elif value_type == ValueType.string:
        return value, value_type
    elif value_type == ValueType.none:
        return value, value_type


class LogEntryController:

    def __init__(self, dp_path=None, conn=None):
        if conn is not None:
            self.conn = conn
        else:
            if dp_path is None:
                dp_path = '.slambda-playground-log.db'
            self.conn = sqlite3.connect(dp_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        """
        Create the log entry table if it does not exist
        """
        query = '''
        CREATE TABLE IF NOT EXISTS log_entries (
            entry_id TEXT PRIMARY KEY,
            fn_name TEXT,
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
        INSERT INTO log_entries (entry_id, fn_name, input_type, output_type, input_data, output_data, ts)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        '''

        entry = entry.normalize_to_db_entry()

        values = (
            entry.entry_id,
            entry.fn_name,
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
        SELECT entry_id, fn_name, input_type, output_type, input_data, output_data, ts
        FROM log_entries
        ORDER BY ts DESC
        LIMIT ? OFFSET ?;
        '''
        offset = (page - 1) * entries_per_page
        values = (entries_per_page, offset)
        cursor = self.conn.execute(query, values)
        entries = [

        ]

        for row in cursor.fetchall():
            entry_id, fn_name, input_type, output_type, input_data, output_data, ts = row
            e = LogEntry(
                entry_id=entry_id,
                fn_name=fn_name,
                input_type=input_type,
                output_type=output_type,
                input_data=input_data,
                output_data=output_data,
                ts=ts,
            ).normalize_to_api_entry()
            entries.append(e)
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


class PlaygroundApp:
    fns: Dict[str, TextFunction]

    @staticmethod
    def open(fn: TextFunction, name: Optional[str] = None, auto_run=True, **kwargs):
        if name is None:
            name = fn.definition.name
            if name is None or name == '':
                name = 'Playground Function'

        fns = {name: fn}
        app = PlaygroundApp(fns)
        if auto_run:
            app.run(**kwargs)
        return app

    @staticmethod
    def open_function_dict(fns: Dict[str, TextFunction], auto_run=True, **kwargs):
        app = PlaygroundApp(fns)
        if auto_run:
            app.run(**kwargs)
        return app

    def __init__(self, fns=None):
        if fns is None:
            fns = build_default_playground_fns()
        self.fns = fns
        self.log_controller = LogEntryController()
        self.app = Flask(__name__, static_folder=None)
        self.add_routes()

    def add_routes(self):
        self.load_frontend()

        @self.app.route('/api/inference', methods=['POST'])
        def inference():
            item_data = request.json
            fn_request = FnRequest(**item_data)
            fn = self.fns.get(fn_request.name, None)
            out = None
            if fn_request.input is None:
                out = fn()
            elif isinstance(fn_request.input, dict):
                out = fn(**fn_request.input)
            elif isinstance(fn_request.input, str):
                out = fn(fn_request.input)

            self.log_controller.add_log_entry(LogEntry(
                fn_name=fn_request.name,
                input_type=ValueType.of_value(fn_request.input),
                input_data=fn_request.input,
                output_type=ValueType.of_value(out),
                output_data=out,
            ))

            return jsonify(FnResult.from_value(out).model_dump(mode='json')), 200

        @self.app.route('/api/status', methods=['GET'])
        def get_system_status():
            has_key = openai.api_key is not None or openai.api_key_path is not None
            status = PlayGroundStatus(
                has_key=has_key,
                fns=[NamedDefinition(name=n, definition=f.definition) for n, f in self.fns.items()]
            )
            return jsonify(status.model_dump(mode='json')), 200

        @self.app.route('/api/inference-log', methods=['GET'])
        def get_logs():
            page = int(request.args.get('page', '1'))
            entries = self.log_controller.list_log_entries(page)
            r = LogEntryListingResult(entries=[e for e in entries])
            return jsonify(r.model_dump(mode='json')), 200

        @self.app.route('/', defaults={'path': ''})
        @self.app.route("/<string:path>")
        @self.app.route('/<path:path>')
        def catch_all(path):
            fp = 'build/' + path
            if fp not in self.frontend_assets:
                fp = 'build/index.html'
            mime_type, _ = mimetypes.guess_type(fp)
            content_bytes = self.frontend_assets[fp]
            if mime_type is None:
                mime_type = 'application/octet-stream'
            return Response(content_bytes, content_type=mime_type)

    def run(self, **kwargs):
        host = kwargs.get('host', '127.0.0.1')
        if 'port' not in kwargs:
            kwargs['port'] = 6767
        print(f'Starting playground at http://{host}:{kwargs["port"]}')
        self.app.run(**kwargs)

    def load_frontend(self):
        self.frontend_assets = {}
        with pkg_resources.path("slambda.data", 'playground.frontend') as asset_zip_path:
            with zipfile.ZipFile(asset_zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.is_dir():
                        continue
                    with zip_ref.open(file_info) as file:
                        file_content = file.read()
                        self.frontend_assets[file_info.filename] = file_content
        pass


if __name__ == '__main__':
    app = PlaygroundApp()
    app.run()
