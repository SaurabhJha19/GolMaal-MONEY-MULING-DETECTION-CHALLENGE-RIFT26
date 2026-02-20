import hashlib


def generate_ring_id(member_accounts: list, pattern_type: str):

    key = pattern_type + "_" + "_".join(sorted(member_accounts))
    digest = hashlib.sha256(key.encode()).hexdigest()[:8].upper()

    return f"RING_{digest}"
