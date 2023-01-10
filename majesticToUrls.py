import csv

with open('majestic.csv', 'r', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    with open('urls.txt', 'w') as urlsfile:
        for row in reader:
            url = row['Domain']
            urlsfile.write(url + '\n')
