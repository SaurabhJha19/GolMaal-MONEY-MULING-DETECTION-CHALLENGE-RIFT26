import pandas as pd
from typing import List
from app.models.transaction import Transaction
from app.config import MAX_UPLOAD_ROWS


def load_transactions(file) -> List[Transaction]:
    # Read CSV safely
    df = pd.read_csv(file)

    if len(df) > MAX_UPLOAD_ROWS:
        raise ValueError("Dataset too large")

    # Normalize column names (strip + lowercase)
    df.columns = df.columns.str.strip().str.lower()

    # Flexible column mapping (in case dataset differs slightly)
    column_mapping = {
        "transaction_id": ["transaction_id", "txn_id", "id"],
        "sender_id": ["sender_id", "sender", "from_account"],
        "receiver_id": ["receiver_id", "receiver", "to_account"],
        "amount": ["amount", "transaction_amount", "value"],
        "timestamp": ["timestamp", "date", "transaction_time"]
    }

    resolved_columns = {}

    for standard_col, possible_names in column_mapping.items():
        for name in possible_names:
            if name in df.columns:
                resolved_columns[standard_col] = name
                break

        if standard_col not in resolved_columns:
            raise ValueError(f"Missing required column: {standard_col}")

    # Clean & validate data
    df[resolved_columns["amount"]] = pd.to_numeric(
        df[resolved_columns["amount"]], errors="coerce"
    )

    if df[resolved_columns["amount"]].isnull().any():
        raise ValueError("Invalid amount values detected.")

    df[resolved_columns["timestamp"]] = pd.to_datetime(
        df[resolved_columns["timestamp"]],
        errors="coerce"
    )

    if df[resolved_columns["timestamp"]].isnull().any():
        raise ValueError("Invalid timestamp format detected.")

    # Build Transaction objects
    transactions = []

    for _, row in df.iterrows():
        transaction = Transaction(
            transaction_id=str(row[resolved_columns["transaction_id"]]).strip(),
            sender_id=str(row[resolved_columns["sender_id"]]).strip(),
            receiver_id=str(row[resolved_columns["receiver_id"]]).strip(),
            amount=float(row[resolved_columns["amount"]]),
            timestamp=row[resolved_columns["timestamp"]],
        )

        transactions.append(transaction)

    return transactions