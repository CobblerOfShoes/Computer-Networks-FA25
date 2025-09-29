#!/usr/bin/python3
import re
import sys
import os
from datetime import datetime

def main(args):
    html = args[0]
    ad_str = args[1]

    if re.search(ad_str, html):
        print(html)
        matches = re.findall(r'<img src=.*>', html)
    else:
        sys.exit(1)
        
    matches = '\n'.join(matches)
        
    filename = datetime.now().strftime("%y-%M-%d-%H:%m") + ".txt"
    filepath = f'logs/{filename}'
    
    with open(filepath, 'w+') as file:
        file.write(matches)
    print(f"File saved to {filepath}")
        
    return 0

if __name__ == '__main__':
    main(sys.argv[1:])