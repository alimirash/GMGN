import subprocess
from Scrap.parse_address_details import extract_address_info
import secrets
import uuid

def scrape_address(address):
    base_url = "https://gmgn.ai/sol/address/"
    url = base_url + address
    authorization_token = secrets.token_hex(36)
    cookie = str(uuid.uuid4()) + "." + str(uuid.uuid4())
    # proxy = "http://your-proxy-server:port"
    curl_command = [
        "curl", "-X", "GET", url,
        # "-x", proxy,
        "-H", f"Authorization: Bearer {authorization_token}",
        "-H", f"Cookie: session-id={cookie}",
        "-H", "Accept: application/json",
        "-H", "Content-Type: application/json",
        "-H", "User-Agent: PostmanRuntime/7.43.0"
    ]
    result = subprocess.run(curl_command, capture_output=True, text=True)

    response = result.stdout
    status = extract_address_info(address, response)
    return status

