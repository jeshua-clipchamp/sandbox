import sys
import json
import glob
import re

def main(patterns, file_list):
    for pattern in patterns:
        for fname in file_list:
            if pattern.match(fname):
                print('::set-output name={will_run}::{true}')
                return
    
    print('::set-output name={will_run}::{false}')

if __name__ == '__main__':
    main(
        file_list=json.load(open(sys.argv[1])),
        patterns=[re.compile(glob.fnmatch.translate(pattern)) for pattern in sys.argv[2:]]
    )
