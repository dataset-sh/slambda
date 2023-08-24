import json
import os
import importlib

from slambda.core import TextFunction


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


DOC_BASE = './doc-site'


def list_functions(doc_base=DOC_BASE):
    import slambda.contrib
    contrib_dir = slambda.contrib.__path__[0]
    all_function_scripts = list_scripts(contrib_dir, recursive=True)

    for fn in all_function_scripts:
        print(f"Extracting {fn}..")
        fip = f"slambda.contrib.{fn}"
        fns = get_function(fip)
        json_data = {
            'fns': fns,
            'module_name': fip,
        }

        if '.' in fn:
            base_module_name, func_name = fn.split('.')
            json_base = os.path.join(doc_base, 'src', 'data', base_module_name)
            os.makedirs(json_base, exist_ok=True)
            json_path = os.path.join(doc_base, 'src', 'data', base_module_name, f"{func_name}.json")
            module_base = os.path.join(doc_base, 'docs', 'functions', base_module_name)
            doc_path = os.path.join(doc_base, 'docs', 'functions', base_module_name, f"{func_name}.mdx")
            ensure_doc_parent_exists(module_base, base_module_name)
            ensure_doc_exists(doc_path, name=func_name, path=f"{base_module_name}/{func_name}")
        else:
            func_name = fn
            json_path = os.path.join(doc_base, 'src', 'data', f"{func_name}.json")
            doc_path = os.path.join(doc_base, 'docs', 'functions', f"{func_name}.mdx")
            ensure_doc_exists(doc_path, name=func_name, path=func_name)

        with open(json_path, 'w') as out:
            json.dump(json_data, out)
    return all_function_scripts


DOC_TEMPLATE = """
---
title: {name}
sidebar_position: 3
---

import {{TextFnModuleView}} from "@site/src/components/TextFnTemplate"
import FnData from "@site/src/data/{path}.json"

# {name}

<TextFnModuleView
    module_name={{FnData.module_name}}
    fns={{FnData.fns}}
/>
""".strip()


def ensure_doc_exists(doc_path, name, path):
    if os.path.exists(doc_path):
        return
    else:
        with open(doc_path, 'w') as out:
            out.write(DOC_TEMPLATE.format(name=name, path=path))


def ensure_doc_parent_exists(doc_base, base_module_name):
    if os.path.exists(doc_base) and os.path.isdir(doc_base):
        return
    else:
        os.makedirs(doc_base, exist_ok=True)
        cat_json_path = os.path.join(doc_base, '_category_.json')
        with open(cat_json_path, 'w') as out:
            json.dump({
                "label": f"{base_module_name}",
                "link": {
                    "type": "generated-index"
                }
            }, out)


def get_function(name):
    fn_module = importlib.import_module(name)
    fns = []
    for item_name in dir(fn_module):
        item = getattr(fn_module, item_name)
        if isinstance(item, TextFunction):
            fns.append({
                "name": item_name,
                "template": item.definition.model_dump(mode='json', exclude_none=True)
            })
    return fns


def run():
    list_functions()


if __name__ == '__main__':
    run()
