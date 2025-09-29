#!/usr/bin/python3
import re
import sys
import os
from datetime import datetime
from pathlib import Path

def main(args):
    html = args[0]
    ad_str = args[1]
    log_location = args[2]
    siteID = args[3]
    time = args[4]

    if re.search(ad_str, html):
        # print(html)
        matches = re.findall(r'<img src=.*>', html)
    else:
        sys.exit(1)

    matches = '\n'.join(matches)

    filename = time + ".txt"
    filepath = Path(f'{log_location}/{siteID}/{filename}')

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(matches)
    print(f"File saved to {filepath}")

    return 0

if __name__ == '__main__':
    main(sys.argv[1:])