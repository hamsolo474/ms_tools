import sys
import argparse
import json
import csv
import io
import re

guid_regex = re.compile('([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})')

def mgparse(text, debug=False):
    q = '"'
    quotes = []
    opdic = {}
    keys = []
    for index, char in enumerate(text):
        check = False
        if char == q:
            try:
                check = text[index+1] in (',',':')
            except IndexError as e:
                continue
            if check:
                if len(quotes) > 1:
                    quotes.pop()
                elif len(quotes) == 1:
                    if text[index+1] == ':':
                        keys.append(text[quotes.pop()+1:index])
                    else:
                        try:
                            opdic[keys.pop()] = text[quotes.pop()+1:index].replace('\\\\','\\')
                        except IndexError as e:
                            pass
            else:
                quotes.append(index)
    return opdic

def json_parse(text, debug=False):
    beginning = text.find('{')
    if beginning == -1:
        raise ValueError("No JSON object found")
    try:
        opdic = json.loads(text[beginning:].strip())
    except json.decoder.JSONDecodeError:
        return mgparse(text)
    opdic['file'] = text[:beginning].strip()
    opdic['all'] = text[beginning:]
    return opdic

def csvline(text, args):
    filename = text.split(':')[0]
    try:
        line = text.split(':')[1]
    except IndexError:
        line = ''
    opdic = {'filename': filename, 'line': line}
    text = text[len(filename)+len(line)+2:]
    if args.force_lower:
        text = text.lower()
    sep = ','
    tabseps = ['GatewayErrors', 'GatewayInfo']
    for i in tabseps:
        if i in opdic['filename']:
            sep = '\t'
            break
    q = '"'
    reader = csv.reader(io.StringIO(text), delimiter=sep)
    for i in reader:
        for index, value in enumerate(i):
            opdic[str(index)] = value
    renames = {}
    try:
        if 'QueryExecutionReport' in opdic['filename']:
            renames = {'0':'GatewayObjectId',
                       '1':'RequestId',
                       '3':'QueryTrackingId',
                       '5':'QueryExecutionDuration',
                       '7':'DataReadingAndSerializationDuration',
                       '8':'DataReadingDuration',
                       '9':'DataSerializationDuration',
                       '10':'SpoolingDiskWritingDuration',
                       '11':'SpoolingDiskReadingDuration',
                       '12':'SpoolingTotalDataSize',
                       '13':'DataProcessingEndTimeUTC',
                       '14':'DataProcessingDuration',
                       '15':'Success',
                       '2':'constring',
                       '4':'timestamp',
                       '6':'type',
                       '16':'message'}
        elif 'GatewayErrors' in opdic['filename']:
            opdic['gwtype'] = opdic['0'].split(':')[0]
            opdic['level'] = opdic['0'].split(':')[1]
            opdic['timestamp'] = opdic['0'].split(' ')[2]
            opdic['hash'] = opdic['7'].split(' ')[0]
            opdic['message'] = opdic['7'][len(opdic['hash'])+1:]
            renames = {'1':'activityid',
                       '2':'rootactivityid',
                       '3':'activitytype',
                       '4':'clientactivityid',
                       '5':'sourceid',
                       '6':'helperid'}
        elif 'GatewayInfo' in opdic['filename']:
            opdic['gwtype'] = opdic['0'].split(' ')[0]
            opdic['level'] = opdic['0'].split(' ')[1][:-1]
            opdic['timestamp'] = opdic['0'].split(' ')[4]
            opdic['hash'] = opdic['7'].split(' ')[0]
            opdic['message'] = opdic['7'][len(opdic['hash'])+1:]
            renames = {'1':'activityid',
                       '2':'rootactivityid',
                       '3':'activitytype',
                       '4':'clientactivityid',
                       '5':'sourceid',
                       '6':'helperid'}
        elif 'MashupEvaluationReport' in opdic['filename']:
            renames = {'1':'GatewayObjectId',
                       '2':'ConnectionId',
                       '3':'RequestId',
                       '4':'QueryTrackingId',
                       '5':'DataSource',
                       '6':'TotalRows',
                       '7':'TotalBytes',
                       '8':'TotalProcessorTime(ms)',
                       '9':'EndTimeUTC',
                       '10':'AverageWorkingSet(byte)',
                       '11':'MaxWorkingSet(byte)',
                       '12':'AverageCommit(byte)',
                       '13':'MaxCommit(byte)',
                       '14':'MaxPercentProcessorTime',
                       '15':'AverageIODataBytesPerSecond',
                       '16':'MaxIODataBytesPerSecond'}
    except IndexError as e:
        pass
    for k,v in renames.items():
        try:
            opdic[v] = opdic[k]
        except KeyError:
            pass
    return opdic

