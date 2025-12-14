import csv
import random
import os
import configparser

# Load Config
config = configparser.ConfigParser()
config.read('config.ini')

DATA_DIR = config['DEFAULT']['DATA_DIR']
FILENAME = config['FILES']['RAW_DATASET']
SIZE = int(config['PARAMS']['DATA_SIZE'])

def generate_dataset():
    # Ensure directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created folder: {DATA_DIR}")

    filepath = os.path.join(DATA_DIR, FILENAME)
    
    # Generate Data
    data = [random.randint(30000, 120000) for _ in range(SIZE)]
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Salary"])
        for salary in data:
            writer.writerow([salary])
            
    print(f"Dataset generated at: {filepath} ({SIZE} entries)")

if __name__ == "__main__":
    generate_dataset()