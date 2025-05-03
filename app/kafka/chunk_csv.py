"""
Contains the functionality to create one large chunk of the original CSV file
"""

import os
from dotenv import load_dotenv
import csv

load_dotenv()

csv_file = os.environ.get('CSV_FILE')
output_file = 'Data\\partition-1.csv'

if not os.path.exists('Data'):
    os.makedirs('Data')

target_size = 1000 * 1024 * 1024 # 3GB
current_size = 0

with open(csv_file, 'r', encoding='utf-8') as f, \
    open(output_file, 'w', encoding='utf-8', newline='') as f_out:
    reader = csv.reader(f)
    writer = csv.writer(f_out)

    header = next(reader)
    writer.writerow(header)
    current_size += len(','.join(header).encode('utf-8')) # converting array to string and calculating size


    for row in reader:
        row_data = ','.join(row) + '\n'
        row_size = len(row_data.encode('utf-8'))

        if current_size + row_size > target_size:
            break

        writer.writerow(row)
        current_size += row_size

