from argparse import ArgumentParser
from re import findall, match
from os import path, getcwd, system, makedirs, listdir, remove
from subprocess import run as subprocess_run
from shlex import split as split_commandline
from beautifultable import BeautifulTable


parser = ArgumentParser(description="command.py - a command-line tool to save and run repetitively used commands")

subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

subparser_new = subparsers.add_parser("new", help="Create a new shortcut")
subparser_new.add_argument("shortcut_name", help="The name of the new shortcut")
subparser_new.add_argument("--global", action="store_true", help="Create the shortcut in global scope")

subparser_run = subparsers.add_parser("run", help="Run a shortcut.")
subparser_run.add_argument("shortcut_name", help="The name of the shortcut to run.")
subparser_run.add_argument("--var", nargs="*", metavar="varname=varvalue", help="Runtime variables for the shortcut.")
subparser_run.add_argument("--flag", nargs="*", metavar="flagname", help="Runtime Flags for the shortcut.")
subparser_run.add_argument("--global", action="store_true", help="Run the shortcut in global scope.")

subparser_edit = subparsers.add_parser("edit", help="Edit a shortcut.")
subparser_edit.add_argument("shortcut_name", help="The name of the shortcut to edit.")
subparser_edit.add_argument("--global", action="store_true", help="Edit the shortcut in global scope.")

subparser_list = subparsers.add_parser("list", help="List all shortcuts.")
subparser_list.add_argument("--global", action="store_true", help="List all the shortcuts in global scope.")

subparser_info = subparsers.add_parser("info", help="Get information about a shortcut.")
subparser_info.add_argument("shortcut_name", help="The name of the shortcut to get information about.")
subparser_info.add_argument("--global", action="store_true", help="Get information about the shortcut saved in global scope.")

subparser_del = subparsers.add_parser("del", help="Delete a shortcut.")
subparser_del.add_argument("shortcut_name", help="The name of the shortcut to delete.")
subparser_del.add_argument("-y", action="store_true", help="Confirm deletion without prompt.")
subparser_del.add_argument("--global", action="store_true", help="Delete a shortcut of global scope.")

suboarser_help = subparsers.add_parser("help", help="Display help for a command.")
suboarser_help.add_argument("command_name", help="The name of the command")

args = parser.parse_args()

if hasattr(args, "shortcut_name"):
    if not match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", args.shortcut_name):
        parser.error(f"invalid shortcut name \"{args.shortcut_name}\" ")


SHORTCUT_LOCAL_DIR = path.join(getcwd(), ".command-shortcuts")
SHORTCUT_GLOBAL_DIR = path.join(path.expanduser("~"), ".command-shortcuts")

SHORTCUT_FILE_EXTENSION = ".command-shortcut"

if hasattr(args,"shortcut_name"):

    if (not path.exists(SHORTCUT_LOCAL_DIR)):
        makedirs(SHORTCUT_LOCAL_DIR)
    if (not path.exists(SHORTCUT_GLOBAL_DIR)):
        makedirs(SHORTCUT_GLOBAL_DIR)
    
    shortcut_fname = path.join(
        SHORTCUT_GLOBAL_DIR if getattr(args, "global", False) else SHORTCUT_LOCAL_DIR,
        getattr(args, "shortcut_name") + SHORTCUT_FILE_EXTENSION
    )
    shortcut_exists = path.exists(shortcut_fname)

def error(message):
    print("Error:", message)
    exit(1)

def _error_if_file_not_found():
    if not shortcut_exists:
        error("there's no shortcut with the specified name...")

def create_new_shortcut():
    if shortcut_exists:
        error(f"a shortcut with the specified name already exists...")
    print(f"opening \"{shortcut_fname}\" in notepad...")
    open(shortcut_fname, "w").close()
    subprocess_run(["notepad.exe", shortcut_fname])

def _parse_shortcutfile():
    VAR_REGX = r'\{(\w+)\((.*?)\)\}'
    with open(shortcut_fname, 'r') as fobj:
        lines = fobj.readlines()
    input_variables = {}

    if args.var is not None:
        for varvalstr in args.var:
            if len(varvaltuple:=varvalstr.split("=")) == 2:
                input_variables[varvaltuple[0]] = varvaltuple[1]
    
    for line in lines:
        if line.startswith('#'):
            continue
        for match in findall(VAR_REGX, line):
            line = line.replace('{'+match[0]+'('+match[1]+')'+'}', input_variables.get(match[0], match[1]))
        
        yield line

def run_shortcut():
    _error_if_file_not_found()
    
    for cmdline in _parse_shortcutfile():
        try:
            subprocess_run(split_commandline(cmdline))
        except FileNotFoundError:
            system(cmdline)

def edit_shortcut():
    _error_if_file_not_found()
    print(f"opening \"{shortcut_fname}\" in notepad...")
    subprocess_run(["notepad.exe", shortcut_fname])

def list_shortcuts():
    shortcuts_table = BeautifulTable()
    shortcuts_table.columns.header = ["Shortcuts Name", "Shortcut Filename"]
    shortcuts_dirname = SHORTCUT_GLOBAL_DIR if getattr(args, "global", False) else SHORTCUT_LOCAL_DIR
    for f in listdir(shortcuts_dirname):
        f = path.join(shortcuts_dirname , f)
        if path.isfile(f) and f.endswith(SHORTCUT_FILE_EXTENSION):
            shortcuts_table.rows.append([path.basename(path.splitext(f)[0]), f])
    shortcuts_table.maxwidth = 100
    if len(shortcuts_table.rows) == 0:
        print("no shortcuts found...")
    else:
        print(shortcuts_table)

def shortcut_info():
    _error_if_file_not_found()
    VAR_REGX = r'\{(\w+)\((.*?)\)\}'
    info_table = BeautifulTable()
    info_table.rows.header = ["Shortcuts Name", "Shortcut Filename", "Runtime Variables"]
    with open(shortcut_fname, 'r') as fobj:
        lines = fobj.readlines()
    runtime_vars = {}
    for line in lines:
        if line.startswith('#'):
            continue
        for match in findall(VAR_REGX, line):
            runtime_vars[match[0]] = match[1]
    info_table.columns.append([args.shortcut_name, shortcut_fname, runtime_vars])
    info_table.maxwidth = 100
    print(info_table)

def delete_shortcut():
    _error_if_file_not_found()
    if not args.y:
        print(f"deleting this shortcut will effectively delete \"{shortcut_fname}\"")
        if input(f"are you sure you want to delete this shortcut (y\\n) ? ").strip().lower() != "y":
            exit(1)
    remove(shortcut_fname)
    print(f"Successfully removed {args.shortcut_name}")

def main():
    match (args.command):
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
        case "help":
          match args.command_name:
            case "new":
              print(subparser_new.format_help())
            case "run":
              print(subparser_run.format_help())
            case "edit":
              print(subparser_edit.format_help())
            case "list":
              print(subparser_list.format_help())
            case "info":
              print(subparser_info.format_help())
            case "del":
              print(subparser_del.format_help())
            case _:
              error("unkonown command name...")

if __name__ == "__main__":
    main()
