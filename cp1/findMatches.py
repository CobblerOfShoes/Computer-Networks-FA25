#!/usr/bin/python3
import re
import sys
import os
from datetime import datetime
from pathlib import Path

def main(args):
    html = args[0]
    ad_str = args[1]
    siteID = args[2]

    print(html)
    print(ad_str)

    if re.search(ad_str, html):
        print(html)
        matches = re.findall(r'<img src=.*>', html)
    else:
        sys.exit(1)

    matches = '\n'.join(matches)

    filename = datetime.now().strftime("%y-%M-%d-%H:%m") + ".txt"
    filepath = Path(f'server-logs/{siteID}/{filename}')

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(matches)
    print(f"File saved to {filepath}")

    return 0

if __name__ == '__main__':
    main(sys.argv[1:])