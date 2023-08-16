import csv
import gzip
import os
import requests
import shutil
from warcio import ArchiveIterator


URL = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2023-14/segments/1679296950528.96/robotstxt/CC-MAIN-20230402105054-20230402135054-00799.warc.gz"
DOWNLOAD_PATH = "data/raw/CC-MAIN-20230402105054-20230402135054-00799.warc.gz"
EXTRACT_PATH = "data/raw/CC-MAIN-20230402105054-20230402135054-00799.warc"
OUTPUT_PATH = "data/extracted/robots_data.csv"
STATISTICS_PATH ="data/statistics/robots_stats"

# Create raw data directory 
if not os.path.exists("data/raw"):
        os.makedirs("data/raw")

# Download the WARC file
response = requests.get(URL,stream=True)
with open(DOWNLOAD_PATH,'wb') as file:
    for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)

# Uncompress the file to data/raw
with gzip.open(DOWNLOAD_PATH,'rb') as file_in:
    with open(EXTRACT_PATH,'wb') as file_out:
        shutil.copyfileobj(file_in,file_out)

# Using a dictionary to accumulate daily stats
stats_data = {}

# Create extracted data directory 
if not os.path.exists("data/extracted"):
        os.makedirs("data/extracted")

# Extract relevant data and write to output file
with open(OUTPUT_PATH,'w') as output_file:
    # Note: Chose CSV format because it's widely supported and easily readable.
    writer = csv.writer(output_file)
    writer.writerow(['fetched_at','domain','http_code','user_agent','disallow_cnt','allow_cnt'])

    with open(EXTRACT_PATH,'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'response':
                fetched_at = record.rec_headers.get_header('WARC-DATE')
                domain = record.rec_headers.get_header('WARC-Target-URI')
                http_code = int(record.http_headers.get_statuscode())
                user_agent, disallow_cnt,allow_cnt = '*',0,0

                if http_code == 200:
                    payload = record.content_stream().read().decode('utf-8','ignore')
                    for line in payload.split("\n"):
                        if "User-agent:" in line:
                            user_agent = line.split("User-agent:")[1].strip()
                        if "Disallow:" in line:
                            disallow_cnt += 1
                        if "Allow:" in line:
                            allow_cnt += 1
                    writer.writerow([fetched_at,http_code,domain,user_agent,disallow_cnt,allow_cnt])
                else:
                    writer.writerow([fetched_at,http_code,domain,None,None,None])
                
                # Populating the stats dictionary
                if fetched_at not in stats_data:
                    stats_data[fetched_at] = {
                        'total_errors': 0,
                        'total_ok': 0,
                        'distinct_ua': set(),
                        'total_allows': 0,
                        'total_disallows': 0
                    }
                stats_data[fetched_at]['total_errors'] += 0 if http_code == 200 else 1
                stats_data[fetched_at]['total_ok'] += 1 if http_code == 200 else 0
                stats_data[fetched_at]['distinct_ua'].add(user_agent)
                stats_data[fetched_at]['total_allows'] += allow_cnt
                stats_data[fetched_at]['total_disallows'] += disallow_cnt
    
    print(f"Data saved to {OUTPUT_PATH}!")

# Create stats directory 
if not os.path.exists("data/statistics"):
        os.makedirs("data/statistics")

# Write the aggregated statistics to a file
with open(STATISTICS_PATH, 'w') as stats_file:
    writer = csv.writer(stats_file)
    writer.writerow(['date', 'total_errors', 'total_ok', 'total_distinct_ua', 'total_allows', 'total_disallows'])

    for date, data in stats_data.items():
        writer.writerow([date, data['total_errors'], data['total_ok'], len(data['distinct_ua']),
                         data['total_allows'], data['total_disallows']])

print(f"Statistics saved to {STATISTICS_PATH}!")


if __name__ == '__main__':
    print("Done!")
