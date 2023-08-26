from argparse import ArgumentParser
from os import path, system, makedirs, listdir, remove
from beautifultable import BeautifulTable
from time import sleep
from re import findall, match


arg_parser = ArgumentParser(description='command.py - a command-line tool to save and run repetitively used commands')

subparsers = arg_parser.add_subparsers(dest='command')
subparsers.required = True


subparser_new = subparsers.add_parser('new', help='Create a new shortcut')
subparser_new.add_argument('shortcut_name', help='The name of the new shortcut')
subparser_new.add_argument('--global', action='store_true', help='Create the shortcut in global scope')


subparser_run = subparsers.add_parser('run', help='Run a shortcut')
subparser_run.add_argument('shortcut_name', help='The name of the shortcut to run')
subparser_run.add_argument('runtime_arguments', nargs='?', help='The runtime arguments for the shortcut')
subparser_run.add_argument('--var', nargs='*', metavar='varname=varvalue', help='Custom variables for the shortcut')
subparser_run.add_argument('--global', action='store_true', help='Run the shortcut in global scope')


subparser_edit = subparsers.add_parser('edit', help='Edit a shortcut')
subparser_edit.add_argument('shortcut_name', help='The name of the shortcut to edit')
subparser_edit.add_argument('--global', action='store_true', help='Edit the shortcut in global scope')


subparser_list = subparsers.add_parser('list', help='List all shortcuts')
subparser_list.add_argument('--global', action='store_true', help='List all the shortcuts in global scope')


subparser_info = subparsers.add_parser('info', help='Get information about a shortcut')
subparser_info.add_argument('shortcut_name', help='The name of the shortcut to get information about')
subparser_info.add_argument('--local', action='store_true', help='Get information about the shortcut saved in global scope')


subparser_del = subparsers.add_parser('del', help='Delete a shortcut')
subparser_del.add_argument('shortcut_name', help='The name of the shortcut to delete')
subparser_del.add_argument('-y', action='store_true', help='Confirm deletion without prompt')
subparser_del.add_argument('--global', action='store_true', help='Delete a shortcut of global scope')

ARGS = arg_parser.parse_args()
#print(ARGS)
if hasattr(ARGS, "shortcut_name"):
    if not match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', ARGS.shortcut_name):
        print(f"invalid shortcut name \"{ARGS.shortcut_name}\" ")
        exit(1)

SHORTCUTS_LOCAL_DIR = path.join('.', ".command-shortcuts")
SHORTCUTS_GLOBAL_DIR = path.join(path.expanduser('~'), ".command-shortcuts")

if (not path.exists(SHORTCUTS_LOCAL_DIR)):
    makedirs(SHORTCUTS_LOCAL_DIR)
if (not path.exists(SHORTCUTS_GLOBAL_DIR)):
    makedirs(SHORTCUTS_GLOBAL_DIR)

def _shortcut_filename(SHORTCUT_NAME, GLOBAL_SCOPE = getattr(ARGS, "global", False)):
    SHORTCUTS_DIR = SHORTCUTS_GLOBAL_DIR if GLOBAL_SCOPE else SHORTCUTS_LOCAL_DIR
    return path.join(SHORTCUTS_DIR, ARGS.shortcut_name+".command-shortcut")

def _auto_get_shortcut_filename(SHORTCUT_NAME):
    if getattr(ARGS, "global", False):
        if not path.exists(shortcut_filename:=(_shortcut_filename(ARGS.shortcut_name, True))):
            print(f"no shortcut found with name \"{ARGS.shortcut_name}\" in global scope")
        else:
            return shortcut_filename
    else:
        if not path.exists(shortcut_filename:=(_shortcut_filename(ARGS.shortcut_name, False))):
            print(f"no shortcut found with name \"{ARGS.shortcut_name}\" in local scope")
        else:
            return shortcut_filename
        if not path.exists(shortcut_filename:=(_shortcut_filename(ARGS.shortcut_name, True))):
            print(f"no shortcut found with name \"{ARGS.shortcut_name}\" in global scope")
        else:
            return shortcut_filename
    exit(1)
def create_new_shortcut():
    SHORTCUT_FILENAME = _shortcut_filename(ARGS.shortcut_name)
    if path.exists(SHORTCUT_FILENAME):
        print("a shortcut with the specified name already exists...")
        exit(1)
    print(f"opening \"{SHORTCUT_FILENAME}\" in notepad...")
    with open(SHORTCUT_FILENAME, 'w')as fobj:
        print("# keep in mind, lines starting with a hashtag are treated as a comments, and you can also add custom variables with their default values as {varname(defaultvalue)})", file = fobj)
    system(f"notepad \"{SHORTCUT_FILENAME}\"")
    
