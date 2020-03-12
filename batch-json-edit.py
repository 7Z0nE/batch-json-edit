import argparse
import json
import os


def parse_folder(root, recursive=False):
    files = [os.path.join(root, name) for name in os.listdir(root) if not os.path.isdir(name)]
    folders = [os.path.join(root, name) for name in os.listdir(root) if os.path.isdir(name)]
    if recursive:
        for folder in folders:
            files += parse_folder(folder, recursive=recursive)
    return files 


def parse_files(paths, recursive=False):
    files = []
    for path in paths:
        if os.path.isdir(path):
            files += parse_folder(path, recursive=recursive)
        else:
            files.append(path)
    return files


def load_json(files):
    jsons = []
    for path in files:
        with open(path) as f:
            jsons.append(json.load(f))
    return jsons


def get_json_nested(json, attr):
    attrs = attr.split('.')
    res = json[attrs[0]]
    for a in attrs[1:]:
        res = res[a]
    return res


def set_json_nested(json, attr, value):
    attrs = attr.split('.')
    res = json[attrs[0]]
    for a in attrs[1:-1]:
        if not a in res:
            res[a] = {}
        else:
            res = res[a]
    res[attrs[-1]] = value


def delete_json_nested(json, attr):
    attrs = attr.split('.')
    res = json[attrs[0]]
    for a in attrs[1:-1]:
        if not a in res:
            print(res, a)
            return
        else:
            res = res[a]
    res.pop(attrs[-1], None)


parser = argparse.ArgumentParser('Edit multiple json files of similar structure simultaneously.')
subparsers = parser.add_subparsers(title='command', dest='command')

add_parser = subparsers.add_parser('add', help='Adds an attribute to the specified json files. Errors if the attribute already exists.')
edit_parser = subparsers.add_parser('edit', help='Edits an attribute. Errors if the attribute does not exist in all files.')
set_parser = subparsers.add_parser('set', help='Sets an attribute. Ignores whether is already existed or not.')
delete_parser = subparsers.add_parser('delete', help='Deletes an attribute. Ignores whether it already exists or not.')

set_parser.add_argument('field', help='Path to the field to set. E.g. x.y.myfield.')
set_parser.add_argument('value', help='value to write to the field')
set_parser.add_argument('files', nargs='+', help='files and folders containing json files to edit')
set_parser.add_argument('--recursive', nargs='?', default='False', help='whether to recurse into folder of folders')

delete_parser.add_argument('field', help='Path to the field to delete. E.g. x.y.myfield.')
delete_parser.add_argument('files', nargs='+', help='files and folders containing json files to edit')
delete_parser.add_argument('--recursive', nargs='?', type=bool, default='False', help='whether to recurse into folder of folders')

args = parser.parse_args()

files = parse_files(args.files, recursive=args.recursive)
jsons = load_json(files)
print(files)
for j in jsons:
    if args.command == 'set':
        set_json_nested(j, args.field, args.value)
    elif args.command == 'delete':
        delete_json_nested(j, args.field)

for f, j in zip(files, jsons):
    with open(f, 'w') as ff:
        json.dump(j, ff, indent=4, sort_keys=False)

