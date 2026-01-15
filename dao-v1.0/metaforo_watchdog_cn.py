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

# --- 配置区 ---

# Metaforo API 配置
METAFORO_API_BASE = "https://dao.ckb.community/api"
METAFORO_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'api_key': 'metaforo_website',
    'origin': 'https://dao.ckb.community',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
}

# Nervos Explorer API 配置
EXPLORER_API_BASE = "https://mainnet-api.explorer.nervos.org/api/v1"
EXPLORER_HEADERS = {
    'accept': 'application/vnd.api+json',
    'content-type': 'application/vnd.api+json',
    'origin': 'metaforo.python.script'
}

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 3  # 秒

# --- 函数定义 ---

def is_retryable_error(exception):
    """
    检查异常是否为可重试的网络错误。
    
    可重试的错误包括:
    - 连接被对方重置
    - 连接中断
    - 超时
    - 请求过多 (429)
    - 服务器错误 (5xx)
    """
    if isinstance(exception, requests.exceptions.ConnectionError):
        return True
    if isinstance(exception, requests.exceptions.Timeout):
        return True
    if isinstance(exception, requests.exceptions.HTTPError):
        if exception.response is not None:
            status_code = exception.response.status_code
            # 429 (频率限制) 或 5xx (服务器错误) 时重试
            if status_code == 429 or status_code >= 500:
                return True
    return False


