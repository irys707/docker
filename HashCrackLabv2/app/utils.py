def detect_hash_type(hashes):
    if len(hashes.splitlines()[0]) == 32:
        return "0"  # MD5
    elif len(hashes.splitlines()[0]) == 40:
        return "100"  # SHA1
    elif len(hashes.splitlines()[0]) == 32 and hashes.upper().startswith("NTLM"):
        return "1000"  # NTLM
    return "0"
