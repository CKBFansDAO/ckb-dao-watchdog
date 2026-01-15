import requests
import json
import sys
import time
import csv
import os
import math
import re
import pyckb
from datetime import datetime

# --- Configuration ---

# Metaforo API Configuration
METAFORO_API_BASE = "https://dao.ckb.community/api"
METAFORO_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'api_key': 'metaforo_website',
    'origin': 'https://dao.ckb.community',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
}

# Nervos Explorer API Configuration
EXPLORER_API_BASE = "https://mainnet-api.explorer.nervos.org/api/v1"
EXPLORER_HEADERS = {
    'accept': 'application/vnd.api+json',
    'content-type': 'application/vnd.api+json',
    'origin': 'metaforo.python.script'
}

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds

# --- Function Definitions ---

def is_retryable_error(exception):
    """
    Check if the exception is a retryable network error.
    
    Retryable errors include:
    - Connection reset by peer
    - Connection aborted
    - Timeout
    - Too many requests (429)
    - Server errors (5xx)
    """
    if isinstance(exception, requests.exceptions.ConnectionError):
        return True
    if isinstance(exception, requests.exceptions.Timeout):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        if exception.response is not None:
            status_code = exception.response.status_code
            # Retry on 429 (rate limit) or 5xx (server error)
            if status_code == 429 or status_code >= 500:
                return True
    return False


