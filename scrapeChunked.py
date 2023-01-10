import csv
import requests
from bs4 import BeautifulSoup
import chardet
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice

CHUNK_SIZE = 1000 # you can adjust this value to any size that fits your memory

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

visited = set()
try:
    with open('visited.txt', 'r') as f:
        visited.update(f.read().splitlines())
except FileNotFoundError:
    pass

def get_meta_data(url):
    try:
        response = requests.get(url, headers=headers)
        encoding = chardet.detect(response.content)['encoding']
        response.encoding = encoding
        content_type = response.headers.get('content-type','')
        encoding = content_type.split('charset=')[-1]
        response.encoding = encoding
        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
        title = soup.find('title').get_text()
        description = soup.find('meta', attrs={'name': 'description'})

        if not description:
            description = soup.find('meta', attrs={'property': 'og:description'})

        if not description:
            description = soup.find('meta', attrs={'itemprop': 'description'})

        if not description:
            description = soup.find('meta', attrs={'name': 'twitter:description'})

        description = description['content'] if description else "No Description Found"
        return [url, title, description], None
    except Exception as e:
        return [url, None, None], e

with open('websites.csv', 'a', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['URL', 'Title', 'Description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    with open('failed.txt', 'a') as failedfile:
        with open('urls.txt', 'r') as urlsfile:
            with ThreadPoolExecutor() as executor:
                # read the urls from file in chunks
                while True:
                    chunk = ["http://" + url.rstrip() for url in islice(urlsfile, CHUNK_SIZE) if url not in visited]
                    if not chunk:
                        break
                    visited.update(chunk)
                    with open('visited.txt', 'w') as f:
                        for url in visited:
                            f.write(f"{url}\n")
                    futures = [executor.submit(get_meta_data, url) for url in chunk]
                    for future in as_completed(futures):
                        metadata, result = future.result()
                        if isinstance(result, Exception):
                            failedfile.write(f"{str(metadata[0])}, {result}\n")
                        else:
                            url, title, description = metadata
                            writer.writerow({'URL': url, 'Title': title, 'Description': description})