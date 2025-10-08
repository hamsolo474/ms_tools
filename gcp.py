import csv
import io
import sys
import argparse
import re

guid_regex = re.compile('([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})')

def csvline(text):
    filename = text.split(':')[0]
    try: line = text.split(':')[1]
    except IndexError: line = ''
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
    quotes = []
    strings = []
    reader = csv.reader(io.StringIO(text), delimiter=sep)
    for i in reader:
        for index, value in enumerate(i):
            opdic[str(index)] = value
    #renames
    renames = {}
    try:
        if 'QueryExecutionReport' in opdic['filename']:
            renames = {'2':'constring',
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
        #opdic[v] = opdic.pop(k)
            opdic[v] = opdic[k]
        except KeyError:
            #print(f'failed {k}')
            pass
    return opdic

def parse(text, debug=False):
    return csvline(text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read MS Logs as CSV")
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
    parser.add_argument('--unique',
                        action = "store_true",
                        default=False,
                        help="only return unique rows")
    parser.add_argument('--unique-count', '--count-unique',
                        action = "store_true",
                        default=False,
                        help="similar to sort | uniq -c ")
    parser.add_argument('--merge-ids',
                        action = "store_false",
                        default=True,
                        help="run a regex to strip guids, disable to see full string but I would recommend leaving this on and doing another grep to investigate further")
    parser.add_argument('--print-long-lines',
                        action = "store_true",
                        default=False,
                        help="print long lines and do not truncate after 500chars")
    parser.add_argument('--force-lower',
                        action = "store_true",
                        default=False,
                        help="force lowercase conversion for case insensitivity")

    args = parser.parse_args()
    lines = sys.stdin.read().split('\n')
    obj = None
    keys = []

    if args.delimeter.lower() == 'tab':
        args.delimeter = '\t'
        
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
                    result = obj[target].strip()
                    if len(result) == 0:
                        break
                    op.append(obj[target])
                except KeyError:
                    pass
            if len(op) == len(args.fields) and not args.keys:
                line = args.delimeter.join(op).lower()
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
            if args.unique_count: print(f'{v}', end='\t')
            print(k)
            results = True
            
    if args.keys:
        print(sorted(set(keys)))
        exit()

    if not results:
        print(f"Program ran correctly but produced no results from this {len(lines)} lines of input")
    #print(args.unique, args.unique_count)
    
    
