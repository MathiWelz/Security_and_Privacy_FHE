import time
import configparser
from users import DataHolder, DataAnalyzer

# 1. Setup Configuration
config = configparser.ConfigParser()
config.read('config.ini')

DATA_DIR = config['DEFAULT']['DATA_DIR']
RAW_FILE = config['FILES']['RAW_DATASET']

# 2. Instantiate Users (Actors)
holder = DataHolder(DATA_DIR)
analyzer = DataAnalyzer(DATA_DIR)

def run_simulation():
    print("=== STARTING PRIVACY PRESERVING SALARY AUDIT ===\n")
    
    # 3. Holder Loads Data
    try:
        raw_data = holder.load_dataset(RAW_FILE)
    except FileNotFoundError:
        print("Error: Dataset not found. Run dataset_gen.py first.")
        return

    results_table = []

    # ----------------------------
    # SCHEME A: PAILLIER
    # ----------------------------
    print("\n--- SCHEME 1: PAILLIER ---")
    start_total = time.time()
    
    # Step 1: Encrypt
    t0 = time.time()
    holder.encrypt_paillier(raw_data, config['FILES']['PAILLIER_ENC'])
    t_enc = time.time() - t0

    # Step 2: Analyze (Cloud)
    t0 = time.time()
    analyzer.process_paillier(config['FILES']['PAILLIER_ENC'], config['FILES']['PAILLIER_RES'])
    t_ana = time.time() - t0

    # Step 3: Decrypt
    t0 = time.time()
    p_sum, p_mean = holder.decrypt_paillier(config['FILES']['PAILLIER_RES'])
    t_dec = time.time() - t0

    total_time = time.time() - start_total
    print(f"> Result: Sum={p_sum}, Mean={p_mean}")
    results_table.append(['Paillier', t_enc, t_ana, t_dec, total_time])

    # ----------------------------
    # SCHEME B: TENSEAL
    # ----------------------------
    print("\n--- SCHEME 2: TENSEAL (CKKS) ---")
    start_total = time.time()

    # Step 1: Encrypt
    t0 = time.time()
    holder.encrypt_tenseal(raw_data, config['FILES']['TENSEAL_ENC'])
    t_enc = time.time() - t0

    # Step 2: Analyze (Cloud)
    # Note: We pass holder.ts_tool to provide context (Public Keys)
    t0 = time.time()
    analyzer.process_tenseal(config['FILES']['TENSEAL_ENC'], config['FILES']['TENSEAL_RES'], holder.ts_tool)
    t_ana = time.time() - t0

    # Step 3: Decrypt
    t0 = time.time()
    ts_mean = holder.decrypt_tenseal(config['FILES']['TENSEAL_RES'])
    t_dec = time.time() - t0

    total_time = time.time() - start_total
    print(f"> Result: Mean={ts_mean:.2f}")
    results_table.append(['TenSEAL', t_enc, t_ana, t_dec, total_time])

    # ----------------------------
    # FINAL OUTPUT
    # ----------------------------
    print("\n\n=== PERFORMANCE REPORT (Seconds) ===")
    print(f"{'Scheme':<15} | {'Encrypt':<10} | {'Analysis':<10} | {'Decrypt':<10} | {'Total':<10}")
    print("-" * 65)
    for row in results_table:
        print(f"{row[0]:<15} | {row[1]:<10.5f} | {row[2]:<10.5f} | {row[3]:<10.5f} | {row[4]:<10.5f}")

if __name__ == "__main__":
    run_simulation()