def request_with_retry(method, url, headers, timeout=20, max_retries=MAX_RETRIES, **kwargs):
    """
    带自动重试的 HTTP 请求。
    
    Args:
        method: 'get' 或 'post'
        url: 请求 URL
        headers: 请求头
        timeout: 超时时间（秒）
        max_retries: 最大重试次数
        **kwargs: 传递给 requests 的其他参数
    
    Returns:
        Response 对象
    
    Raises:
        requests.exceptions.RequestException: 如果所有重试都失败
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
            elif method.lower() == 'post':
                response = requests.post(url, headers=headers, timeout=timeout, **kwargs)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            
            if attempt < max_retries and is_retryable_error(e):
                print(f"    网络错误 (第 {attempt + 1}/{max_retries + 1} 次尝试): {e}")
                print(f"    {RETRY_DELAY} 秒后重试...")
                time.sleep(RETRY_DELAY)
            else:
                raise
    
    raise last_exception


def parse_thread_id_from_url(url: str) -> int:
    """
    从 Metaforo 投票页面 URL 中解析出 thread_id。
    
    支持的 URL 格式:
    - https://dao.ckb.community/thread/66568
    - https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
    
    Args:
        url: Metaforo 投票页面的 URL
    
    Returns:
        thread_id 整数
    
    Raises:
        ValueError: 如果无法从 URL 中解析出 thread_id
    """
    # 匹配 URL 末尾的数字（thread_id 总是在最后）
    match = re.search(r'(\d+)$', url.rstrip('/'))
    if match:
        return int(match.group(1))
    raise ValueError(f"无法从 URL 中解析 thread_id: {url}")


def get_poll_options(thread_id: int):
    """
    通过 thread_id 获取投票的所有选项信息。
    
    Args:
        thread_id: 帖子 ID
    
    Returns:
        包含所有选项信息的列表，每个元素包含 {"id": option_id, "html": option_name}
        如果失败则返回 None
    """
    print(f"正在获取帖子 {thread_id} 的投票选项信息...")
    try:
        url = f"{METAFORO_API_BASE}/get_thread/{thread_id}?sort=old&group_name=neurontest"
        response = request_with_retry('get', url, headers=METAFORO_HEADERS)
        data = response.json()
        
        if data.get("status") and data["code"] == 20000:
            thread_data = data.get("data", {}).get("thread", {})
            polls = thread_data.get("polls", [])
            
            if not polls:
                print("该帖子没有投票信息。")
                return None
            
            # 获取第一个 poll 的所有 options
            poll = polls[0]
            options = poll.get("options", [])
            
            if not options:
                print("投票没有选项信息。")
                return None
            
            print(f"找到 {len(options)} 个投票选项:")
            for opt in options:
                print(f"  - {opt.get('html')} (ID: {opt.get('id')}, 投票数: {opt.get('voters')}, 权重: {opt.get('weights')})")
            
            return [{"id": opt.get("id"), "html": opt.get("html")} for opt in options], thread_id
        else:
            print(f"获取帖子信息失败: {data.get('description')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求 get_thread 接口时发生网络错误 (所有重试均失败): {e}")
        return None


def metamask_to_ckb_address(metamask_address: str, mainnet: bool = True) -> str:
    """
    将 MetaMask (Ethereum) 地址转换为 CKB 地址（使用 PW Lock）。
    
    Args:
        metamask_address: MetaMask 地址，如 "0xf93178475F922083335B91c4B9a70E66172A8391"
        mainnet: 是否为主网地址，默认为 True
    
    Returns:
        CKB 地址字符串
    """
    if not metamask_address:
        return ""
    
    # 配置网络
    pyckb.config.current = pyckb.config.mainnet if mainnet else pyckb.config.testnet
    
    # PW Lock script 参数
    # Code Hash: 0xbf43c3602455798c1a61a596e0d95278864c552fafe231c063b3fabf97a8febc
    # Hash Type: type (1)
    code_hash = bytearray.fromhex("bf43c3602455798c1a61a596e0d95278864c552fafe231c063b3fabf97a8febc")
    hash_type = pyckb.core.script_hash_type_type  # type = 1
    
    # 将 MetaMask 地址转换为 args（移除 0x 前缀）
    address_hex = metamask_address[2:] if metamask_address.startswith("0x") else metamask_address
    args = bytearray.fromhex(address_hex.lower())
    
    # 创建 PW Lock script
    script = pyckb.core.Script(code_hash, hash_type, args)
    
    # 生成 CKB 地址
    return script.addr()

def get_all_votes(option_id: int):
    """
    分页获取指定投票选项的所有投票记录。
    """
    all_votes = []
    page = 1 # Metaforo 的 page 参数从 1 开始
    while True:
        print(f"正在获取投票列表第 {page} 页...")
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
                    print("已获取所有投票数据。")
                    break
                all_votes.extend(vote_list)
                page += 1
            else:
                print(f"获取投票列表失败: {data.get('description')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"请求 poll/list 接口时发生网络错误 (所有重试均失败): {e}")
            return None
        time.sleep(0.5) # 避免请求过于频繁
    return all_votes

def get_user_dao_addresses(user_id: int):
    """
    获取用户绑定的 Nervos DAO 地址列表，包括 Neuron 地址和通过 web3_public_key 转换的 PW Lock 地址。
    
    Returns:
        地址列表（包含 neuron_addresses 和通过 web3_public_key 转换的地址）
    """
    print(f"  正在查询用户 {user_id} 绑定的地址...")
    try:
        url = f"{METAFORO_API_BASE}/profile/{user_id}/neurontest"
        response = request_with_retry('get', url, headers=METAFORO_HEADERS)
        data = response.json()
        if data.get("status") and data["code"] == 20000:
            user_data = data.get("data", {}).get("user", {})
            addresses = list(user_data.get("neuron_addresses", []))
            
            # 获取 web3_public_key 并转换为 CKB 地址
            web3_public_key = user_data.get("web3_public_key", "")
            if web3_public_key:
                pwlock_address = metamask_to_ckb_address(web3_public_key, mainnet=True)
                if pwlock_address and pwlock_address not in addresses:
                    addresses.append(pwlock_address)
                    print(f"    已通过 web3_public_key ({web3_public_key[:10]}...) 转换得到 PW Lock 地址")
            
            return addresses
        else:
            print(f"  获取用户 {user_id} 地址失败: {data.get('description')}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"  请求 profile 接口时发生网络错误 (所有重试均失败): {e}")
        return []

def get_address_onchain_weight(address: str):
    """
    分页获取并计算单个 CKB 地址在 Nervos DAO 中的总权重。
    """
    total_capacity = 0
    page = 1
    page_size = 20
    print(f"    正在计算地址 {address[:15]}... 的链上权重...")

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
                break # 已是最后一页
            page += 1
        except requests.exceptions.RequestException as e:
            # 404 错误不可重试（地址不存在），仅记录并继续
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                print(f"    地址在 explorer 中未找到 (404): {address[:15]}...")
            else:
                print(f"    请求 explorer 接口时发生网络错误 (所有重试均失败): {e}")
            break
        except (json.JSONDecodeError, KeyError) as e:
            print(f"    解析 explorer 接口返回数据时出错: {e}")
            break
        time.sleep(0.5) # 避免请求过于频繁

    # 将 shannon 转换为 CKB，并向下取整
    return math.floor(total_capacity / (10**8))

def process_option(option_id: int, option_name: str, thread_id: int, timestamp: str):
    """
    处理单个投票选项，获取投票数据并导出文件。
    
    Args:
        option_id: 投票选项 ID
        option_name: 投票选项名称（如 "Yes", "No"）
        thread_id: 帖子 ID
        timestamp: 时间戳字符串
    
    Returns:
        导出的文件路径列表 [json_path, csv_path]，失败则返回 None
    """
    print(f"\n{'='*80}")
    print(f"开始处理投票选项: {option_name} (ID: {option_id})")
    print(f"{'='*80}")

    # 1. 获取所有投票记录
    voters_data = get_all_votes(option_id)
    if not voters_data:
        print(f"选项 {option_name} 未获取到任何投票数据。")
        return None

    print(f"\n--- 选项 [{option_name}] 初始投票数据 ---")
    print("昵称\t\t投票时间\t\t\t投票权重")
    print("-" * 60)
    for vote in voters_data:
        name_display = vote.get('name', 'N/A').ljust(15)
        print(f"{name_display}\t{vote.get('last_time', 'N/A')}\t{vote.get('weight', 0)}")
    print("-" * 60)

    # 2. & 3. 遍历投票者，获取地址并计算链上权重
    print(f"\n开始获取选项 [{option_name}] 每个用户的链上权重...")
    for i, vote in enumerate(voters_data):
        user_id = vote.get("user_id")
        print(f"\n正在处理第 {i+1}/{len(voters_data)} 个用户: {vote.get('name', 'N/A')} (ID: {user_id})")
        
        if not user_id:
            vote["weight_list"] = []
            vote["weight_calc"] = 0
            continue

        addresses = get_user_dao_addresses(user_id)
        if not addresses:
            print(f"  用户 {user_id} 未绑定任何地址。")
            vote["weight_list"] = []
            vote["weight_calc"] = 0
            continue
        
        weight_list = []
        total_onchain_weight = 0
        for address in addresses:
            onchain_weight = get_address_onchain_weight(address)
            weight_list.append({"address": address, "Weight": onchain_weight})
            total_onchain_weight += onchain_weight
            print(f"    地址 {address[:15]}... 的权重为: {onchain_weight:,.2f} CKB")
        
        vote["weight_list"] = weight_list
        vote["weight_calc"] = total_onchain_weight
        print(f"  用户 {user_id} 的链上总权重计算完成: {total_onchain_weight:,.2f} CKB")
        print(f"  Metaforo 记录的权重: {vote.get('weight', 0)}")

    # 4. 最终结果输出
    print(f"\n\n--- 选项 [{option_name}] 最终权重验证结果 ---")
    for vote in voters_data:
        print("\n" + "=" * 80)
        print(f"昵称: {vote.get('name', 'N/A')} (ID: {vote.get('user_id')})")
        print(f"Metaforo 记录权重: {vote.get('weight', 0):,.2f}")
        print(f"计算出的链上总权重: {vote.get('weight_calc', 0):,.2f}")
        print("-" * 40)
        print("绑定的地址及各自权重:")
        if vote.get('weight_list'):
            for item in vote['weight_list']:
                print(f"  - 地址: {item['address']}")
                print(f"    权重: {item['Weight']:,.2f} CKB")
        else:
            print("  - 未绑定地址或未能查询到权重。")
    print("=" * 80)

    # 5. 导出 JSON 和 CSV 文件
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
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 文件名格式: vote_result_{thread_id}_{option_name}_{timestamp}
    safe_option_name = re.sub(r'[^\w\-]', '_', option_name)  # 替换特殊字符
    json_path = os.path.join(script_dir, f"./vote_result/{thread_id}/{safe_option_name}_{timestamp}.json")
    csv_path = os.path.join(script_dir, f"./vote_result/{thread_id}/{safe_option_name}_{timestamp}.csv")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(json_path)
    os.makedirs(output_dir, exist_ok=True)

    # 保存 JSON 文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=4)
    print(f"\nJSON 文件已保存至: {json_path}")
    
    # 保存 CSV 文件
    if export_data:
        fieldnames = ["nickname", "userid", "total weight(metaforo)", "total weight(on chain, floored)", "⚠️need_review", "address", "address weight(floored)", "explorer_url"]
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(export_data)
        print(f"CSV 文件已保存至: {csv_path}")
    
    return [json_path, csv_path]


def main():
    """
    主执行函数
    
    支持两种调用方式:
    1. python metaforo.dao.zh.py <metaforo_url>
       例如: python metaforo.dao.zh.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
    2. python metaforo.dao.zh.py <option_id>  (向后兼容)
    """
    if len(sys.argv) < 2:
        print("用法: python metaforo.dao.zh.py <metaforo_url>")
        print("示例: python metaforo.dao.zh.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568")
        sys.exit(1)

    arg = sys.argv[1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 判断输入是 URL 还是 option_id
    if arg.startswith("http"):
        # URL 模式: 解析 thread_id 并获取所有选项
        try:
            thread_id = parse_thread_id_from_url(arg)
            print(f"从 URL 解析得到 thread_id: {thread_id}")
        except ValueError as e:
            print(f"错误: {e}")
            sys.exit(1)
        
        result = get_poll_options(thread_id)
        if not result:
            print("无法获取投票选项信息，脚本终止。")
            sys.exit(1)
        
        options, thread_id = result
        
        print(f"\n开始处理所有 {len(options)} 个投票选项...\n")
        
        all_files = []
        for option in options:
            option_id = option["id"]
            option_name = option["html"]
            files = process_option(option_id, option_name, thread_id, timestamp)
            if files:
                all_files.extend(files)
        
        print(f"\n{'='*80}")
        print("所有投票选项处理完毕！")
        print(f"共生成 {len(all_files)} 个文件:")
        for f in all_files:
            print(f"  - {f}")
    else:
        # 向后兼容: 直接传入 option_id
        try:
            option_id = int(arg)
        except ValueError:
            print("错误: 参数必须是 Metaforo URL 或 option_id 整数。")
            sys.exit(1)
        
        print(f"开始验证投票选项 ID: {option_id}\n")
        process_option(option_id, str(option_id), option_id, timestamp)


if __name__ == "__main__":
    main()
