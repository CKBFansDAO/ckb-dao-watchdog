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
vote_result/{thread_id}/{option}_{weight}CKB_{timestamp}.json
vote_result/{thread_id}/{option}_{weight}CKB_{timestamp}.csv
```

Example:

```
vote_result/66568/Yes_63660826CKB_20260114_220441(UTC+8).json
vote_result/66568/Yes_63660826CKB_20260114_220441(UTC+8).csv
vote_result/66568/No_152820057CKB_20260114_220441(UTC+8).json
vote_result/66568/No_152820057CKB_20260114_220441(UTC+8).csv
```

## Output Fields

| Field | Description |
|-------|-------------|
| `nickname` | Voter's nickname on Metaforo |
| `userid` | Voter's user ID |
| `voted_at` | Voting timestamp (UTC+0) |
| `total weight(metaforo)` | Weight recorded on Metaforo |
| `total weight(on chain, floored)` | Calculated on-chain weight (floored) |
| `⚠️need_review` | `true` if weights don't match (requires manual review) |
| `address` | Bound CKB address |
| `address weight(floored)` | Weight for this address (floored) |
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

## Output Example

```bash
aabbcc@192 ckb-dao-watchdog % /usr/local/bin/python3 /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/metaforo_watchdog_en.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
Parsed thread_id from URL: 66568
Fetching poll options for thread 66568...
Found 2 poll options:
  - Yes (ID: 12551, Voters: 15, Weight: 92994150)
  - No (ID: 12552, Voters: 8, Weight: 152820057)

Processing all 2 poll options...


================================================================================
Processing poll option: Yes (ID: 12551)
================================================================================
Fetching vote list page 1...
Fetching vote list page 2...
Fetching vote list page 3...
All vote data fetched.

--- Option [Yes] Initial Vote Data ---
Nickname                Vote Time                       Vote Weight
------------------------------------------------------------
5520.bit        2026-01-15 02:37:56     4205768
Phroi           2026-01-15 00:19:35     400000
Michiel         2026-01-14 19:31:26     1290000
ckbfansyixiu    2026-01-15 02:35:37     4500000
miteux          2026-01-14 17:42:03     18937556
Methemeticz     2026-01-14 11:41:16     1996228
JPD             2026-01-14 00:15:32     6378375
Balliu          2026-01-13 21:40:28     586906
Byakuya         2026-01-13 17:08:23     2970632
Pires           2026-01-13 11:51:56     38765432
Neon            2026-01-12 17:17:16     100000
phill           2026-01-12 06:40:17     1557056
Knight          2026-01-11 01:12:54     1310305
Logics21        2026-01-15 01:39:07     75892
Ophiuchus       2026-01-14 23:43:25     9920000
------------------------------------------------------------

Fetching on-chain weight for option [Yes] users...

