import tenseal as ts
import pandas as pd
import tomli

def load_config():
    with open("config.toml", "rb") as f:
        return tomli.load(f)

class DataHolder:
    def __init__(self):
        self.conf = load_config()
        self.weights = (
            self.conf["scoring"]["w_income"],
            self.conf["scoring"]["w_debt"],
            self.conf["scoring"]["w_late_payment"],
        )

    # ---------------------------------------------------------
    # CKKS ENCRYPTION
    # ---------------------------------------------------------
    def encrypt_ckks(self, row):
        context = ts.context(
            scheme=ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        context.global_scale = 2**40
        context.generate_galois_keys()

        enc_income = ts.ckks_vector(context, [row["income"]])
        enc_debt = ts.ckks_vector(context, [row["debt"]])
        enc_late = ts.ckks_vector(context, [row["late_payments"]])

        return {
            "scheme": "CKKS",
            "context": context.serialize(),
            "ciphertexts": {
                "income": enc_income.serialize(),
                "debt": enc_debt.serialize(),
                "late": enc_late.serialize()
            }
        }

    # ---------------------------------------------------------
    # BFV ENCRYPTION (integer, unbatched)
    # ---------------------------------------------------------
    def encrypt_bfv(self, row):
        context = ts.context(
            scheme=ts.SCHEME_TYPE.BFV,
            poly_modulus_degree=4096,
            plain_modulus=1032193
        )
        context.generate_galois_keys()

        income = ts.bfv_vector(context, [int(row["income"])])
        debt = ts.bfv_vector(context, [int(row["debt"])])
        late = ts.bfv_vector(context, [int(row["late_payments"])])

        return {
            "scheme": "BFV",
            "context": context.serialize(),
            "ciphertexts": {
                "income": income.serialize(),
                "debt": debt.serialize(),
                "late": late.serialize()
            }
        }

    # ---------------------------------------------------------
    # BFV ENCRYPTION (batched SIMD)
    # ---------------------------------------------------------
    def encrypt_bfv_batch(self, row):
        context = ts.context(
            scheme=ts.SCHEME_TYPE.BFV,
            poly_modulus_degree=4096,
            plain_modulus=1032193
        )
        context.generate_galois_keys()

        # Pack the three values in one ciphertext
        vec = ts.bfv_vector(context, [
            int(row["income"]),
            int(row["debt"]),
            int(row["late_payments"])
        ])

        return {
            "scheme": "BFV_BATCH",
            "context": context.serialize(),
            "ciphertexts": vec.serialize()
        }

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def encrypt_row(self, row, scheme="CKKS"):
        if scheme == "CKKS":
            return self.encrypt_ckks(row)
        elif scheme == "BFV":
            return self.encrypt_bfv(row)
        elif scheme == "BFV_BATCH":
            return self.encrypt_bfv_batch(row)
        else:
            raise ValueError("Unknown scheme selected")

if __name__ == "__main__":
    df = pd.read_csv("data/loans.csv")
    holder = DataHolder()

    sample = df.iloc[0]
    encrypted = holder.encrypt_row(sample, scheme="CKKS")
    print("Encrypted sample generated.")
