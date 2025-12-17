import csv
import random
import os
import configparser
import argparse

# Load Config for defaults
config = configparser.ConfigParser()
config.read('config.ini')

DATA_DIR = config['DEFAULT']['DATA_DIR']
FILENAME = config['FILES']['RAW_DATASET']
DEFAULT_SIZE = int(config['PARAMS']['DATA_SIZE'])

def generate_dataset(size=None):
    # Use argument size if provided, otherwise config default
    final_size = size if size is not None else DEFAULT_SIZE
    
    # Ensure directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created folder: {DATA_DIR}")

    filepath = os.path.join(DATA_DIR, FILENAME)
    
    # Generate Data
    data = [random.randint(30000, 120000) for _ in range(final_size)]
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Salary"])
        for salary in data:
            writer.writerow([salary])
            
    print(f"Dataset generated at: {filepath} ({final_size} entries)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dummy salary dataset.")
    parser.add_argument("--size", type=int, default=None, help="Number of records to generate.")
    args = parser.parse_args()
    
    generate_dataset(args.size)