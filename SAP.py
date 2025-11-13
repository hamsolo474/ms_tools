import argparse
try:
    import pandas as pd
except ModuleNotFoundError: 
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
    import pandas as pd

SAP_path = r"SAP.csv"
try:
    df = pd.read_csv(SAP_path)
except BaseException as e:
    print('Cannot find SAP.csv, please contact v-micgilmore@microsoft.com for the sheet')
    raise e

op = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('terms',
                        type=str,
                        nargs='*',
                        help='search terms')
    args = parser.parse_args()

    for i in df['Path']:
        found = True
        for j in args.terms:
            if j.lower() not in str(i).lower():
                found = False
        if found == True:
            op.append(i)
    for i in sorted(set(op)):
        print(i)
