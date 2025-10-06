#!/usr/bin/python3
import re
import sys
import os
from datetime import datetime
import requests

def main(args):
    html = args[0]
    ad_str = args[1]
    domain = args[2]
    id = args[3]

    if re.search(ad_str, html):
        print(html)
        matches = re.findall(r'<img src=.*>', html)
    else:
        sys.exit(1)
        
    img_urls = []
    for match in matches:
        start = match.find('"')
        end = match.find('"', start + 1)
        img_urls.append(match[start+1:end])
        
    filename = datetime.now().strftime("%y-%M-%d-%H:%M:%S")
    filepath = f'logs/{id}/{filename}'
    
    try:
        os.makedirs(filepath)
    except:
        pass
    
    for img in img_urls:
        start = 0
        img_name = img[::-1]
        start = img_name.find("/")
        img_name = img_name[:start]
        img_name = img_name[::-1]
        res = requests.get(img)
        
        with open(filepath + '/' + img_name, 'bw') as image:
            for chunk in res.iter_content(chunk_size=8192):
                image.write(chunk)
    
    return 0

if __name__ == '__main__':
    main(sys.argv[1:])