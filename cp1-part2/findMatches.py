#!/usr/bin/python3
import re
import sys
import requests
import os
from pathlib import Path
from urllib.parse import urlparse

BUFSIZ = 8192

def main(args):
    html = args[0]
    ad_str = args[1]
    log_location = args[2]
    siteID = args[3]
    time = args[4]

    image_urls = []
    if re.search(ad_str, html):
        # print(html)
        matches = re.findall(r'<img.*src="(.*)".*/>', html)
        image_urls.extend(list(matches))
    else:
        sys.exit(1)

    directory = f'{log_location}/{siteID}/{time}'

    for url in image_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()

            parsed_url = urlparse(url)
            path = parsed_url.path
            image_name = os.path.basename(os.path.normpath(path))
            filepath = Path(f'{directory}/{image_name}')
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with filepath.open('wb') as file:
                for chunk in response.iter_content(chunk_size=BUFSIZ):
                    file.write(chunk)
            print(f"Image \"{image_name}\" saved to: {directory}")
        except requests.exceptions.RequestException:
            print(f"Could not download image from {url}")

    return 0

if __name__ == '__main__':
    main(sys.argv[1:])
