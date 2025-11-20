import sys
import argparse
import json

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
                            print('IndexError:',e)
                            print(opdic)
                            print(text)
            else: # All opening quotes
                quotes.append(index)
    #opdic['file'] = text[:text.find('{')].strip()
    return opdic

def parse(text, debug=False):
    beginning = text.find('{')
    try:
        opdic = json.loads(text[beginning:].strip())
    except json.decoder.JSONDecodeError:
        return mgparse(text)
    opdic['file'] = text[:beginning].strip()
    opdic['all'] = text[beginning:]
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

if __name__ == '__main__':
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
                        help="which delimeter to use tab, comma, colon etc..")
    parser.add_argument('--print-headers',
                        action = "store_true",
                        default=False,
                        help="Print headers")
    parser.add_argument('--unique', "-u",
                        action = "store_true",
                        default=False,
                        help="only return unique rows")
    parser.add_argument('--unique-count', '--count-unique', "-c",
                        action = "store_true",
                        default=False,
                        help="similar to sort | uniq -c ")
    parser.add_argument('--print-long-lines', "-p",
                        action = "store_true",
                        default=False,
                        help="print long lines and do not truncate after 500chars")
    parser.add_argument('--force-lower', "-l",
                        action = "store_true",
                        default=False,
                        help="force lowercase conversion for case insensitivity")


    args = parser.parse_args()

    #lines=mgsplit('''Traces/PBIDesktop.5824.2025-08-19T05-09-02-252687.log:4370:DataMashup.Trace Information: 24579 : {"Start":"2025-08-19T05:51:00.9964016Z","Action":"CredentialStorage/GetCredentials","Credentials":[["PostgreSQL","cren-stagedb-ddl-validation.cqxbawsoxhca.ap-southeast-2.rds.amazonaws.com","cren-stagedb-ddl-validation.cqxbawsoxhca.ap-southeast-2.rds.amazonaws.com;stagedb",396],["PostgreSQL","cren-stagedb-ddl-validation.cqxbawsoxhca.ap-southeast-2.rds.amazonaws.com:8432","cren-stagedb-ddl-validation.cqxbawsoxhca.ap-southeast-2.rds.amazonaws.com:8432;stagedb",396]],"ProductVersion":"2.135.7627.0 (24.08)","ActivityId":"00000000-0000-0000-0000-000000000000","Process":"PBIDesktop","Pid":5824,"Tid":73,"Duration":"00:00:00.0000908"}
    #Traces/PBIDesktop.5824.2025-08-19T05-09-02-252687.log:4442:DataMashup.Trace Information: 24579 : {"Start":"2025-08-19T05:51:12.5704106Z","Action":"CredentialStorage/GetCredentials","Credentials":[["PostgreSQL","cren-stagedb-ddl-validation.cqxbawsoxhca.ap-southeast-2.rds.amazonaws.com","cren-stagedb-ddl-validation.cqxbawsoxhca.ap-southeast-2.rds.amazonaws.com;stagedb",396],["PostgreSQL","cren-stagedb-ddl-validation.cqxbawsoxhca.ap-southeast-2.rds.amazonaws.com:8432","cren-stagedb-ddl-validation.cqxbawsoxhca.ap-southeast-2.rds.amazonaws.com:8432;stagedb",396]],"ProductVersion":"2.135.7627.0 (24.08)","ActivityId":"00000000-0000-0000-0000-000000000000","Process":"PBIDesktop","Pid":5824,"Tid":163,"Duration":"00:00:00.0000963"}''', debug=True)
    lines=mgsplit(sys.stdin.read(), debug=False)

    obj = None
    keys = []


    if args.delimeter.lower() == 'tab':
        args.delimeter = '\t'
    if args.force_lower:
        lines = [i.lower() for i in lines]
    if args.print_headers:
        print(args.delimeter.join(args.fields))
        
    unique = {}
    results = False
    for i in lines:
        try:
            obj = parse(i, debug=False)
            keys.extend(obj.keys())
            op = []
            for target in args.fields:
                try:
                    result = str(obj[target]).strip()
                    if len(result) == 0:
                        break
                    op.append(result)
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
                    if len(line) > 500 and not args.print_long_lines:
                        print(line[:500], 'Line too long, truncated')
                    else:
                        print(line)
                    results = True
        except KeyError:
            pass
            
    if args.unique == True or args.unique_count == True:
        for k, v in sorted(unique.items(), key=lambda x: x[1], reverse=True):
            if args.unique_count: print(f'{v}', end='\t')
            print(k)
            results = True
            
    if args.keys:
        print(sorted(set(keys)))
        exit()

    if not results:
        print(f"Program ran correctly but produced no results from this {len(lines)} lines of input")
    #print(args.unique, args.unique_count)
