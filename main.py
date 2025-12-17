import time
import configparser
import argparse
import ast
import csv
import os
from users import DataHolder, DataAnalyzer

# 1. Setup Configuration & Args
config = configparser.ConfigParser()
config.read('config.ini')

DATA_DIR = config['DEFAULT']['DATA_DIR']
RAW_FILE = config['FILES']['RAW_DATASET']

def run_simulation(args, ts_coeff_list):
    print("=== STARTING PRIVACY PRESERVING SALARY AUDIT ===\n")
    print(f"Config: Size={args.size} | Paillier_N={args.phe_n} | TenSEAL_Poly={args.ts_poly}")
    
    # 2. Instantiate Users
    holder = DataHolder(
        DATA_DIR, 
        phe_n_length=args.phe_n,
        ts_poly=args.ts_poly,
        ts_coeff=ts_coeff_list
    )
    analyzer = DataAnalyzer(DATA_DIR)

    try:
        raw_data = holder.load_dataset(RAW_FILE)
    except FileNotFoundError:
        print("Error: Dataset not found. Run dataset_gen.py first.")
        return

    rows_to_save = []
    results_table = []

    # ----------------------------
    # SCHEME A: PAILLIER
    # ----------------------------
    print("\n--- SCHEME 1: PAILLIER ---")
    start_total = time.time()
    
    t0 = time.time()
    holder.encrypt_paillier(raw_data, config['FILES']['PAILLIER_ENC'])
    t_enc = time.time() - t0

    t0 = time.time()
    analyzer.process_paillier(config['FILES']['PAILLIER_ENC'], config['FILES']['PAILLIER_RES'])
    t_ana = time.time() - t0

    t0 = time.time()
    p_sum, p_mean = holder.decrypt_paillier(config['FILES']['PAILLIER_RES'])
    t_dec = time.time() - t0

    total_time = time.time() - start_total
    print(f"> Result: Sum={p_sum}, Mean={p_mean}")
    
    results_table.append(['Paillier', t_enc, t_ana, t_dec, total_time])
    
    rows_to_save.append({
        'Scheme': 'Paillier',
        'Records_Size': args.size,
        'PHE_N': args.phe_n,
        'TS_Poly': 'N/A',
        'TS_Coeff': 'N/A',
        'Encrypt_Time': t_enc,
        'Analysis_Time': t_ana,
        'Decrypt_Time': t_dec,
        'Total_Time': total_time,
        'Result_Value': p_mean
    })

    # ----------------------------
    # SCHEME B: TENSEAL
    # ----------------------------
    print("\n--- SCHEME 2: TENSEAL (CKKS) ---")
    start_total = time.time()

    # Step 1: Encrypt & Share Keys
    t0 = time.time()
    holder.encrypt_tenseal(raw_data, config['FILES']['TENSEAL_ENC'])
    # NEW: Save context/key to file for the analyzer
    holder.save_tenseal_context(config['FILES']['TENSEAL_CTX'])
    t_enc = time.time() - t0

    # Step 2: Analyze (Cloud)
    # NEW: Analyzer loads context from file, not memory
    t0 = time.time()
    analyzer.process_tenseal(
        config['FILES']['TENSEAL_ENC'], 
        config['FILES']['TENSEAL_RES'], 
        config['FILES']['TENSEAL_CTX']
    )
    t_ana = time.time() - t0

    # Step 3: Decrypt
    t0 = time.time()
    ts_mean = holder.decrypt_tenseal(config['FILES']['TENSEAL_RES'])
    t_dec = time.time() - t0

    total_time = time.time() - start_total
    print(f"> Result: Mean={ts_mean:.2f}")
    
    results_table.append(['TenSEAL', t_enc, t_ana, t_dec, total_time])
    
    rows_to_save.append({
        'Scheme': 'TenSEAL',
        'Records_Size': args.size,
        'PHE_N': 'N/A',
        'TS_Poly': args.ts_poly,
        'TS_Coeff': str(ts_coeff_list),
        'Encrypt_Time': t_enc,
        'Analysis_Time': t_ana,
        'Decrypt_Time': t_dec,
        'Total_Time': total_time,
        'Result_Value': ts_mean
    })

    # ----------------------------
    # FINAL OUTPUT
    # ----------------------------
    print("\n\n=== PERFORMANCE REPORT (Seconds) ===")
    print(f"{'Scheme':<15} | {'Encrypt':<10} | {'Analysis':<10} | {'Decrypt':<10} | {'Total':<10}")
    print("-" * 65)
    for row in results_table:
        print(f"{row[0]:<15} | {row[1]:<10.5f} | {row[2]:<10.5f} | {row[3]:<10.5f} | {row[4]:<10.5f}")

    # CSV SAVING
    file_exists = os.path.isfile(args.csv_file)
    with open(args.csv_file, mode='a', newline='') as f:
        fieldnames = ['Scheme', 'Records_Size', 'PHE_N', 'TS_Poly', 'TS_Coeff', 'Encrypt_Time', 'Analysis_Time', 'Decrypt_Time', 'Total_Time', 'Result_Value']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(rows_to_save)
    
    print(f"\n[System] Results appended to {args.csv_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Privacy Preserving Salary Audit Simulation")
    
    # Arguments
    parser.add_argument("--size", type=int, default=13000, help="Size of dataset")
    parser.add_argument("--phe_n", type=int, default=1024, help="Paillier key size in bits")
    parser.add_argument("--ts_poly", type=int, default=8192, help="TenSEAL Poly Modulus Degree")
    parser.add_argument("--ts_coeff", type=str, default="[60, 40, 40, 60]", help="TenSEAL Coeff Mod Bit Sizes (as string list)")
    parser.add_argument("--csv_file", type=str, default="benchmark_results.csv", help="Output CSV file name")
    
    args = parser.parse_args()
    
    try:
        ts_coeff_list = ast.literal_eval(args.ts_coeff)
    except:
        print("Error parsing --ts_coeff. Ensure it is a valid list string e.g. '[60, 40, 40, 60]'")
        exit(1)

    run_simulation(args, ts_coeff_list)