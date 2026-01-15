# DAO v1.0 (Metaforo) Watchdog

[中文版](./README_CN.md)

Auditing tool for CKB Community Fund DAO v1.0 voting on Metaforo platform.

## Overview

This tool verifies voting weights on the [CKB Community Fund DAO](https://dao.ckb.community) by comparing Metaforo-recorded weights against actual on-chain Nervos DAO deposits.

## Prerequisites

- Python 3.11+
- Dependencies:

```bash
pip install requests pyckb
```

## Usage

### Method 1: Using Metaforo URL (Recommended)

Simply provide the voting page URL:

```bash
python metaforo_watchdog_en.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
```

The tool will automatically:
1. Parse the thread ID from the URL
2. Fetch all voting options (e.g., Yes, No)
3. Process each option and generate reports

### Method 2: Using Option ID (Advanced)

If you know the specific option ID:

```bash
python metaforo_watchdog_en.py 12551
```

### Docker Usage

You can also run the tool using Docker without installing Python dependencies locally.

1. **Pull the Docker image:**

   ```bash
   docker pull ghcr.io/ckbfansdao/ckb-dao-watchdog/dao-v1-0:main
   ```

2. **Run the tool:**

   ```bash
   docker run -it --rm -v $(pwd)/vote_result:/app/vote_result ghcr.io/ckbfansdao/ckb-dao-watchdog/dao-v1-0:main metaforo_watchdog_en.py <url_or_id>
   ```

## Output

For each voting option, the tool generates:

```
vote_result/{thread_id}/{option}_{timestamp}.json
vote_result/{thread_id}/{option}_{timestamp}.csv
```

Example:
```
vote_result/66568/Yes_20260114220441.json
vote_result/66568/Yes_20260114220441.csv
vote_result/66568/No_20260114220441.json
vote_result/66568/No_20260114220441.csv
```

## Output Fields

| Field | Description |
|-------|-------------|
| `nickname` | User's display name on Metaforo |
| `userid` | User's Metaforo ID |
| `total weight(metaforo)` | Weight recorded by Metaforo platform |
| `total weight(on chain, floored)` | Calculated weight from on-chain DAO deposits |
| `address` | CKB address (Neuron or PW Lock) |
| `address weight(floored)` | DAO deposit weight for this address |
| `need_review` | `true` if weights don't match (requires manual review) |
| `explorer_url` | Link to view address on CKB Explorer |

## How Weight is Calculated

1. **Neuron Addresses**: Directly bound CKB addresses from Neuron wallet
2. **MetaMask/PW Lock**: Ethereum addresses converted to CKB addresses using PW Lock script
3. **DAO Deposits**: Only `nervos_dao_deposit` cells are counted
4. **Unit Conversion**: Shannon → CKB (÷ 10^8), then floored to integer

## Verification Logic

The tool flags `need_review = true` when:
```
floor(total_weight_metaforo) ≠ floor(total_weight_on_chain)
```

This may indicate:
- Recent deposit/withdrawal not yet reflected
- Address binding issues
- Potential discrepancies requiring investigation

## API Endpoints Used

- **Metaforo API**: `https://dao.ckb.community/api`
  - `GET /get_thread/{thread_id}` - Get poll options
  - `POST /poll/list` - Get voters for an option
  - `GET /profile/{user_id}/neurontest` - Get user's bound addresses

- **Nervos Explorer API**: `https://mainnet-api.explorer.nervos.org/api/v1`
  - `GET /address_live_cells/{address}` - Get address's live cells

## Troubleshooting

### Network Errors
The tool includes retry logic and rate limiting (0.5s between requests). If you encounter persistent network errors, try again later.

### No Vote Data
If a voting option has no votes, the tool will skip it and continue with other options.

### Weight Mismatch
A `need_review = true` flag doesn't necessarily indicate fraud. Common causes:
- User deposited/withdrew after voting
- Address not properly bound

## License

MIT License
