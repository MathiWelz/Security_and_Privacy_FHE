import json
import base64
import tenseal as ts
from phe import paillier

# --- PAILLIER HELPERS ---
class PaillierTool:
    def __init__(self, n_length=1024):
        print(f"[Init] Generating Paillier Keys ({n_length}-bit)...")
        self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=n_length)

    def encrypt_list(self, values):
        encrypted = []
        total = len(values)
        print(f"  > Starting Paillier Encryption of {total} items...")
        
        for i, x in enumerate(values):
            encrypted.append(self.public_key.encrypt(x))
            
            # Progress Indicator: Print every 50 items (much faster feedback)
            if i > 0 and i % 50 == 0:
                print(f"    Processing: {i}/{total}")
                
        print(f"    Processing: {total}/{total}")
        print(f"  > Encryption Complete.")
        return encrypted

    def decrypt_value(self, enc_value):
        return self.private_key.decrypt(enc_value)

    def serialize_encrypted_data(self, enc_list):
        enc_data = {}
        enc_data['public_key'] = {'n': self.public_key.n}
        enc_data['values'] = [(str(x.ciphertext()), x.exponent) for x in enc_list]
        return enc_data

    def deserialize_encrypted_data(self, json_data):
        pub_key = paillier.PaillierPublicKey(n=int(json_data['public_key']['n']))
        return [paillier.EncryptedNumber(pub_key, int(x[0]), int(x[1])) for x in json_data['values']], pub_key

# --- TENSEAL (CKKS) HELPERS ---
class TenSEALTool:
    def __init__(self, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60]):
        # 1. Determine safe Global Scale based on input coefficients
        # Logic: Use the middle coefficient if available, otherwise the last one.
        if len(coeff_mod_bit_sizes) > 2:
            scale_bits = coeff_mod_bit_sizes[1]
        elif len(coeff_mod_bit_sizes) >= 1:
            scale_bits = coeff_mod_bit_sizes[-1]
        else:
            scale_bits = 40 # Default fallback

        print(f"[TenSEAL] Context Init: Poly={poly_modulus_degree}, Coeff={coeff_mod_bit_sizes}, Scale=2^{scale_bits}")

        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_modulus_degree,
            coeff_mod_bit_sizes=coeff_mod_bit_sizes
        )
        # 2. Set the dynamic global scale
        self.context.global_scale = 2**scale_bits
        self.context.generate_galois_keys()

    def encrypt_vector(self, values):
        return ts.ckks_vector(self.context, values)
    
    def save_context(self, filepath, save_secret=False):
        """Saves the context (keys) to a plain text file using Base64."""
        # Get binary data
        data = self.context.serialize(save_secret_key=save_secret)
        # Encode to Base64 string
        b64_data = base64.b64encode(data).decode('utf-8')
        
        with open(filepath, "w") as f:
            f.write(b64_data)
        print(f"[TenSEAL] Context saved as Base64 text to {filepath} (Secret: {save_secret})")

    @staticmethod
    def load_context(filepath):
        """Loads a context from a plain text Base64 file."""
        with open(filepath, "r") as f:
            b64_data = f.read()
        # Decode back to binary
        data = base64.b64decode(b64_data)
        return ts.context_from(data)