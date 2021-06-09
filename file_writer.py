import csv
import logging

def write_file(filename, fieldnames, mode, array):
    try:
        with open(f"{filename}.csv", encoding='utf-8-sig', mode=mode) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(array)
    except Exception as e:
        logging.error(e)
        raise
