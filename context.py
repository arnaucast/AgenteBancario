
from dataclasses import dataclass

@dataclass
class BankingContext:
    nif: str = None  # The NIF will be set via Streamlit

