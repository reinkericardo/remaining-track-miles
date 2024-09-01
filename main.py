import data_processing_utilities
import logging

logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

file_path = 'data/states_2022-06-27-20.csv.gz'
df = data_processing_utilities.load_csv_gzip(file_path=file_path)

