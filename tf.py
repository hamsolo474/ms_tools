import sys
import argparse
import datetime

def parse_duration(duration, debug=False):
    unit = duration.strip()[-1].lower()
    if debug: print(f'unit={unit}')
    if not unit in 'hms':
        print('Invalid duration')
    else:
        value = int(duration.strip()[:-1])
        if debug: print(f'{value} {unit}')
        match (unit):
            case 's':
                retval = datetime.timedelta(seconds=value)
            case 'm':
                retval = datetime.timedelta(minutes=value)
            case 'h':
                retval = datetime.timedelta(hours=value)
    if debug: print(retval)
    return retval


parser = argparse.ArgumentParser(description=r"""Timefilter
Read PowerBI logs and only display the lines within a time range
example usage
C:\\Users\\v-micgilmore\\Documents\\Customer\\2xxxxxxxxxxxxxx6\\3 Oct2024TLS13PBIDesktopDiagnosticInfo20250819T155154>grep -rni "Start" | gjp.py Start Action | tf.py --before 2025-08-19T05:11:01.0230237Z --duration 1m
""")
parser.add_argument('--delimeter',
                    type = str,
                    default="\t",
                    help="which delimeter to use tab, comma, colon etc..")

parser.add_argument('--field',
                    type = int,
                    default=1,
                    help="which column contains the timestamp, 1 indexed")

parser.add_argument('--start', "--after",
                    type = str,
                    default=None,
                    help="Show logs after this time 2025-08-19T05:09:03.1294141Z")

parser.add_argument('--end', "--before",
                    type = str,
                    default=None,
                    help="Show logs before this time 2025-08-19T05:10:03.1294141Z")

parser.add_argument('--duration',
                    type = str,
                    default=None,
                    help="Show logs within duration of specified time you must specify the time like this, 1h 1m 1s, you cannot do 1m30s but you can do 90s")

parser.add_argument('--sort',
                    type=bool,
                    default=True,
                    help="Sort lines")

args = parser.parse_args()

times = []
if args.start:
    try: 
        times.append(datetime.datetime.fromisoformat(args.start.replace("Z", "+00:00")))
    except ValueError as e:
        print(f'{args.start} is an invalid timestamp please add timestamp in this format 2025-08-19T05:10:03.1294141Z')
        raise e
else:
    times.append(datetime.datetime(1980, 1, 1, 1, 1, 1, 129414, tzinfo=datetime.timezone.utc))

if args.end:
    try: 
        times.append(datetime.datetime.fromisoformat(args.end.replace("Z", "+00:00")))
    except ValueError as e:
        print(f'{args.end} is an invalid timestamp please add timestamp in this format 2025-08-19T05:10:03.1294141Z')
        raise e
else:
    times.append(datetime.datetime(3000, 1, 1, 1, 1, 1, 129414, tzinfo=datetime.timezone.utc))

if args.duration:
    if args.start and args.end:
        print('You can only have two out of the following: duration, start and end')
        raise AssertionError
    elif args.start:
        times[1] = times[0] + parse_duration(args.duration)
        #print(f'Replaced end {times}')
    elif args.end:
        times[0] = times[1] - parse_duration(args.duration)
        #print(f'Replaced start {times}')
    print(f'Checking between {times[0]} and {times[1]}, {args.duration}')

times = sorted(times)

lines=sys.stdin.read().splitlines()

results = False
rows = []
for line in lines:
    try:
        cols = line.split(args.delimeter)
        time = datetime.datetime.fromisoformat(cols[args.field-1].replace("Z", "+00:00"))
        rows.append([time, line])
    except IndexError as e:
        print(f'ERROR: {line}: with delimeter {args.delimeter} {e}')
    except ValueError as e:
        pass

if args.sort:
    rows = sorted(rows, key=lambda x: x[0])

for row in rows:
    time = row[0]
    if times[0] <= time <= times[1]:
        print(row[1])
        results = True

if not results:
    print(f"Program ran correctly but produced no results from this many {len(lines)} lines of input")