def run_shortcut():
    SHORTCUT_FILENAME = _auto_get_shortcut_filename(ARGS.shortcut_name)
    provided_vars = {}
    if ARGS.var is not None:
        for var_val_str in ARGS.var:
            if len(var_val_list:=var_val_str.split("=")) == 2:
                provided_vars[var_val_list[0]] = var_val_list[1]
    with open(SHORTCUT_FILENAME, 'r') as fobj:
        for cmdline in fobj.readlines():
            if cmdline.startswith('#'):
                continue
            cmdline_vars = {match[0]:match[1] for match in findall(r'\{(\w+)\((.*?)\)\}', cmdline)}
            for var, val in cmdline_vars.items():
                if var in provided_vars:
                    newval = provided_vars[var]
                else:
                    newval = val
                cmdline = cmdline.replace("{"+var+"("+val+")}", newval)
            #print(cmdline)
            from subprocess import run
            from shlex import split
            try:
                run(split(cmdline))
            except FileNotFoundError:
                system(cmdline)
        
def edit_shortcut():
    SHORTCUT_FILENAME = _auto_get_shortcut_filename(ARGS.shortcut_name)
    print(f"opening \"{SHORTCUT_FILENAME}\" in notepad...")
    print("keep in mind, lines starting with a hashtag are treated as a comment, and you can also add custom variables with their default values as {varname(defaultvalue)})")
    sleep(1)
    system(f"notepad \"{SHORTCUT_FILENAME}\"")

def list_shortcuts():
    table = BeautifulTable()
    table.columns.header = ["S.no", "Shortcuts Name"]
    SHORTCUT_NAMES = []
    SHORTCUTS_DIR = SHORTCUTS_GLOBAL_DIR if getattr(ARGS, "global", False) else SHORTCUTS_LOCAL_DIR
    for file in listdir(SHORTCUTS_DIR):
        if path.isfile(path.join(SHORTCUTS_DIR, file)) and file.endswith(".command-shortcut"):
            SHORTCUT_NAMES.append(path.basename(path.splitext(file)[0]))
    if len(SHORTCUT_NAMES) == 0:
        print("no shortcuts found...")
        return
    for i, shortcut_name in enumerate(SHORTCUT_NAMES, start = 1):
         table.rows.append([i, shortcut_name])
    print(table)

def shortcut_info():
    if path.exists(SHORTCUT_FILENAME:=(_shortcut_filename(ARGS.shortcut_name))):
        info_table = BeautifulTable()
        info_table.columns.append(["Shortcuts Name", "Runtime Variables", "Commandlines"])
        runtime_vars_table = BeautifulTable()
        runtime_vars_table.rows.append(["Name", "Default Value"])
        commandline_table = BeautifulTable()
        commandline_table.rows.append(["line num", "Commandline"])
        commandlines_count = 0
        with open(SHORTCUT_FILENAME, 'r') as fobj:
            var_count = 0
            for cmdline in fobj.readlines():
                commandlines_count += 1
                commandline_table.rows.append([commandlines_count, cmdline])
                if cmdline.startswith('#'):
                    continue
                for match in findall(r'\{(\w+)\((.*?)\)\}', cmdline):
                    runtime_vars_table.rows.append([match[0], match[1]])
                    var_count += 1
            if var_count == 0:
                print(runtime_vars_table)
                runtime_vars_table = "-"
            if commandlines_count == 0:
                print(commandline_table)
                commandline_table = "-"
        info_table.columns.append([ARGS.shortcut_name, runtime_vars_table, commandline_table])
        #info_table[2][1].align = 'l'
        print(info_table)
    else:
        print(f"no shortcut found with name \"{ARGS.shortcut_name}\"...")
    
def delete_shortcut():
    if path.exists(shortcut_filename:=(_shortcut_filename(ARGS.shortcut_name))):
        if ARGS.y:
            remove(shortcut_filename)
            print(f"deleted \"{shortcut_filename}\"")
        else:
            if input("are you sure you want to delete this shortcut ? (y\\n) ").strip().lower() == "y":
                remove(shortcut_filename)
                print(f"deleted \"{shortcut_filename}\"")
            else:
                print("cancelling deletion...")
    else:
        print(f"no shortcut found with name \"{ARGS.shortcut_name}\"...")

match (ARGS.command):
    case "new":
        create_new_shortcut()
    case "run":
        run_shortcut()
    case "edit":
        edit_shortcut()
    case "list":
        list_shortcuts()
    case "info":
        shortcut_info()
    case "del":
        delete_shortcut()


