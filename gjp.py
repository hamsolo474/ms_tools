import sys
import argparse

#Example usage
# C:\Users\v-micgilmore\Documents\Customer\2507230030005039\PBIDesktopDiagnosticInfo.20250724T144038>grep -rni "incident" | grep -i "category" | grep "DAXQuery" | grep DataMashup | gjp.py message

def mgparse(text, debug=False):
    """
Count all the quotes, keeping count of how many opens to closes there are,
when there is only one open quote left, next close sig is a whole value
    """
    q = '"'
    quotes = []
    opdic = {}
    keys = []
    for index, char in enumerate(text):
        if char == q:
            if debug: print(f'index {index} is {q}, {len(quotes)}')
            if debug: print(f"quotes: {quotes}")
            if text[index+1] in (',',':'):
                if len(quotes) > 1: #If theres a nested closing quote
                    if debug: print(f"popped: {quotes[-1]}")
                    quotes.pop()
                elif len(quotes) == 1: #The last closing quote
                    if debug: print(f" final: {text[quotes[-1]:index+1]}")
                    if text[index+1] == ':':
                        keys.append(text[quotes.pop()+1:index])
                    else:
                        opdic[keys.pop()] = text[quotes.pop()+1:index].replace('\\\\','\\')
            else: # All opening quotes
                quotes.append(index)
    opdic['file'] = text[:text.find('{')].strip()
    return opdic

parser = argparse.ArgumentParser(description=r"""Read the MS malformed JSON in logs
Usage example:
C:\Users\v-micgilmore\Documents\Customer\2507230030005039\PBIDesktopDiagnosticInfo.20250724T144038>grep -rni "incident" | grep -i "category" | grep "DAXQuery" | grep DataMashup | gjp.py message
""")
parser.add_argument('fields',
                    type=str,
                    nargs='*',
                    help='json fields to look for')
parser.add_argument('--keys',
                    action = "store_true",
                    default=False,
                    help="print keys")
parser.add_argument('--space',
                    action = "store_true",
                    default=False,
                    help="put newline between results")
parser.add_argument('--not-strict',
                    action = "store_true",
                    default=False,
                    help="only print lines with all values present")
parser.add_argument('--delimeter',
                    type = str,
                    default="\t",
                    help="which delimiter to use tab, comma, colon etc..")
parser.add_argument('--print-headers',
                    action = "store_true",
                    default=False,
                    help="Print headers")



args = parser.parse_args()

lines=sys.stdin.read().split('"}')

obj = None
keys = []


if args.delimeter.lower() == 'tab':
    args.delimeter = '\t'
if args.print_headers:
    print(args.delimeter.join(args.fields))
    
for i in lines:
    try:
        obj = mgparse(i)
        keys.extend(obj.keys())
        op = []
        for target in args.fields:
            try:
                #obj[target]
                result = obj[target].strip()
                if len(result) == 0:
                    break
                op.append(obj[target])
            except KeyError:
                pass
        if len(op) == len(args.fields) and not args.keys:
            print(args.delimeter.join(op))
        #try:
        #    if len(obj[target].strip()) > 0: print('')
        #except NameError:
        #    pass
            #print('')
        #if args.space: print('')
    except KeyError:
        #print('')
        pass
if args.keys:
    print(sorted(set(keys)))
    exit()
