import json
import tenseal as ts
from phe import paillier

# --- PAILLIER HELPERS ---
class PaillierTool:
    def __init__(self):
        # SPEED OPTIMIZATION: Using 1024-bit keys instead of 2048 default.
        # This makes encryption roughly 5-10x faster for demos.
        print("[Init] Generating Paillier Keys (1024-bit)...")
        self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=1024)

    def encrypt_list(self, values):
        encrypted = []
        total = len(values)
        print(f"  > Starting Paillier Encryption of {total} items...")
        
        for i, x in enumerate(values):
            encrypted.append(self.public_key.encrypt(x))
            # Progress Indicator every 10%
            if total > 10 and i % (total // 10) == 0:
                print(f"    Processing: {i}/{total}")
                
        print(f"  > Encryption Complete.")
        return encrypted

    def decrypt_value(self, enc_value):
        return self.private_key.decrypt(enc_value)

    def serialize_encrypted_data(self, enc_list):
        """Prepares encrypted data for JSON file storage."""
        enc_data = {}
        enc_data['public_key'] = {'n': self.public_key.n}
        enc_data['values'] = [(str(x.ciphertext()), x.exponent) for x in enc_list]
        return enc_data

    def deserialize_encrypted_data(self, json_data):
        """Reconstructs encrypted objects from JSON data."""
        pub_key = paillier.PaillierPublicKey(n=int(json_data['public_key']['n']))
        return [paillier.EncryptedNumber(pub_key, int(x[0]), int(x[1])) for x in json_data['values']], pub_key

# --- TENSEAL (CKKS) HELPERS ---
class TenSEALTool:
    def __init__(self):
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        self.context.global_scale = 2**40
        self.context.generate_galois_keys()

    def encrypt_vector(self, values):
        return ts.ckks_vector(self.context, values)
    
    def get_context_bytes(self):
        return self.context.serialize(save_secret_key=True)