import json
import os
import importlib

from slambda.core import LmFunction


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


def list_functions():
    import slambda.contrib
    contrib_dir = slambda.contrib.__path__[0]
    all_function_scripts = list_scripts(contrib_dir, recursive=True)
    results = []
    for module_path in all_function_scripts:
        fip = f"slambda.contrib.{module_path}"
        # print(f"Extracting {fip}..")
        fns = get_function(fip)
        for fn in fns:
            results.append(dict(module_name=module_path, function_name=fn['name']))
    return results


def get_function(name):
    fn_module = importlib.import_module(name)
    fns = []
    for item_name in dir(fn_module):
        item = getattr(fn_module, item_name)
        if isinstance(item, LmFunction):
            fns.append({
                "name": item_name,
                "template": item.definition.model_dump(mode='json', exclude_none=True)
            })
    return fns


def run():
    print(json.dumps(list_functions()))


if __name__ == '__main__':
    run()
