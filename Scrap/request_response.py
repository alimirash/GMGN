import subprocess
from Scrap.parse_address_details import extract_address_info
import secrets
import uuid
from datetime import timedelta , datetime ,timezone
import jwt

def generate_user_id():
    return str(uuid.uuid4())

def generate_secret_key():
    return secrets.token_hex(32)

def generate_issuer():
    return secrets.token_hex(16)

def create_jwt_header(algorithm="HS256"):
    return {
        "alg": algorithm,
        "typ": "JWT"
    }

def create_jwt_payload(user_id, issuer, exp_hours=1):
    now = datetime.now(timezone.utc)  # Current UTC time (timezone-aware)

    return {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(hours=exp_hours),
        "iss": issuer
    }

def generate_jwt_for_request():
    user_id = generate_user_id()
    secret_key = generate_secret_key()
    issuer = generate_issuer()
    header = create_jwt_header()
    payload = create_jwt_payload(user_id, issuer)
    token = jwt.encode(payload, secret_key, algorithm="HS256", headers=header)
    return {
        "jwt_token": token,
        "secret_key": secret_key,
        "user_id": user_id,
        "issuer": issuer
    }

def scrape_address(address):
    base_url = "https://gmgn.ai/sol/address/"
    url = base_url + address
    request_details = generate_jwt_for_request()
    jwt_token = request_details["jwt_token"]
    cookie = str(uuid.uuid4()) + "." + str(uuid.uuid4())
    curl_command = [
        "curl", "-X", "GET", url,
        "-H", f"Authorization: Bearer {jwt_token}",
        "-H", f"Cookie: session-id={cookie}",
        "-H", "Accept: application/json",
        "-H", "Content-Type: application/json",
        "-H", "User-Agent: PostmanRuntime/7.43.0"
    ]
    result = subprocess.run(curl_command, capture_output=True, text=True)

    response = result.stdout
    status = extract_address_info(address, response)
    return status

