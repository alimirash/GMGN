import jwt
import uuid
import time 
import secrets
import subprocess
import cloudscraper
import random
import csv
import requests
from datetime import timedelta , datetime ,timezone
from Scrap.parse_address_details import extract_address_info
from config.configs import PROXY_PATH

def scrape_address(address):
    base_url = "https://gmgn.ai/"
    chain = "sol/address/"
    url = base_url + chain + address
    while True:
        proxies = {
        "https": "scraperapi:8b6236c507a0d670c13c91fc8603395e@proxy-server.scraperapi.com:8001"
        }
        result = requests.get(url, proxies=proxies, verify=False)
        response = result.stdout
        status = extract_address_info(address, response)
        if status == "Successful":
                break
        else:
            print(f"Request failed, retrying {address}")
    return status

# def generate_user_id():
#     return str(uuid.uuid4())

# def generate_secret_key():
#     return secrets.token_hex(32)

# def generate_issuer():
#     return secrets.token_hex(16)

# def create_jwt_header(algorithm="HS256"):
#     return {
#         "alg": algorithm,
#         "typ": "JWT"
#     }

# def create_jwt_payload(user_id, issuer, exp_hours=1):
#     now = datetime.now(timezone.utc)  # Current UTC time (timezone-aware)

#     return {
#         "sub": user_id,
#         "iat": now,
#         "exp": now + timedelta(hours=exp_hours),
#         "iss": issuer
#     }

# def generate_jwt_for_request():
#     user_id = generate_user_id()
#     secret_key = generate_secret_key()
#     issuer = generate_issuer()
#     header = create_jwt_header()
#     payload = create_jwt_payload(user_id, issuer)
#     token = jwt.encode(payload, secret_key, algorithm="HS256", headers=header)
#     return {
#         "jwt_token": token,
#         "secret_key": secret_key,
#         "user_id": user_id,
#         "issuer": issuer
#     }

# def generate_cf_csrf_token():
#     token = secrets.token_hex(16)
#     return token

# def get_cf_clearance(url):
#     scraper = cloudscraper.create_scraper()
#     response = scraper.get(url)
#     return scraper.cookies.get('cf_clearance')

# def read_proxies_from_csv(csv_file_path):
#     proxies = []
#     with open(csv_file_path, "r", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             ip = row["ip"]
#             port = row["port"]
#             protocol = row["protocol"]
#             proxy = f"{protocol}://{ip}:{port}"
#             proxies.append(proxy)
#     return proxies

# def get_random_proxy(proxies):
#     return random.choice(proxies)

# def scrape_address(address):
#     base_url = "https://gmgn.ai/"
#     chain = "sol/address/"
#     url = base_url + chain + address
#     while True:
#         request_details = generate_jwt_for_request()
#         jwt_token = request_details["jwt_token"]
#         cf_csrf_token = generate_cf_csrf_token() 
#         cookie = f"_ga=GA1.1.{uuid.uuid4()}.{int(time.time())}; cf_clearance={get_cf_clearance(base_url)}; __cf_bm={cf_csrf_token}; _ga_0XM0LYXGC8=GS1.1.{int(time.time())}.12.1.{uuid.uuid4()}.0.0.0"
#         proxies = read_proxies_from_csv(PROXY_PATH)
#         proxy = get_random_proxy(proxies)
#         curl_command = [
#             "curl", "-X", "GET", url,
#             "--proxy", proxy,
#             "-H", f"Authorization: Bearer {jwt_token}",
#             "-H", f"Cookie: {cookie}",
#             "-H", "Accept: application/json",
#             "-H", "Content-Type: application/json",
#             "-H", "User-Agent: PostmanRuntime/7.43.0"
#         ]
#         result = subprocess.run(curl_command, capture_output=True, text=True)

#         response = result.stdout
#         status = extract_address_info(address, response)
#         if status == "Successful":
#             break
#         else:
#             print(f"Request failed, retrying {address}")
#     return status