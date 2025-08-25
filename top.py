import sys
import argparse

parser = argparse.ArgumentParser(description=r"""Top""")
parser.add_argument('quantity',
                    type=int,
                    help='number of lines')
parser.add_argument('--bottom',
                    action = "store_true",
                    default=False,
                    help="Return bottom rows")
parser.add_argument('--sort',
                    action = "store_true",
                    default=False,
                    help="Sort lines")

args = parser.parse_args()

lines = sys.stdin.read().splitlines()

results = False
try:
    if args.sort:
        lines = sorted(lines)
    if args.bottom:
        lines = lines.reverse()
    quantity = int(args.quantity)
    for i in lines[:args.quantity]:
        print(i)
        results = True
except TypeError as e:
    print(f'{args.top} is not an integer {e}')
if not results:

    print("Program ran correctly but produced no results")
