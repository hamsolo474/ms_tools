#import csv
#import io
import sys
import argparse
#import re

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read MS Logs as CSV")
    parser.add_argument('outfile',
                        type=str,
                        nargs='*',
                        help='file to read from and file to write to, this argument can accept one or two paths')
    parser.add_argument('--delimeter',
                        type = str,
                        default="\t",
                        help="which delimeter to use tab, comma, colon etc..")
    parser.add_argument('--left-append',
                        action = "store_true",
                        default=False,
                        help="append to the left, default is append to the right")
    parser.add_argument('--skip-top-row',
                        action = "store_true",
                        default=False,
                        help="Skip the top row")
    parser.add_argument('--tee',
                        action = "store_true",
                        default=False,
                        help="Print and write output")
    args = parser.parse_args()
    ilines = sys.stdin.read().split('\n')
    
    with open(args.outfile[0], 'r') as f:
        flines = f.read().splitlines()
        if args.skip_top_row:
            fheader = flines[0]
            flines = flines[1:]
    extras = []
    if args.left_append:
        zipped = zip((ilines, flines))
    else:
        zipped = zip(flines, ilines)
    zipped = [i for i in zipped]
    if len(ilines) != len(flines):
        if   len(ilines) > len(flines):
            extras = ilines[len(zipped):]
        elif len(ilines) < len(flines):
            extras = flines[len(zipped):]
    if args.left_append:
        extras = zip(["None" for i in extras], extras)
    else:
        extras = zip(extras, ["None" for i in extras])
    extras = [i for i in extras]
    with open(args.outfile[-1], 'w') as f:
        if args.skip_top_row:
            op = fheader
            f.write(op+'\n')
            if args.tee: print(op)
        for i in zipped:
            op = args.delimeter.join(i)
            f.write(op+'\n')
            if args.tee: print(op)
        if len(list(extras)) > 1:
            for i in extras:
                op = args.delimeter.join(i)
                f.write(op+'\n')
                if args.tee: print(op)
