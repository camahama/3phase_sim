import hashlib
import datetime

def generate_secret_code(salt="mima_secret_salt", date_str=None):
    if date_str is None:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    data = f"{salt}-{date_str}"
    
    # Use SHA256 for a simple, reproducible hash as the "secret code"
    secret_hash = hashlib.sha256(data.encode()).hexdigest()
    
    # Return a portion of the hash to make it "shorter" for a code
    return secret_hash[:10].upper()

if __name__ == "__main__":
    code = generate_secret_code()
    print(f"Your secret code is: {code}")