Processing user 1/15: 5520.bit (ID: 29658)
  Querying addresses bound to user 29658...
    Converted web3_public_key (0x64619f4f...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 2,006,666.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 299,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,102.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 200,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 200,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 200,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 200,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 200,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 200,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 200,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 200,000.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 29658 on-chain total weight calculated: 4,205,768.00 CKB
  Metaforo recorded weight: 4205768

Processing user 2/15: Phroi (ID: 46487)
  Querying addresses bound to user 46487...
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 400,000.00 CKB
  User 46487 on-chain total weight calculated: 400,000.00 CKB
  Metaforo recorded weight: 400000

Processing user 3/15: Michiel (ID: 33832)
  Querying addresses bound to user 33832...
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,290,000.00 CKB
  User 33832 on-chain total weight calculated: 1,290,000.00 CKB
  Metaforo recorded weight: 1290000

Processing user 4/15: ckbfansyixiu (ID: 35412)
  Querying addresses bound to user 35412...
    Converted web3_public_key (0xd7948acd...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 35412 on-chain total weight calculated: 4,500,000.00 CKB
  Metaforo recorded weight: 4500000

Processing user 5/15: miteux (ID: 51047)
  Querying addresses bound to user 51047...
    Converted web3_public_key (0xcc3d176d...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 12,939,805.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 5,997,751.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 51047 on-chain total weight calculated: 18,937,556.00 CKB
  Metaforo recorded weight: 18937556

Processing user 6/15: Methemeticz (ID: 51038)
  Querying addresses bound to user 51038...
    Converted web3_public_key (0xd189954d...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 507,966.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,488,262.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 51038 on-chain total weight calculated: 1,996,228.00 CKB
  Metaforo recorded weight: 1996228

Processing user 7/15: JPD (ID: 34076)
  Querying addresses bound to user 34076...
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 6,378,375.00 CKB
  User 34076 on-chain total weight calculated: 6,378,375.00 CKB
  Metaforo recorded weight: 6378375

Processing user 8/15: Balliu (ID: 51026)
  Querying addresses bound to user 51026...
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 586,906.00 CKB
  User 51026 on-chain total weight calculated: 586,906.00 CKB
  Metaforo recorded weight: 586906

Processing user 9/15: Byakuya (ID: 34079)
  Querying addresses bound to user 34079...
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,188,788.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,309,005.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address not found in explorer (404): ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 472,839.00 CKB
  User 34079 on-chain total weight calculated: 2,970,632.00 CKB
  Metaforo recorded weight: 2970632

Processing user 10/15: Pires (ID: 51020)
  Querying addresses bound to user 51020...
    Converted web3_public_key (0xdccf37ba...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 38,765,432.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 51020 on-chain total weight calculated: 38,765,432.00 CKB
  Metaforo recorded weight: 38765432

Processing user 11/15: Neon (ID: 33888)
  Querying addresses bound to user 33888...
    Converted web3_public_key (0xbff03d3d...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 100,000.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 33888 on-chain total weight calculated: 100,000.00 CKB
  Metaforo recorded weight: 100000

Processing user 12/15: phill (ID: 34020)
  Querying addresses bound to user 34020...
    Converted web3_public_key (0xe6b6d31e...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 555,555.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,001,501.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 34020 on-chain total weight calculated: 1,557,056.00 CKB
  Metaforo recorded weight: 1557056

Processing user 13/15: Knight (ID: 33997)
  Querying addresses bound to user 33997...
    Converted web3_public_key (0xf107a1df...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 90,069.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 290,239.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 118,753.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 100,244.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 100,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 150,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 461,000.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 33997 on-chain total weight calculated: 1,310,305.00 CKB
  Metaforo recorded weight: 1310305

Processing user 14/15: Logics21 (ID: 50903)
  Querying addresses bound to user 50903...
    Converted web3_public_key (0x43f56f5c...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 75,892.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 50903 on-chain total weight calculated: 75,892.00 CKB
  Metaforo recorded weight: 75892

Processing user 15/15: Ophiuchus (ID: 50987)
  Querying addresses bound to user 50987...
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address not found in explorer (404): ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address not found in explorer (404): ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 2,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 2,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 5,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 920,000.00 CKB
  User 50987 on-chain total weight calculated: 9,920,000.00 CKB
  Metaforo recorded weight: 9920000


--- Option [Yes] Final Weight Verification Results ---

================================================================================
Nickname: 5520.bit (ID: 29658)
Metaforo recorded weight: 4,205,768.00
Calculated on-chain total weight: 4,205,768.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2rz5408dth46e4fvk748pje9096y0zjtsc9m5nt
    Weight: 2,006,666.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0sr3r3qpcwwug5u9cf4tx2hj9uffs3m5czz5kw0
    Weight: 299,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw5exx3zt8jqhx45vpl9lejsqjy5hs37xg2q5aqu
    Weight: 300,102.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2tmu3g683we72naew0klg0ums32ymavds5hh5h0
    Weight: 200,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgj2cknw544ymdqzaspnf8kk3fmrhy92jga3m78x
    Weight: 200,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq02x39c9va47l8e90xmaf7nqvwsy3eancgk0trj4
    Weight: 200,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdak9quxxlk3qjlfmng6s5vhuyr749rr4s56a95y
    Weight: 200,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2cc2tzhpm64pegam95s2nj59gs2umhc2qsaehrm
    Weight: 200,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0hzzxa37qjsw9x0wr5tt5hyc62fdqu48gsxw9xj
    Weight: 200,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdje822v42jcj4z244ntfne52dhk7m4fhc0j0p4a
    Weight: 200,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw8zafpk2ue0ajumwe79989vjcye594a5gvgsnaa
    Weight: 200,000.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqtyvx057ewukv73t66ksugjwx8p4nsk7dqkw409z
    Weight: 0.00 CKB

================================================================================
Nickname: Phroi (ID: 46487)
Metaforo recorded weight: 400,000.00
Calculated on-chain total weight: 400,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfhnyttkppqhkmdgt24f865mkfvxvphhpqh5pqm8
    Weight: 400,000.00 CKB

================================================================================
Nickname: Michiel (ID: 33832)
Metaforo recorded weight: 1,290,000.00
Calculated on-chain total weight: 1,290,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdzx545uffra6pzwn5schn5cfpns4nnfacvlc0kk
    Weight: 1,290,000.00 CKB

================================================================================
Nickname: ckbfansyixiu (ID: 35412)
Metaforo recorded weight: 4,500,000.00
Calculated on-chain total weight: 4,500,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfd92edamsr7xr5qjplppu3r8ppxdm86csznwssk
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqglz4zvmddz4j0mlk2t78jzh85l2a2dnns2jfmz0
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqflkpj0wp9svsnx38qskardf434nea8z5cyep8c8
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvtzjvwn2uej4ypn2ql92mn6te74cwarrs0rfqnc
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtkvqaq8vyadptalq247q929aq3e6h4kmsaspk6y
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfkmmupfafphz0lduszlha4uhracnrvecshspe03
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0y226497e09cmry7wxgxakqj5xzhjmh8ggpjdvz
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtxzxyjju7vtdpklppn8wgtl45d4sjy5rsm54xur
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtl9t8x22z8q5gex08h77x64rk5ufvdryg6fr6s3
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq04kxv8w4sa09ryn5r8kwppqnzs8fuegrqt7dapy
    Weight: 500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqv7hhqh9rxljz7nj8yd4ewldkadklvepwgsnv9zm
    Weight: 0.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqwhjj9vmq7k5p8tmud8gqtz9695zwyy0rs9jjc7z
    Weight: 0.00 CKB

================================================================================
Nickname: miteux (ID: 51047)
Metaforo recorded weight: 18,937,556.00
Calculated on-chain total weight: 18,937,556.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq24zycexj3jre8w3fsrlz9f0a5lalju5lc54cgnh
    Weight: 12,939,805.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvhujnsgm32cp8txwavprlpgmspptfyafsytus5a
    Weight: 5,997,751.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqwv85tk6flk5aszmh72axxpecny0uzw8pc0njnuh
    Weight: 0.00 CKB

================================================================================
Nickname: Methemeticz (ID: 51038)
Metaforo recorded weight: 1,996,228.00
Calculated on-chain total weight: 1,996,228.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq00g7nu9mwjajgphr9wpzx5zv40dmugg9g7xck29
    Weight: 507,966.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd3svphxkm2pw4aurdz7s8egnejerwhheg42y0x7
    Weight: 1,488,262.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2e62uqqu36nmg7j6jftrwfv046dxxsqeq5h3n4x
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdh4zhh9xljfn73kxpjzv03ytryglx4rnsyg3tyd
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw9x4fal8r5pa53r8043azmqwk7xccqgdg7tcx94
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgyp2t4wt3qtna7hggt7mfp39zzk7vqu9sltw8z8
    Weight: 0.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqw33x25620zghttc2fnr5czmc8xtpwlwrqp2qze5
    Weight: 0.00 CKB

================================================================================
Nickname: JPD (ID: 34076)
Metaforo recorded weight: 6,378,375.00
Calculated on-chain total weight: 6,378,375.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq25qt0htn4gg3mgxzfk7u7r26m8htexrvs0s0c0k
    Weight: 6,378,375.00 CKB

================================================================================
Nickname: Balliu (ID: 51026)
Metaforo recorded weight: 586,906.00
Calculated on-chain total weight: 586,906.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqf8ew8p4ahl37rzdka3gneg3satyd4xgdcenaa4z
    Weight: 586,906.00 CKB

================================================================================
Nickname: Byakuya (ID: 34079)
Metaforo recorded weight: 2,970,632.00
Calculated on-chain total weight: 2,970,632.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvnw3s2htazkfer477f2pyndt3ujwvfsmqejwlvp
    Weight: 1,188,788.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdgmvulkjtwrs2xdwn2ezf6t37hrmea2qq54jz6e
    Weight: 1,309,005.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgsgnwjejkkdz3wxwqf6p99yx287l8largm76z5n
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgp2s9z734rgf9rz8zxkl5l58z8yvaptrsphhs6k
    Weight: 472,839.00 CKB

================================================================================
Nickname: Pires (ID: 51020)
Metaforo recorded weight: 38,765,432.00
Calculated on-chain total weight: 38,765,432.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw62v6ppxujq932epwdys54mpt22mgga5szw257l
    Weight: 38,765,432.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqwueumm44ep79d8jtvz2aefz9sjxyf3zncu5yl0r
    Weight: 0.00 CKB

================================================================================
Nickname: Neon (ID: 33888)
Metaforo recorded weight: 100,000.00
Calculated on-chain total weight: 100,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq22scz5xdghpea53flwa9tnl9v8t5mp4gqn8u5sg
    Weight: 100,000.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqdl7q7nmq72am4qwrj50wtajtu0dl2gzacl2sygv
    Weight: 0.00 CKB

================================================================================
Nickname: phill (ID: 34020)
Metaforo recorded weight: 1,557,056.00
Calculated on-chain total weight: 1,557,056.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0cznt3gq3v8tsrgdrefg6u2umn0zkuuqq99zpad
    Weight: 555,555.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgwspjefmd6pu6qsg3s5rsspuph2tjk6qspdt7jv
    Weight: 1,001,501.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq0xkmf3afm86zlxnk9zpc64efxrewmrxjsh46hmp
    Weight: 0.00 CKB

================================================================================
Nickname: Knight (ID: 33997)
Metaforo recorded weight: 1,310,305.00
Calculated on-chain total weight: 1,310,305.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqf0ngchg0t322jg69f4a9zxqxv9sfjef3sam0683
    Weight: 90,069.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2khj04f0cyyj645948m3cm7sulaumjtdsf8fwcj
    Weight: 290,239.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwyy72u6qpcwkaamyzfjc7t66t46xlssmsc7c400
    Weight: 118,753.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0g23h3dnftayrsnvd5mqmkhuwxgxuwrlgff6umv
    Weight: 100,244.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2smvjx6aeyg4utgzy0a9tftmj5l0fp94gk3epx9
    Weight: 100,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwxm8tnc6cj8zxdltrh3axnhhlzx345tlq5lr7k7
    Weight: 150,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdpz3j7t3u90szme07tkxdvld74kmfqglg0jtxew
    Weight: 461,000.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq03q7salkxr8q39emgmv3npa4kn240e8rctvru0h
    Weight: 0.00 CKB

================================================================================
Nickname: Logics21 (ID: 50903)
Metaforo recorded weight: 75,892.00
Calculated on-chain total weight: 75,892.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvt9mqu693ngdkx3c4s4uasa0esw3lxw5shpkpc5
    Weight: 75,892.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq2r74h4evljhrfh3uz2te0y6uney702n9c4pfyet
    Weight: 0.00 CKB

================================================================================
Nickname: Ophiuchus (ID: 50987)
Metaforo recorded weight: 9,920,000.00
Calculated on-chain total weight: 9,920,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtlxlndctegk2muj9mx9qp7cqtfvwt3rwqv6xtp5
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwxg033vfjllvxx8vr9ff0xwdy9e56r85qx3rsrv
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwdcfnq86g4nvqjx2mp5ltza9xucja70kswha86q
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdu0ct3lc96tp0wsc4pcps2dutsgl223gss977hk
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0gg6ctatqhkwh7helthnymu8xc8uxzr0c8m8x3k
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqf7q426k2jqynrkvfzsdzu2cl8f3wv7wzqj7kqt3
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdj9wxkekr3gp9pu68lmm8kman6eraf6ygm3y0fj
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtf5ycrtqjxnlpjeg339m8awxk84e4pdacuzy9qw
    Weight: 2,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2wnjshh9uvzrcjsz6efqal63473c0hm7s9xa6r9
    Weight: 2,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvvp902m75qjy7mdsnm0vkfeu3jpth05vsdu02uu
    Weight: 5,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2rd8ker2fa7zk0m0hcgmp9az2g8zjp9ssxusl22
    Weight: 920,000.00 CKB
================================================================================

JSON file saved to: /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/Yes_92994150CKB_20260115_121048(UTC+8).json
CSV file saved to: /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/Yes_92994150CKB_20260115_121048(UTC+8).csv

================================================================================
Processing poll option: No (ID: 12552)
================================================================================
Fetching vote list page 1...
Fetching vote list page 2...
All vote data fetched.

--- Option [No] Initial Vote Data ---
Nickname                Vote Time                       Vote Weight
------------------------------------------------------------
Garie           2026-01-13 12:09:29     17220000
wade            2026-01-13 12:20:19     17644454
otioa           2026-01-13 05:12:52     24000000
Juliann         2026-01-13 12:08:19     19933381
MissGloria      2026-01-13 12:01:43     24000000
kaixin          2026-01-15 04:02:36     30000000
22222bit        2026-01-14 01:32:59     22222
KevinW          2026-01-15 00:11:14     20000000
------------------------------------------------------------

Fetching on-chain weight for option [No] users...

Processing user 1/8: Garie (ID: 50181)
  Querying addresses bound to user 50181...
    Converted web3_public_key (0x001863f1...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 4,200,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 4,160,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 4,500,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address not found in explorer (404): ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 4,360,000.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 50181 on-chain total weight calculated: 17,220,000.00 CKB
  Metaforo recorded weight: 17220000

Processing user 2/8: wade (ID: 51009)
  Querying addresses bound to user 51009...
    Converted web3_public_key (0xd510a097...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 8,740,371.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,207,190.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,659,998.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 3,771,999.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 2,264,896.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 51009 on-chain total weight calculated: 17,644,454.00 CKB
  Metaforo recorded weight: 17644454

Processing user 3/8: otioa (ID: 51007)
  Querying addresses bound to user 51007...
    Converted web3_public_key (0xe7173f1d...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 300,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 1,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 51007 on-chain total weight calculated: 24,000,000.00 CKB
  Metaforo recorded weight: 24000000

Processing user 4/8: Juliann (ID: 50196)
  Querying addresses bound to user 50196...
    Converted web3_public_key (0x6d414128...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 9,068,631.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 10,864,750.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 50196 on-chain total weight calculated: 19,933,381.00 CKB
  Metaforo recorded weight: 19933381

Processing user 5/8: MissGloria (ID: 50998)
  Querying addresses bound to user 50998...
    Converted web3_public_key (0xf53f8b91...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 12,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 12,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 50998 on-chain total weight calculated: 24,000,000.00 CKB
  Metaforo recorded weight: 24000000

Processing user 6/8: kaixin (ID: 50960)
  Querying addresses bound to user 50960...
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address not found in explorer (404): ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address not found in explorer (404): ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address not found in explorer (404): ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 0.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 5,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 5,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 5,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 5,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 5,000,000.00 CKB
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 5,000,000.00 CKB
  User 50960 on-chain total weight calculated: 30,000,000.00 CKB
  Metaforo recorded weight: 30000000

Processing user 7/8: 22222bit (ID: 50066)
  Querying addresses bound to user 50066...
    Converted web3_public_key (0xb3bb3dda...) to PW Lock address
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 22,222.00 CKB
    Calculating on-chain weight for address ckb1qzl58smqy32...
    Address not found in explorer (404): ckb1qzl58smqy32...
    Address ckb1qzl58smqy32... weight: 0.00 CKB
  User 50066 on-chain total weight calculated: 22,222.00 CKB
  Metaforo recorded weight: 22222

Processing user 8/8: KevinW (ID: 50133)
  Querying addresses bound to user 50133...
    Calculating on-chain weight for address ckb1qzda0cr08m8...
    Address ckb1qzda0cr08m8... weight: 20,000,000.00 CKB
  User 50133 on-chain total weight calculated: 20,000,000.00 CKB
  Metaforo recorded weight: 20000000


--- Option [No] Final Weight Verification Results ---

================================================================================
Nickname: Garie (ID: 50181)
Metaforo recorded weight: 17,220,000.00
Calculated on-chain total weight: 17,220,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2nlqmnve6vzzqwmc9dnjvynd9e09sse2grwn7sw
    Weight: 4,200,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgxkjdncvqgw8hfqt78q8sewfj4asydsgceadv0k
    Weight: 4,160,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd28grvhrgvsnn3fqec8f7ap6fzqc74gsq6sdwcq
    Weight: 4,500,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0tlc8uq7umetq0nq08aqxtgwrp22xa0jglzfasu
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdupej27yxwepx2peph9g2zdmwwq778slscy3lm5
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd7g36dl9akqqeekrcp7auh33qt23cjk0swhpkjv
    Weight: 4,360,000.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqgqrp3lrrkcggt2x5rwspl67qewwg5g2hcpvtygs
    Weight: 0.00 CKB

================================================================================
Nickname: wade (ID: 51009)
Metaforo recorded weight: 17,644,454.00
Calculated on-chain total weight: 17,644,454.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0cffqnutceepn6txjc5u26zhvwn40e9qsxyyzg0
    Weight: 8,740,371.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdk33ez8y6agzc72yxdgagffjquak5sx2qsy42nx
    Weight: 1,207,190.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq25pyglgsqpqukzcc0gptrrldqmhhrwn9qnjgyl3
    Weight: 1,659,998.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvmnqkv0zmlkev6nhu8uljh69lagj7egpgfm3x6g
    Weight: 3,771,999.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2d9kpx5q8jtj72ahwl5qy6nsv7x9lqztclm6eus
    Weight: 2,264,896.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqw4zzsfwry9624uz2dmmv86c5lvlwm570ccj2stp
    Weight: 0.00 CKB

================================================================================
Nickname: otioa (ID: 51007)
Metaforo recorded weight: 24,000,000.00
Calculated on-chain total weight: 24,000,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2e33v7azym5az5ta950afg2t72q56mfxcz09g5v
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtq29u0r2nefacwk2frzmng8mtkuvc2lpgze2v2v
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwrreprsqre5tmhf00x0usq6dhsq68gfhcff90t4
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqv527lh24sgfs55nec348arwfzjc54jsnsc2an25
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd5grymm3elduwhvaagplmdu9hcaj2p55ggv8udf
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq259lyvym09exvxvds6s4sr280p7970zxqca3mqt
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwum7mftus46haevgkemhf7q5vheumh90c5akdsz
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq23xwa02ejjvdjdyxd5avfm3ee02wyrz7qwsku9h
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwawpcz3h8x55gc3x30wx3959sr8qtynssclqw55
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwfr288gq236dtr9mc869dwr0ck6py38ncyrdlj5
    Weight: 300,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2tq9ayfx6pccndrgrpdcl80upgky5tjxcyp74c5
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqt5p4fv4lgljp5vxppsffng5ykpa7evw6s9dnh9r
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfw4ps22xe0zjnx2qgnw05h6ghwe0gg7lq2sddjh
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgt8vfg4zyk02vhmeum9d0kxl6qek9y2rqyuwmlh
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfwnnlkxkgw75qx0ruknmrgr8s0z35wk6swuj3c6
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgtund9lhsaawts0pvtm8z9qlv893q7nhgktw553
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqg37f4wmyvxrlslcymmvs5z3j8zufw6hagq9stuv
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfdujan34ct6hq8hl9svh3wk3mkkqchtrs0nszvf
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtmfnwesx22zesrwxdf2hss937vf2xnp4gjsrcvg
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdhwgfgp996r7qjgzcy9tpcvse6nezjdvg5fp96l
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfs0gz0f7n3k24rqldpwanve6nkldj7vgsh0w5dp
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdrut0tl7lrt0yfnxqde3rrt96v3v3skdqfnzqpj
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqv3ma3kyl4sh6zxk66w2zpcth4gmp8eryg65um3s
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd9h4nwwzpdmtexud4t65xm480vmd6fxwgvjua0e
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2ts2v8jjuarumz0yvvm7en6kp4l4ruhhcm400p9
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwjz5rp9ju470n3errhgeflnvthlxugk9ssyg77c
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw46l3s96tg0xurnx7wmskcvnnav4uh4xqelphgg
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2hdz5uucs6ghqps0sxseyt53qy74xvgvgy5q0jj
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvgqjzgk0xy6yqam2hgrv5mheepuhdza0g7j3clf
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqga60dezpavnufsrvasl8zz2g5uewzxhggy4dpqh
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0qmg56wa7gmtcqex2a7mj2mv4pd4262wsfujk73
    Weight: 1,000,000.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq08zul36l6a4gp23lm8azzqctc88xmra0scv0xec
    Weight: 0.00 CKB

================================================================================
Nickname: Juliann (ID: 50196)
Metaforo recorded weight: 19,933,381.00
Calculated on-chain total weight: 19,933,381.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwr985zpl8lw9k6eqaaf526qweclgh5z0q8k3ghg
    Weight: 9,068,631.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvms4223sumhv3ex7ucjk43mxec2453j0c9gdygh
    Weight: 10,864,750.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqtdg9qj32yqphe42a3700rf9le0lalr8pqlm5ymh
    Weight: 0.00 CKB

================================================================================
Nickname: MissGloria (ID: 50998)
Metaforo recorded weight: 24,000,000.00
Calculated on-chain total weight: 24,000,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq084vxx0euhc36tcnsyjf4ny590v94rjpsv8pttm
    Weight: 12,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwgd9av2fhmndvvqklw7f7v6vmn4faanvcn879gl
    Weight: 12,000,000.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq04879ez40q29z9f7xf3gz5rfh2uh24jhsuj5nra
    Weight: 0.00 CKB

================================================================================
Nickname: kaixin (ID: 50960)
Metaforo recorded weight: 30,000,000.00
Calculated on-chain total weight: 30,000,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfg779ryncmyvd0sf8ud2g23s4l0m6u95gypr0y6
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdh9pw6ktcf8tvq0hedrgpmjmhumj2pscghf8qm3
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdnetnkt45q7jshvfzlgxr0an6mvvjmwtgz9lxnz
    Weight: 0.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw208dq57wm9u8kyqvgekcz9nlj97lntrqkf4rwn
    Weight: 5,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqg9tfnasncvu2sfgu55av7e60nv48260vclne5sz
    Weight: 5,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2fzjdqq3tn2xyw2jurtennwks7uztpfeqa5qjyc
    Weight: 5,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqv26thzjwl09selm8mscgdx5gq504yeydqtqj3jr
    Weight: 5,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvactr7302q7d2php7v7dfjuhzqtmhxkvg637g7r
    Weight: 5,000,000.00 CKB
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2zakxet2tryz6mwhadqwc8v8czmwrn5pgjq2h2u
    Weight: 5,000,000.00 CKB

================================================================================
Nickname: 22222bit (ID: 50066)
Metaforo recorded weight: 22,222.00
Calculated on-chain total weight: 22,222.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfmmaugarkeg9f2jwe69455024d90ytc0g2h7ngu
    Weight: 22,222.00 CKB
  - Address: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqdnhv7a4lnu9csdkr5yvukqdp3ufysrzuqye97ds
    Weight: 0.00 CKB

================================================================================
Nickname: KevinW (ID: 50133)
Metaforo recorded weight: 20,000,000.00
Calculated on-chain total weight: 20,000,000.00
----------------------------------------
Bound addresses and their weights:
  - Address: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvnyvfytcls75sqf3hjj5wd9pu5zujhf9cfnlx49
    Weight: 20,000,000.00 CKB
================================================================================

JSON file saved to: /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/No_152820057CKB_20260115_121048(UTC+8).json
CSV file saved to: /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/No_152820057CKB_20260115_121048(UTC+8).csv

================================================================================
All poll options processed!
Generated 4 files:
  - /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/Yes_92994150CKB_20260115_121048(UTC+8).json
  - /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/Yes_92994150CKB_20260115_121048(UTC+8).csv
  - /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/No_152820057CKB_20260115_121048(UTC+8).json
  - /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/No_152820057CKB_20260115_121048(UTC+8).csv

aabbcc@192 ckb-dao-watchdog % 
```

## License

MIT License
