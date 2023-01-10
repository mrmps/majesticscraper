# import csv
# import requests
# from bs4 import BeautifulSoup
# import chardet

# # Open a CSV file to write the data to
# website_list = [
#     "https://www.google.com",
#     "https://www.youtube.com",
#     "https://www.facebook.com",
#     "https://www.baidu.com",
#     "https://www.wikipedia.org",
#     "https://www.example.com"
# ]
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
# }

# with open('websites.csv', 'w', newline='', encoding='utf-8') as csvfile:
#     fieldnames = ['URL', 'Title', 'Description']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writeheader()

#     # Open a file to write failed URLs to
#     with open('failed.txt', 'w') as failedfile:

#         # Iterate over the list of websites
#         for url in website_list:
#             try:
#                 # Make a GET request to the website
#                 response = requests.get(url, headers=headers)
#                 encoding = chardet.detect(response.content)['encoding']
#                 response.encoding = encoding
#                 content_type = response.headers.get('content-type','')
#                 encoding = content_type.split('charset=')[-1]
#                 response.encoding = encoding


#                 # Check that the request was successful
#                 if response.status_code == 200:
#                     # Parse the HTML of the website
#                     soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
#                     # print(soup)

#                     # Extract the title, meta description, and meta keywords
#                     title = soup.find('title').get_text()
#                     description = soup.find('meta', attrs={'name': 'description'})

#                     if not description:
#                         description = soup.find('meta', attrs={'property': 'og:description'})

#                     if not description:
#                         description = soup.find('meta', attrs={'itemprop': 'description'})

#                     if not description:
#                         description = soup.find('meta', attrs={'name': 'twitter:description'})

#                     description = description['content'] if description else "No Description Found"


#                     # description = soup.find("meta",  {"property":"og:description"})
#                     # description = description["content"] if description else None
#                     print(description)
#                     # print(pagedescription)
#                     # keywords = soup.find('meta', attrs={'name': 'keywords'})['content']

#                     # Write the data to the CSV file
#                     if description:
#                         writer.writerow({'URL': url, 'Title': title, 'Description': description})
#                     else:
#                         writer.writerow({'URL': url, 'Title': title, 'Description': pagedescription})
#                 else:
#                     raise Exception(f"Failed with status code {response.status_code}")
#             except Exception as e:
#                 # Write the failed URL to the failedfile
#                 failedfile.write(f"{url}, {e}\n")


import csv
import requests
from bs4 import BeautifulSoup
import chardet
from concurrent.futures import ThreadPoolExecutor, as_completed

website_list = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.baidu.com",
    "https://www.wikipedia.org",
    "https://www.example.com"
]
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
        print(description)
        return [url, title, description], None
    except Exception as e:
        return [url, None, None], e

# Open a CSV file to write the data to
with open('websites.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['URL', 'Title', 'Description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Open a file to write failed URLs to
    with open('failed.txt', 'w') as failedfile:

        # Create a ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            # Submit the get_meta_data function for each URL
            futures = [executor.submit(get_meta_data, url) for url in website_list]

            # Wait for the futures to complete and process the results
            for future in as_completed(futures):
                metadata, result = future.result()
                if isinstance(result, Exception):
                    failedfile.write(f"{str(metadata)}, {result}\n")
                else:
                    url, title, description = metadata
                    writer.writerow({'URL': url, 'Title': title, 'Description': description})
