import tenseal as ts
import tomli

def load_config():
    with open("config.toml", "rb") as f:
        return tomli.load(f)

class DataAnalyzer:
    def __init__(self):
        self.conf = load_config()
        self.w1 = self.conf["scoring"]["w_income"]
        self.w2 = self.conf["scoring"]["w_debt"]
        self.w3 = self.conf["scoring"]["w_late_payment"]

    # ---------------------------------------------------------
    # CKKS SCORING
    # ---------------------------------------------------------
    def score_ckks(self, payload):
        context = ts.context_from(payload["context"])
        enc_income = ts.ckks_vector_from(context, payload["ciphertexts"]["income"])
        enc_debt = ts.ckks_vector_from(context, payload["ciphertexts"]["debt"])
        enc_late = ts.ckks_vector_from(context, payload["ciphertexts"]["late"])

        result = (
            enc_income * self.w1 +
            enc_debt * self.w2 +
            enc_late * self.w3
        )
        return result.serialize()

    # ---------------------------------------------------------
    # BFV SCORING (integer)
    # ---------------------------------------------------------
    def score_bfv(self, payload):
        context = ts.context_from(payload["context"])
        enc_income = ts.bfv_vector_from(context, payload["ciphertexts"]["income"])
        enc_debt = ts.bfv_vector_from(context, payload["ciphertexts"]["debt"])
        enc_late = ts.bfv_vector_from(context, payload["ciphertexts"]["late"])

        result = (
            enc_income * int(self.w1) +
            enc_debt * int(self.w2) +
            enc_late * int(self.w3)
        )
        return result.serialize()

    # ---------------------------------------------------------
    # BFV BATCED SCORING (SIMD)
    # ---------------------------------------------------------
    def score_bfv_batch(self, payload):
        context = ts.context_from(payload["context"])
        vec = ts.bfv_vector_from(context, payload["ciphertexts"])

        w = [int(self.w1), int(self.w2), int(self.w3)]
        score_vec = vec.dot(w)        # SIMD dot-product

        return score_vec.serialize()

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def compute_score(self, payload):
        if payload["scheme"] == "CKKS":
            return self.score_ckks(payload)
        elif payload["scheme"] == "BFV":
            return self.score_bfv(payload)
        elif payload["scheme"] == "BFV_BATCH":
            return self.score_bfv_batch(payload)
        else:
            raise ValueError("Unknown scheme")

if __name__ == "__main__":
    print("Analyzer ready.")
