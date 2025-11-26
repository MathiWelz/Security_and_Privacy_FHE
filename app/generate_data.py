import pandas as pd
import numpy as np
import os
import tomli
import argparse
from models import LoanApplicant

def load_config():
    with open("config.toml", "rb") as f:
        return tomli.load(f)

def generate_loan_data():
    # 1. Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Generate synthetic loan data")
    parser.add_argument("--size", type=int, default=None, help="Number of samples to generate")
    args = parser.parse_args()

    # 2. Load Config
    conf = load_config()
    output_path = conf['files']['raw_data']
    
    # 3. Determine Size (CLI Argument > Config File)
    if args.size is not None:
        n_samples = args.size
        source = "Command Line"
    else:
        n_samples = conf['generation']['n_samples']
        source = "Config File"

    # Create data folder
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Generating data using model: {LoanApplicant.__name__}")
    print(f"Sample size: {n_samples} (Source: {source})")

    # 4. Generate Data
    applicants = []
    for i in range(n_samples):
        person = LoanApplicant(
            person_id=f"ID_{i:03d}",
            income=np.random.randint(2000, 15000),
            debt=np.random.randint(0, 5000),
            late_payments=np.random.randint(0, 10),
            loan_amount=np.random.randint(10000, 500000)
        )
        applicants.append(person.to_dict())

    # 5. Save
    df = pd.DataFrame(applicants)
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    generate_loan_data()