def split_all_lines(text):
    lines = []
    current = ""
    for char in text:
        if char == '\n':
            if current.strip():
                lines.append(current)
            current = ""
        else:
            current += char
    if current.strip():
        lines.append(current)
    return lines

def mgsplit(text, debug=False):
    return split_all_lines(text)

def route_and_parse(text, args, verbose=False):
    try:
        return json_parse(text), 'json'
    except Exception:
        pass
    try:
        return csvline(text, args), 'csv'
    except Exception:
        if verbose:
            print(f"Skipped: {text[:100]}...", file=sys.stderr)
        return None, 'skipped'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=r"""Unified CSV/JSON log parser for MS Logs
Automatically detects JSON vs CSV format per line
Usage example:
  grep -rni "exception" | grp.py message
""")
    parser.add_argument('fields',
                        type=str,
                        nargs='*',
                        help='fields to extract')
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
    parser.add_argument('--unique-count', '--count-unique', "--cu", "--uc", "-c",
                        action = "store_true",
                        default=False,
                        help="similar to sort | uniq -c ")
    parser.add_argument('--greater-than', '--gt',
                        action = "store_int",
                        default=0,
                        help="only show count greater than X")  
    parser.add_argument('--merge-ids',
                        action = "store_false",
                        default=True,
                        help="run a regex to strip guids, disable to see full string")
    parser.add_argument('--print-long-lines', "-p",
                        action = "store_true",
                        default=False,
                        help="print long lines and do not truncate after 500chars")
    parser.add_argument('--force-lower', "-l",
                        action = "store_true",
                        default=False,
                        help="force lowercase conversion for case insensitivity")
    parser.add_argument('--verbose', "-v",
                        action = "store_true",
                        default=False,
                        help="show skipped lines")

    args = parser.parse_args()

    if args.delimeter.lower() == 'tab':
        args.delimeter = '\t'
    if args.force_lower:
        lines = [i.lower() for i in mgsplit(sys.stdin.read())]
    else:
        lines = mgsplit(sys.stdin.read())

    obj = None
    keys = []

    if args.print_headers:
        print(args.delimeter.join(args.fields))
        
    unique = {}
    results = False
    skipped_count = 0
    
    for i in lines:
        try:
            obj, parser_type = route_and_parse(i, args, verbose=args.verbose)
            if obj is None:
                skipped_count += 1
                continue
            keys.extend(obj.keys())
            
            if args.keys:
                continue
                
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
                    if args.merge_ids == True:
                        line = guid_regex.sub('{GUID}', line)
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
            if args.unique_count: 
                if v > args.greater_than:
                    print(f'{v}', end='\t')
                    print(k)
            else:
                print(k)
            results = True
            
    if args.keys:
        print(sorted(set(keys)))
        exit()

    if not results:
        if skipped_count > 0 and args.verbose:
            print(f"Program ran correctly but produced no results from this {len(lines)} lines of input ({skipped_count} skipped)", file=sys.stderr)
        else:
            print(f"Program ran correctly but produced no results from this {len(lines)} lines of input")
