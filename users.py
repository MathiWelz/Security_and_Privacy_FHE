import os
import json
import pandas as pd
import tenseal as ts
from phe import paillier
from fhe_lib import PaillierTool, TenSEALTool

class DataHolder:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.dataset_path = None
        # Initialize Crypto Tools
        self.phe_tool = PaillierTool()
        self.ts_tool = TenSEALTool()

    def load_dataset(self, filename):
        self.dataset_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
            
        df = pd.read_csv(self.dataset_path)
        print(f"[Holder] Loaded dataset: {len(df)} rows.")
        # IMPORTANT: We only take the Salary column
        return df['Salary'].tolist()

    # --- PAILLIER WORKFLOW ---
    def encrypt_paillier(self, data, filename):
        print(f"[Holder] Encrypting {len(data)} items with Paillier...")
        # The tool now handles the loop and progress printing
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
        
    def decrypt_tenseal(self, filename):
        path = os.path.join(self.data_dir, filename)
        # FIX APPLIED: Changed 'wb' to 'rb' because we are reading results
        with open(path, 'rb') as f:
            proto = f.read()
        enc_vector = ts.ckks_vector_from(self.ts_tool.context, proto)
        result = enc_vector.decrypt()
        # Returns Mean
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
        
        # Operations
        print(f"  > Summing {len(enc_values)} items...")
        total_sum = sum(enc_values)
        
        print("  > Calculating Mean...")
        # Multiply by 1/N
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
    def process_tenseal(self, input_file, output_file, context_helper):
        print("[Analyzer] Processing TenSEAL file...")
        in_path = os.path.join(self.data_dir, input_file)
        
        # FIX APPLIED: Changed 'wb' to 'rb' here as well
        with open(in_path, 'rb') as f:
            proto = f.read()
        
        enc_vector = ts.ckks_vector_from(context_helper.context, proto)
        
        enc_sum = enc_vector.sum()
        enc_mean = enc_sum.mul(1/enc_vector.size())
        
        out_path = os.path.join(self.data_dir, output_file)
        with open(out_path, 'wb') as f:
            f.write(enc_mean.serialize())
        print(f"[Analyzer] Computations complete. Saved to {output_file}")