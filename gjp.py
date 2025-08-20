import sys
import argparse

#Example usage
# C:\Users\v-micgilmore\Documents\Customer\2xxxxxxxxxxxxxx9\PBIDesktopDiagnosticInfo.20250724T144038>grep -rni "incident" | grep -i "category" | grep "DAXQuery" | grep DataMashup | gjp.py message

def mgparse(text, debug=False):
    """
Count all the quotes, keeping count of how many opens to closes there are,
when there is only one open quote left, next close sig is a whole value
    """
    q = '"'
    quotes = []
    opdic = {}
    keys = []
    #text = text.replace('\"','"')
    for index, char in enumerate(text):
        check = False
        if char == q:
            if debug: print(f'index {index} is {q}, len = {len(quotes)}')
            if debug: print(f"quotes: {quotes}")
            try:
                check = text[index+1] in (',',':')
            except IndexError as e:
                if debug: print(e)
                continue
            if check:
                if len(quotes) > 1: #If theres a nested closing quote
                    if debug: print(f"popped: {quotes[-1]}, len = {len(quotes)}")
                    quotes.pop()
                elif len(quotes) == 1: #The last closing quote
                    if debug: print(f"final: {text[quotes[-1]:index+1]}")
                    if text[index+1] == ':':
                        keys.append(text[quotes.pop()+1:index])
                    else:
                        try:
                            opdic[keys.pop()] = text[quotes.pop()+1:index].replace('\\\\','\\')
                        except IndexError as e:
                            print(e)
                            print(opdic)
                            print(text)
            else: # All opening quotes
                quotes.append(index)
    opdic['file'] = text[:text.find('{')].strip()
    return opdic
    
def mgsplit(text, debug=False):
    brackets = []
    lines = []
    closeb = "}"
    openb = "{"
    for index, char in enumerate(text):
        if char == openb:
            brackets.append(index)
            if debug: print(f"added: {brackets[-1]} len = {len(brackets)}")
        if char == closeb:
            if len(brackets) > 1:
                if debug: print(f"popped: {brackets[-1]} len = {len(brackets)}")
                brackets.pop()
            elif len(brackets) == 1:
                prev_newline = text[:brackets.pop()].rfind('\n')
                if prev_newline < 0: prev_newline = 0
                if debug: print(f"final: {text[prev_newline:index+1]}\n")
                lines.append(text[prev_newline:index+1])
    if debug: print(lines)
    return lines

parser = argparse.ArgumentParser(description=r"""Read the MS malformed JSON in logs
Usage example:
C:\Users\v-micgilmore\Documents\Customer\2xxxxxxxxxxxxxx9\PBIDesktopDiagnosticInfo.20250724T144038>grep -rni "incident" | grep -i "category" | grep "DAXQuery" | grep DataMashup | gjp.py message
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
parser.add_argument('--unique',
                    action = "store_true",
                    default=False,
                    help="only return unique rows")
parser.add_argument('--unique-count',
                    action = "store_true",
                    default=False,
                    help="similar to sort | uniq -c ")



args = parser.parse_args()

#lines=sys.stdin.read().split('"}')
lines=mgsplit(sys.stdin.read(), debug=False)

obj = None
keys = []


if args.delimeter.lower() == 'tab':
    args.delimeter = '\t'
if args.print_headers:
    print(args.delimeter.join(args.fields))
    
unique = {}
for i in lines:
    try:
        obj = mgparse(i, debug=False)
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
            line = args.delimeter.join(op)
            if args.unique == True or args.unique_count == True:
                try:
                    unique[line] += 1
                except KeyError:
                    unique[line] = 1
            else:
                print(line)
        #try:
        #    if len(obj[target].strip()) > 0: print('')
        #except NameError:
        #    pass
            #print('')
        #if args.space: print('')
    except KeyError:
        #print('')
        pass
        
if args.unique == True or args.unique_count == True:
    for k, v in sorted(unique.items(), key=lambda x: x[1], reverse=True):
        if args.unique_count: print(f'{v}', end='\t')
        print(k)
        
if args.keys:
    print(sorted(set(keys)))
    exit()

#print(args.unique, args.unique_count)
