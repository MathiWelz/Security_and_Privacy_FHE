import os
import json
import pandas as pd
import tenseal as ts
from phe import paillier
from fhe_lib import PaillierTool, TenSEALTool

class DataHolder:
    def __init__(self, data_dir, phe_n_length=1024, ts_poly=8192, ts_coeff=[60, 40, 40, 60]):
        self.data_dir = data_dir
        self.dataset_path = None
        self.phe_tool = PaillierTool(n_length=phe_n_length)
        self.ts_tool = TenSEALTool(poly_modulus_degree=ts_poly, coeff_mod_bit_sizes=ts_coeff)

    def load_dataset(self, filename):
        self.dataset_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
            
        df = pd.read_csv(self.dataset_path)
        print(f"[Holder] Loaded dataset: {len(df)} rows.")
        return df['Salary'].tolist()

    # --- PAILLIER WORKFLOW ---
    def encrypt_paillier(self, data, filename):
        print(f"[Holder] Encrypting {len(data)} items with Paillier...")
        enc_list = self.phe_tool.encrypt_list(data)
        serialized = self.phe_tool.serialize_encrypted_data(enc_list)
        
        path = os.path.join(self.data_dir, filename)
        with open(path, 'w') as f:
            json.dump(serialized, f)
        print(f"[Holder] Sent encrypted file to: {filename}")

    def decrypt_paillier(self, filename):
        path = os.path.join(self.data_dir, filename)
        with open(path, 'r') as f:
            data = json.load(f)
            
        pub_key = paillier.PaillierPublicKey(n=int(data['public_key']['n']))
        enc_sum = paillier.EncryptedNumber(pub_key, int(data['sum'][0]), int(data['sum'][1]))
        enc_mean = paillier.EncryptedNumber(pub_key, int(data['mean'][0]), int(data['mean'][1]))
        
        dec_sum = self.phe_tool.private_key.decrypt(enc_sum)
        dec_mean = self.phe_tool.private_key.decrypt(enc_mean)
        return dec_sum, dec_mean

    # --- TENSEAL WORKFLOW ---
    def encrypt_tenseal(self, data, filename):
        print("[Holder] Encrypting data with TenSEAL (CKKS)...")
        enc_vector = self.ts_tool.encrypt_vector(data)
        path = os.path.join(self.data_dir, filename)
        with open(path, 'wb') as f:
            f.write(enc_vector.serialize())
        print(f"[Holder] Sent encrypted file to: {filename}")

    def save_tenseal_context(self, filename):
        """Helper to save the key/context for the Analyzer to use."""
        path = os.path.join(self.data_dir, filename)
        self.ts_tool.save_context(path, save_secret=False)
        
    def decrypt_tenseal(self, filename):
        path = os.path.join(self.data_dir, filename)
        with open(path, 'rb') as f:
            proto = f.read()
        enc_vector = ts.ckks_vector_from(self.ts_tool.context, proto)
        result = enc_vector.decrypt()
        return result[0]


class DataAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    # --- PAILLIER ANALYSIS ---
    def process_paillier(self, input_file, output_file):
        print("[Analyzer] Processing Paillier file...")
        in_path = os.path.join(self.data_dir, input_file)
        
        with open(in_path, 'r') as f:
            data = json.load(f)
            
        pub_key = paillier.PaillierPublicKey(n=int(data['public_key']['n']))
        enc_values = [paillier.EncryptedNumber(pub_key, int(x[0]), int(x[1])) for x in data['values']]
        
        print(f"  > Summing {len(enc_values)} items...")
        total_sum = sum(enc_values)
        
        print("  > Calculating Mean...")
        mean = total_sum * (1 / len(enc_values))
        
        results = {
            'public_key': data['public_key'],
            'sum': (str(total_sum.ciphertext()), total_sum.exponent),
            'mean': (str(mean.ciphertext()), mean.exponent)
        }
        
        out_path = os.path.join(self.data_dir, output_file)
        with open(out_path, 'w') as f:
            json.dump(results, f)
        print(f"[Analyzer] Computations complete. Saved to {output_file}")

    # --- TENSEAL ANALYSIS ---
    def process_tenseal(self, input_file, output_file, context_filename):
        print("[Analyzer] Processing TenSEAL file...")
        in_path = os.path.join(self.data_dir, input_file)
        ctx_path = os.path.join(self.data_dir, context_filename)

        # 1. Load the Context (Keys) from text file
        print(f"  > Loading context from {context_filename}...")
        context = TenSEALTool.load_context(ctx_path)
        
        # 2. Load Data
        with open(in_path, 'rb') as f:
            proto = f.read()
        
        enc_vector = ts.ckks_vector_from(context, proto)
        
        # 3. Compute
        enc_sum = enc_vector.sum()
        enc_mean = enc_sum.mul(1/enc_vector.size())
        
        out_path = os.path.join(self.data_dir, output_file)
        with open(out_path, 'wb') as f:
            f.write(enc_mean.serialize())
        print(f"[Analyzer] Computations complete. Saved to {output_file}")