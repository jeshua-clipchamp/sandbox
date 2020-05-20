import sys
import json
import glob
import re

def main(patterns, file_list):
    for pattern in patterns:
        for fname in file_list:
            if pattern.match(fname):
                print(1)
                return
    
    print(0)

if __name__ == '__main__':
    main(
        file_list=json.load(open(sys.argv[1])),
        patterns=[re.compile(glob.fnmatch.translate(pattern)) for pattern in sys.argv[2:]]
    )
