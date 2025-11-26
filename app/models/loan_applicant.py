from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class LoanApplicant:
    """
    Represents a bank customer applying for a loan.
    This model acts as the Single Source of Truth for the data schema.
    """
    person_id: str
    income: int
    debt: int
    late_payments: int
    loan_amount: int

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the object to a dictionary."""
        return asdict(self)

    @staticmethod
    def get_sensitive_fields() -> List[str]:
        """
        Defines which columns require Homomorphic Encryption.
        """
        return ['income', 'debt', 'late_payments']

    @staticmethod
    def get_public_fields() -> List[str]:
        """
        Defines columns that remain in Plaintext (e.g., ID).
        """
        return ['person_id', 'loan_amount']