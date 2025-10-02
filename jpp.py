import json
import argparse
import sys
import gjp
try:
    from colorama import Fore, Style, init
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def pretty_print_json(json_data):
    try:
        # Parse the JSON data
        parsed_json = gjp.parse(json_data)
        
        # Pretty print the JSON with colors
        print_json(parsed_json)
    except json.JSONDecodeError as e:
        print(Fore.RED + f"Invalid JSON: {e}")

def print_json(data, indent=0):
    if isinstance(data, dict):
        print(Fore.CYAN + '{')
        for key, value in data.items():
            print(Fore.YELLOW + ' ' * (indent + 2) + f'"{key}": ', end='')
            print_json(value, indent + 2)
        print(Fore.CYAN + ' ' * indent + '}')
    elif isinstance(data, list):
        print(Fore.CYAN + '[')
        for item in data:
            print(Fore.YELLOW + ' ' * (indent + 2), end='')
            print_json(item, indent + 2)
        print(Fore.CYAN + ' ' * indent + ']')
    else:
        print(Fore.WHITE + str(data))


if __name__ == "__main__":
    try:
        assert len(sys.argv[1:]) > 1
        #parser = argparse.ArgumentParser(description=r"""Read the MS malformed JSON in logs
#""")
        #parser.add_argument('fields',
#                            type=str,
#                            nargs='*',
#                            help='json fields to look for') 
        #args = parser.parse_args()
        #print(args.fields[0])
        #lines = gjp.mgsplit(args.fields, debug=True)
        lines = []
        print('jpp.py interactive mode, paste lines and then press CTRL D to end input')
        run = True
        while run:
            inp = input()
            if '\x04' in inp:
                inp = inp.replace('\x04','')
                run = False 
            lines.append(inp)
        lines = '\n'.join(lines)
        lines = gjp.mgsplit(lines, debug=True)
    except AssertionError:
        lines = gjp.mgsplit(sys.stdin.read(), debug=False)
    #print(lines)
    for line in lines:
        try:
            pretty_print_json(line)
        except BaseException:
            print(line)