def request_with_retry(method, url, headers, timeout=20, max_retries=MAX_RETRIES, **kwargs):
    """
    Make HTTP request with automatic retry on retryable errors.
    
    Args:
        method: 'get' or 'post'
        url: Request URL
        headers: Request headers
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
        **kwargs: Additional arguments passed to requests
    
    Returns:
        Response object
    
    Raises:
        requests.exceptions.RequestException: If all retries failed
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
            elif method.lower() == 'post':
                response = requests.post(url, headers=headers, timeout=timeout, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            
            if attempt < max_retries and is_retryable_error(e):
                print(f"    Network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                print(f"    Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise
    
    raise last_exception


def parse_thread_id_from_url(url: str) -> int:
    """
    Parse thread_id from Metaforo voting page URL.
    
    Supported URL formats:
    - https://dao.ckb.community/thread/66568
    - https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
    
    Args:
        url: Metaforo voting page URL
    
    Returns:
        thread_id integer
    
    Raises:
        ValueError: If thread_id cannot be parsed from URL
    """
    # Match digits at the end of URL (thread_id is always at the end)
    match = re.search(r'(\d+)$', url.rstrip('/'))
    if match:
        return int(match.group(1))
    raise ValueError(f"Cannot parse thread_id from URL: {url}")


def get_poll_options(thread_id: int):
    """
    Get all poll options for a thread by thread_id.
    
    Args:
        thread_id: Thread ID
    
    Returns:
        List of option info, each containing {"id": option_id, "html": option_name}
        Returns None if failed
    """
    print(f"Fetching poll options for thread {thread_id}...")
    try:
        url = f"{METAFORO_API_BASE}/get_thread/{thread_id}?sort=old&group_name=neurontest"
        response = request_with_retry('get', url, headers=METAFORO_HEADERS)
        data = response.json()
        
        if data.get("status") and data["code"] == 20000:
            thread_data = data.get("data", {}).get("thread", {})
            polls = thread_data.get("polls", [])
            
            if not polls:
                print("This thread has no poll information.")
                return None
            
            # Get all options from the first poll
            poll = polls[0]
            options = poll.get("options", [])
            
            if not options:
                print("Poll has no option information.")
                return None
            
            print(f"Found {len(options)} poll options:")
            for opt in options:
                print(f"  - {opt.get('html')} (ID: {opt.get('id')}, Voters: {opt.get('voters')}, Weight: {opt.get('weights')})")
            
            return [{"id": opt.get("id"), "html": opt.get("html")} for opt in options], thread_id
        else:
            print(f"Failed to get thread info: {data.get('description')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error when requesting get_thread API (all retries failed): {e}")
        return None


def metamask_to_ckb_address(metamask_address: str, mainnet: bool = True) -> str:
    """
    Convert MetaMask (Ethereum) address to CKB address (using PW Lock).
    
    Args:
        metamask_address: MetaMask address, e.g. "0xf93178475F922083335B91c4B9a70E66172A8391"
        mainnet: Whether to generate mainnet address, defaults to True
    
    Returns:
        CKB address string
    """
    if not metamask_address:
        return ""
    
    # Configure network
    pyckb.config.current = pyckb.config.mainnet if mainnet else pyckb.config.testnet
    
    # PW Lock script parameters
    # Code Hash: 0xbf43c3602455798c1a61a596e0d95278864c552fafe231c063b3fabf97a8febc
    # Hash Type: type (1)
    code_hash = bytearray.fromhex("bf43c3602455798c1a61a596e0d95278864c552fafe231c063b3fabf97a8febc")
    hash_type = pyckb.core.script_hash_type_type  # type = 1
    
    # Convert MetaMask address to args (remove 0x prefix)
    address_hex = metamask_address[2:] if metamask_address.startswith("0x") else metamask_address
    args = bytearray.fromhex(address_hex.lower())
    
    # Create PW Lock script
    script = pyckb.core.Script(code_hash, hash_type, args)
    
    # Generate CKB address
    return script.addr()

def get_all_votes(option_id: int):
    """
    Fetch all vote records for a specific poll option with pagination.
    """
    all_votes = []
    page = 1 # Metaforo page parameter starts from 1
    while True:
        print(f"Fetching vote list page {page}...")
        payload = {
            'option_id': (None, str(option_id)),
            'page': (None, str(page)),
            'group_name': (None, 'neurontest')
        }
        try:
            response = request_with_retry('post', f"{METAFORO_API_BASE}/poll/list", headers=METAFORO_HEADERS, files=payload)
            data = response.json()

            if data.get("status") and data["code"] == 20000:
                vote_list = data.get("data", {}).get("list", [])
                if not vote_list:
                    print("All vote data fetched.")
                    break
                all_votes.extend(vote_list)
                page += 1
            else:
                print(f"Failed to fetch vote list: {data.get('description')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error when requesting poll/list API (all retries failed): {e}")
            return None
        time.sleep(0.5) # Avoid too frequent requests
    return all_votes

def get_user_dao_addresses(user_id: int):
    """
    Get user's bound Nervos DAO address list, including Neuron addresses and PW Lock address converted from web3_public_key.
    
    Returns:
        Address list (containing neuron_addresses and address converted from web3_public_key)
    """
    print(f"  Querying addresses bound to user {user_id}...")
    try:
        url = f"{METAFORO_API_BASE}/profile/{user_id}/neurontest"
        response = request_with_retry('get', url, headers=METAFORO_HEADERS)
        data = response.json()
        if data.get("status") and data["code"] == 20000:
            user_data = data.get("data", {}).get("user", {})
            addresses = list(user_data.get("neuron_addresses", []))
            
            # Get web3_public_key and convert to CKB address
            web3_public_key = user_data.get("web3_public_key", "")
            if web3_public_key:
                pwlock_address = metamask_to_ckb_address(web3_public_key, mainnet=True)
                if pwlock_address and pwlock_address not in addresses:
                    addresses.append(pwlock_address)
                    print(f"    Converted web3_public_key ({web3_public_key[:10]}...) to PW Lock address")
            
            return addresses
        else:
            print(f"  Failed to get addresses for user {user_id}: {data.get('description')}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"  Network error when requesting profile API (all retries failed): {e}")
        return []

def get_address_onchain_weight(address: str):
    """
    Fetch and calculate the total weight of a single CKB address in Nervos DAO with pagination.
    """
    total_capacity = 0
    page = 1
    page_size = 20
    print(f"    Calculating on-chain weight for address {address[:15]}...")

    while True:
        try:
            url = f"{EXPLORER_API_BASE}/address_live_cells/{address}?page={page}&page_size={page_size}&sort=capacity.desc"
            response = request_with_retry('get', url, headers=EXPLORER_HEADERS)
            data = response.json().get("data", [])

            for cell in data:
                attributes = cell.get("attributes", {})
                if attributes.get("cell_type") == "nervos_dao_deposit":
                    capacity = float(attributes.get("capacity", 0))
                    total_capacity += capacity

            if len(data) < page_size:
                break # Last page reached
            page += 1
        except requests.exceptions.RequestException as e:
            # 404 errors are not retryable (address doesn't exist), just log and continue
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                print(f"    Address not found in explorer (404): {address[:15]}...")
            else:
                print(f"    Network error when requesting explorer API (all retries failed): {e}")
            break
        except (json.JSONDecodeError, KeyError) as e:
            print(f"    Error parsing explorer API response: {e}")
            break
        time.sleep(0.5) # Avoid too frequent requests

    # Convert shannon to CKB and floor the result
    return math.floor(total_capacity / (10**8))

def process_option(option_id: int, option_name: str, thread_id: int, timestamp: str):
    """
    Process a single poll option, fetch vote data and export files.
    
    Args:
        option_id: Poll option ID
        option_name: Poll option name (e.g. "Yes", "No")
        thread_id: Thread ID
        timestamp: Timestamp string
    
    Returns:
        List of exported file paths [json_path, csv_path], None if failed
    """
    print(f"\n{'='*80}")
    print(f"Processing poll option: {option_name} (ID: {option_id})")
    print(f"{'='*80}")

    # 1. Fetch all vote records
    voters_data = get_all_votes(option_id)
    if not voters_data:
        print(f"Option {option_name} has no vote data.")
        return None

    print(f"\n--- Option [{option_name}] Initial Vote Data ---")
    print("Nickname\t\tVote Time\t\t\tVote Weight")
    print("-" * 60)
    for vote in voters_data:
        name_display = vote.get('name', 'N/A').ljust(15)
        print(f"{name_display}\t{vote.get('last_time', 'N/A')}\t{vote.get('weight', 0)}")
    print("-" * 60)

    # 2. & 3. Iterate through voters, get addresses and calculate on-chain weight
    print(f"\nFetching on-chain weight for option [{option_name}] users...")
    for i, vote in enumerate(voters_data):
        user_id = vote.get("user_id")
        print(f"\nProcessing user {i+1}/{len(voters_data)}: {vote.get('name', 'N/A')} (ID: {user_id})")
        
        if not user_id:
            vote["weight_list"] = []
            vote["weight_calc"] = 0
            continue

        addresses = get_user_dao_addresses(user_id)
        if not addresses:
            print(f"  User {user_id} has no bound addresses.")
            vote["weight_list"] = []
            vote["weight_calc"] = 0
            continue
        
        weight_list = []
        total_onchain_weight = 0
        for address in addresses:
            onchain_weight = get_address_onchain_weight(address)
            weight_list.append({"address": address, "Weight": onchain_weight})
            total_onchain_weight += onchain_weight
            print(f"    Address {address[:15]}... weight: {onchain_weight:,.2f} CKB")
        
        vote["weight_list"] = weight_list
        vote["weight_calc"] = total_onchain_weight
        print(f"  User {user_id} on-chain total weight calculated: {total_onchain_weight:,.2f} CKB")
        print(f"  Metaforo recorded weight: {vote.get('weight', 0)}")

    # 4. Final result output
    print(f"\n\n--- Option [{option_name}] Final Weight Verification Results ---")
    for vote in voters_data:
        print("\n" + "=" * 80)
        print(f"Nickname: {vote.get('name', 'N/A')} (ID: {vote.get('user_id')})")
        print(f"Metaforo recorded weight: {vote.get('weight', 0):,.2f}")
        print(f"Calculated on-chain total weight: {vote.get('weight_calc', 0):,.2f}")
        print("-" * 40)
        print("Bound addresses and their weights:")
        if vote.get('weight_list'):
            for item in vote['weight_list']:
                print(f"  - Address: {item['address']}")
                print(f"    Weight: {item['Weight']:,.2f} CKB")
        else:
            print("  - No bound addresses or unable to query weight.")
    print("=" * 80)

    # 5. Export JSON and CSV files
    export_data = []
    for vote in voters_data:
        nickname = vote.get('name', 'N/A')
        userid = vote.get('user_id')
        total_weight_metaforo = vote.get('weight', 0)
        total_weight_onchain = vote.get('weight_calc', 0)
        weight_list = vote.get('weight_list', [])
        
        need_review = total_weight_metaforo != math.floor(total_weight_onchain)
        
        if weight_list:
            for item in weight_list:
                address = item['address']
                export_data.append({
                    "nickname": nickname,
                    "userid": userid,
                    "total weight(metaforo)": total_weight_metaforo,
                    "total weight(on chain, floored)": math.floor(total_weight_onchain),
                    "address": address,
                    "address weight(floored)": math.floor(item['Weight']),
                    "⚠️need_review": need_review,
                    "explorer_url": f"https://explorer.app5.org/address/{address}"
                })
        else:
            export_data.append({
                "nickname": nickname,
                "userid": userid,
                "total weight(metaforo)": total_weight_metaforo,
                "total weight(on chain, floored)": math.floor(total_weight_onchain),
                "⚠️need_review": need_review,
                "address": "",
                "address weight(floored)": 0,
                "explorer_url": ""
            })
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Filename format: vote_result_{thread_id}_{option_name}_{timestamp}
    safe_option_name = re.sub(r'[^\w\-]', '_', option_name)  # Replace special characters
    json_path = os.path.join(script_dir, f"./vote_result/{thread_id}/{safe_option_name}_{timestamp}.json")
    csv_path = os.path.join(script_dir, f"./vote_result/{thread_id}/{safe_option_name}_{timestamp}.csv")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(json_path)
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=4)
    print(f"\nJSON file saved to: {json_path}")
    
    # Save CSV file
    if export_data:
        fieldnames = ["nickname", "userid", "total weight(metaforo)", "total weight(on chain, floored)", "⚠️need_review", "address", "address weight(floored)", "explorer_url"]
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(export_data)
        print(f"CSV file saved to: {csv_path}")
    
    return [json_path, csv_path]


def main():
    """
    Main execution function
    
    Supports two calling methods:
    1. python metaforo_watchdog_en.py <metaforo_url>
       Example: python metaforo_watchdog_en.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
    2. python metaforo_watchdog_en.py <option_id>  (backward compatible)
    """
    if len(sys.argv) < 2:
        print("Usage: python metaforo_watchdog_en.py <metaforo_url>")
        print("Example: python metaforo_watchdog_en.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568")
        sys.exit(1)

    arg = sys.argv[1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Determine if input is URL or option_id
    if arg.startswith("http"):
        # URL mode: parse thread_id and get all options
        try:
            thread_id = parse_thread_id_from_url(arg)
            print(f"Parsed thread_id from URL: {thread_id}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        result = get_poll_options(thread_id)
        if not result:
            print("Failed to get poll options, script terminated.")
            sys.exit(1)
        
        options, thread_id = result
        
        print(f"\nProcessing all {len(options)} poll options...\n")
        
        all_files = []
        for option in options:
            option_id = option["id"]
            option_name = option["html"]
            files = process_option(option_id, option_name, thread_id, timestamp)
            if files:
                all_files.extend(files)
        
        print(f"\n{'='*80}")
        print("All poll options processed!")
        print(f"Generated {len(all_files)} files:")
        for f in all_files:
            print(f"  - {f}")
    else:
        # Backward compatible: direct option_id input
        try:
            option_id = int(arg)
        except ValueError:
            print("Error: Argument must be a Metaforo URL or option_id integer.")
            sys.exit(1)
        
        print(f"Starting vote verification for option ID: {option_id}\n")
        process_option(option_id, str(option_id), option_id, timestamp)


if __name__ == "__main__":
    main()
