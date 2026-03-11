import hashlib
import time

def generate_hash(student, course, issuer):
    # Added timestamp so every single certificate is 100% unique
    data = f"{student}{course}{issuer}{time.time()}"
    return hashlib.sha256(data.encode()).hexdigest()