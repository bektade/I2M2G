import os
from pathlib import Path

def look_for_creds() -> tuple:
    """
    Defaults to extracting the cert and key path from environment variables,
    but if those don't exist it tries to find the hidden credentials files 
    in the default folder of /certs.

    Returns: tuple of paths for cert and key files
    """
    # Find if the cred paths are on PATH
    cert = os.getenv('CERT_PATH')
    key = os.getenv('KEY_PATH')
    cert_path = Path('certs/.cert.pem')
    key_path = Path('certs/.key.pem')
    if cert and key:
        return cert, key
    # If not, look in the local directory
    elif cert_path.is_file() and key_path.is_file():
        return (cert_path, key_path)
    else:
        raise FileNotFoundError('Could not find cert and key credentials')