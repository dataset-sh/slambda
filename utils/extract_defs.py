import json
import os
import importlib

from slambda.core import Template, TextFunction


def list_scripts(base_dir, recursive=False):
    if not os.path.exists(os.path.join(base_dir, '__init__.py')):
        return []

    ret = []
    for item in os.listdir(base_dir):
        fp = os.path.join(base_dir, item)
        if os.path.isdir(fp):
            if recursive:
                for child in list_scripts(fp, recursive=False):
                    ret.append(f"{item}.{child}")
        else:
            if not item.startswith("__") and item.endswith('.py'):
                ret.append(item[:-3])
    return ret


def list_functions(doc_base='./slambda-doc'):
    import slambda.contrib
    contrib_dir = slambda.contrib.__path__[0]
    all_function_scripts = list_scripts(contrib_dir, recursive=True)

    for fn in all_function_scripts:
        fip = f"slambda.contrib.{fn}"
        templates, fns = get_function(fip)
        json_data = {
            'templates': templates,
            'fns': fns,
        }

        if '.' in fn:
            base_name, func_name = fn.split('.')
            json_base = os.path.join(doc_base, 'src', 'data', base_name)
            os.makedirs(json_base, exist_ok=True)
            json_path = os.path.join(doc_base, 'src', 'data', base_name, f"{func_name}.json")
            doc_base = os.path.join(doc_base, 'docs', 'functions', base_name)
            doc_path = os.path.join(doc_base, 'docs', 'functions', base_name, f"{func_name}.mdx")
            ensure_doc_parent_exists(doc_base)
            ensure_doc_exists(doc_path)
        else:
            func_name = fn
            json_path = os.path.join(doc_base, 'src', 'data', f"{func_name}.json")
            doc_path = os.path.join(doc_base, 'docs', 'functions', f"{func_name}.mdx")
            ensure_doc_exists(doc_path)

        with open(json_path, 'w') as out:
            json.dump(json_data, out)
    return all_function_scripts


def ensure_doc_exists(doc_path):
    if os.path.exists(doc_path):
        return
    else:
        with open(doc_path, 'w') as out:
            out.write('')


def ensure_doc_parent_exists(doc_base):
    if os.path.exists(doc_base) and os.path.isdir(doc_base):
        return
    else:
        os.makedirs(doc_base, exist_ok=True)
        cat_json_path = os.path.join(doc_base, '_category_.json')
        with open(cat_json_path, 'w') as out:
            json.dump({
                "label": f"{doc_base}",
                "link": {
                    "type": "generated-index"
                }
            }, out)


def get_function(name):
    fn_module = importlib.import_module(name)
    templates = {}
    fns = []
    for item_name in dir(fn_module):
        item = getattr(fn_module, item_name)
        if isinstance(item, Template):
            templates[item_name] = item.model_dump(mode='json', exclude_none=True)
        if isinstance(item, Template):
            fns.append(item_name)
    return templates, fns


def run():
    print(list_functions())


if __name__ == '__main__':
    run()
