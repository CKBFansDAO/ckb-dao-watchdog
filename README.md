# CKB DAO Watchdog 🐕

[中文版](./README_CN.md)

Community-driven tools for auditing and verifying CKB DAO governance voting results.

## Overview

CKB DAO Watchdog is a collection of open-source tools that enable community members to independently verify DAO voting results. By comparing on-chain data with platform-recorded weights, these tools help ensure transparency and integrity in CKB DAO governance.

## Features

- **Independent Verification**: Verify voting weights against on-chain Nervos DAO deposits
- **Multi-Platform Support**: Currently supports Metaforo (DAO v1.0), with DAO v1.1 coming soon
- **Transparent Auditing**: Export detailed JSON/CSV reports for community review
- **Bilingual**: Available in both English and Chinese

## Directory Structure

```
ckb-dao-watchdog/
├── .gitignore                   # Git ignore file
├── LICENSE                      # MIT License
├── README.md                    # English documentation
├── README_CN.md                 # Chinese documentation
│
├── dao-v1.0/                    # DAO v1.0 (Metaforo) auditing tools
│   ├── metaforo_watchdog_en.py  # English version script
│   ├── metaforo_watchdog_cn.py  # Chinese version script
│   ├── README.md                # Detailed English guide
│   └── README_CN.md             # Detailed Chinese guide
│
└── dao-v1.1/                    # DAO v1.1 tools (coming soon)
    └── README.md                # Coming soon notice
```

## Quick Start

### Prerequisites

- Python 3.11+
- Required packages:

```bash
pip install requests pyckb
```

### Usage

```bash
# Navigate to dao-v1.0 directory
cd dao-v1.0

# Run with Metaforo voting page URL
python metaforo_watchdog_en.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
```

See [dao-v1.0/README.md](./dao-v1.0/README.md) for detailed usage instructions.

## How It Works

1. **Parse URL**: Extract thread ID from Metaforo voting page URL
2. **Fetch Poll Options**: Get all voting options (e.g., Yes/No) via Metaforo API
3. **Get Voter Data**: Retrieve all voters and their recorded weights for each option
4. **Query On-Chain Data**: For each voter:
   - Get their bound CKB addresses (Neuron + MetaMask/PW Lock)
   - Query Nervos DAO deposits via Explorer API
   - Calculate actual on-chain weight
5. **Compare & Report**: Compare Metaforo weights with on-chain weights, flag discrepancies

## Output Files

For each voting option, the tool generates:
- `vote_result_{thread_id}_{option}_{timestamp}.json`
- `vote_result_{thread_id}_{option}_{timestamp}.csv`

Fields include:
- `nickname`, `userid`
- `total weight(metaforo)` - Weight recorded by Metaforo
- `total weight(on chain, floored)` - Calculated on-chain weight
- `address`, `address weight(floored)`
- `need_review` - Flag for discrepancies requiring manual review
- `explorer_url` - Link to address on CKB Explorer

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Related Links

- [CKB Community Fund DAO](https://dao.ckb.community)
- [Nervos CKB Explorer](https://explorer.nervos.org)
- [CKBFans](https://github.com/ckbfans)