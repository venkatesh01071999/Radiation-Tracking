"""
Simulation of real time data. Usage of reversed dataset.
"""

import os
from dotenv import load_dotenv
import csv
import time
import logging


load_dotenv()
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

processed_file = os.environ.get("PROCESSED_FILE")
simulation_file = os.environ.get("SIMULATION_FILE") # its not stored in git as it is a simulation file.

with open(processed_file, 'r') as file,\
    open(simulation_file, 'w', newline='') as sim_file:
    reader = csv.reader(file)
    writer = csv.writer(sim_file)

    header = next(reader)
    writer.writerow(header)

    for index,row in enumerate(reader):
        writer.writerow(row)
        logger.info(f"Row {index} written to simulation file")
        time.sleep(int(os.environ.get('SIMULATION_DELAY')))  # simulate delay between appending rows
    
        
