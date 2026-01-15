# DAO v1.0 (Metaforo) Watchdog

[English](./README.md)

CKB Community Fund DAO v1.0 在 Metaforo 平台上的投票审计工具。

## 概述

本工具通过比对 Metaforo 平台记录的权重与链上实际的 Nervos DAO 存款，验证 [CKB Community Fund DAO](https://dao.ckb.community) 的投票权重。

## 环境要求

- Python 3.11+
- 依赖包：

```bash
pip install requests pyckb
```

## 使用方法

### 方式一：使用 Metaforo URL（推荐）

直接提供投票页面 URL：

```bash
python metaforo_watchdog_cn.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
```

工具会自动：
1. 从 URL 中解析帖子 ID
2. 获取所有投票选项（如 Yes、No）
3. 处理每个选项并生成报告

### 方式二：使用 Option ID（高级）

如果你知道具体的选项 ID：

```bash
python metaforo_watchdog_cn.py 12551
```

### Docker 使用方法

你也可以使用 Docker 运行工具，无需在本地安装 Python 依赖。

1. **拉取 Docker 镜像：**

   ```bash
   docker pull ghcr.io/ckbfansdao/ckb-dao-watchdog/dao-v1-0:main
   ```

2. **运行工具：**

   ```bash
   docker run -it --rm -v $(pwd)/vote_result:/app/vote_result ghcr.io/ckbfansdao/ckb-dao-watchdog/dao-v1-0:main metaforo_watchdog_cn.py <url_or_id>
   ```

## 输出文件

对于每个投票选项，工具会生成：

```
vote_result/{thread_id}/{选项}_{权重}CKB_{时间戳}.json
vote_result/{thread_id}/{选项}_{权重}CKB_{时间戳}.csv
```

示例：

```
vote_result/66568/Yes_63660826CKB_20260114_220441(UTC+8).json
vote_result/66568/Yes_63660826CKB_20260114_220441(UTC+8).csv
vote_result/66568/No_152820057CKB_20260114_220441(UTC+8).json
vote_result/66568/No_152820057CKB_20260114_220441(UTC+8).csv
```

## 输出字段说明

| 字段 | 说明 |
|------|------|
| `nickname` | 用户在 Metaforo 上的显示名称 |
| `userid` | 用户的 Metaforo ID |
| `voted_at` | 投票时间 (UTC+0) |
| `total weight(metaforo)` | Metaforo 平台记录的权重 |
| `total weight(on chain, floored)` | 根据链上 DAO 存款计算的权重 |
| `⚠️need_review` | 如果权重不匹配则为 `true`（需要人工复核） |
| `address` | CKB 地址（Neuron 或 PW Lock） |
| `address weight(floored)` | 该地址的 DAO 存款权重 |
| `explorer_url` | 在 CKB Explorer 上查看地址的链接 |

## 权重计算方式

1. **Neuron 地址**：从 Neuron 钱包直接绑定的 CKB 地址
2. **MetaMask/PW Lock**：使用 PW Lock 脚本将以太坊地址转换为 CKB 地址
3. **DAO 存款**：仅计算 `nervos_dao_deposit` 类型的 Cell
4. **单位转换**：Shannon → CKB（÷ 10^8），然后向下取整

## 验证逻辑

当以下条件成立时，工具会标记 `need_review = true`：
```
floor(total_weight_metaforo) ≠ floor(total_weight_on_chain)
```

这可能表示：
- 最近的存款/取款尚未反映
- 地址绑定问题
- 需要调查的潜在差异

## 使用的 API 接口

- **Metaforo API**：`https://dao.ckb.community/api`
  - `GET /get_thread/{thread_id}` - 获取投票选项
  - `POST /poll/list` - 获取某选项的投票者
  - `GET /profile/{user_id}/neurontest` - 获取用户绑定的地址

- **Nervos Explorer API**：`https://mainnet-api.explorer.nervos.org/api/v1`
  - `GET /address_live_cells/{address}` - 获取地址的活跃 Cell

## 常见问题

### 网络错误
工具包含重试逻辑和请求频率限制（请求间隔 0.5 秒）。如果遇到持续的网络错误，请稍后重试。

### 无投票数据
如果某个投票选项没有投票，工具会跳过它并继续处理其他选项。

### 权重不匹配
`need_review = true` 标记不一定表示存在欺诈。常见原因：
- 用户在投票后进行了存款/取款
- 地址未正确绑定

## 输出示例

```bash
aabbcc@192 ckb-dao-watchdog % /usr/local/bin/python3 /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/metaforo_watchdog_cn.py
用法: python metaforo.dao.zh.py <metaforo_url>
示例: python metaforo.dao.zh.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
aabbcc@192 ckb-dao-watchdog % /usr/local/bin/python3 /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/metaforo_watchdog_cn.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
从 URL 解析得到 thread_id: 66568
正在获取帖子 66568 的投票选项信息...
找到 2 个投票选项:
  - Yes (ID: 12551, 投票数: 15, 权重: 92994150)
  - No (ID: 12552, 投票数: 8, 权重: 152820057)

开始处理所有 2 个投票选项...


================================================================================
开始处理投票选项: Yes (ID: 12551)
================================================================================
正在获取投票列表第 1 页...
正在获取投票列表第 2 页...
正在获取投票列表第 3 页...
已获取所有投票数据。

--- 选项 [Yes] 初始投票数据 ---
昵称            投票时间                        投票权重
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

开始获取选项 [Yes] 每个用户的链上权重...

正在处理第 1/15 个用户: 5520.bit (ID: 29658)
  正在查询用户 29658 绑定的地址...
    已通过 web3_public_key (0x64619f4f...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 2,006,666.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 299,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,102.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 200,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 200,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 200,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 200,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 200,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 200,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 200,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 200,000.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 29658 的链上总权重计算完成: 4,205,768.00 CKB
  Metaforo 记录的权重: 4205768

正在处理第 2/15 个用户: Phroi (ID: 46487)
  正在查询用户 46487 绑定的地址...
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 400,000.00 CKB
  用户 46487 的链上总权重计算完成: 400,000.00 CKB
  Metaforo 记录的权重: 400000

正在处理第 3/15 个用户: Michiel (ID: 33832)
  正在查询用户 33832 绑定的地址...
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,290,000.00 CKB
  用户 33832 的链上总权重计算完成: 1,290,000.00 CKB
  Metaforo 记录的权重: 1290000

正在处理第 4/15 个用户: ckbfansyixiu (ID: 35412)
  正在查询用户 35412 绑定的地址...
    已通过 web3_public_key (0xd7948acd...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 35412 的链上总权重计算完成: 4,500,000.00 CKB
  Metaforo 记录的权重: 4500000

正在处理第 5/15 个用户: miteux (ID: 51047)
  正在查询用户 51047 绑定的地址...
    已通过 web3_public_key (0xcc3d176d...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 12,939,805.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 5,997,751.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 51047 的链上总权重计算完成: 18,937,556.00 CKB
  Metaforo 记录的权重: 18937556

正在处理第 6/15 个用户: Methemeticz (ID: 51038)
  正在查询用户 51038 绑定的地址...
    已通过 web3_public_key (0xd189954d...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 507,966.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,488,262.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 51038 的链上总权重计算完成: 1,996,228.00 CKB
  Metaforo 记录的权重: 1996228

正在处理第 7/15 个用户: JPD (ID: 34076)
  正在查询用户 34076 绑定的地址...
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 6,378,375.00 CKB
  用户 34076 的链上总权重计算完成: 6,378,375.00 CKB
  Metaforo 记录的权重: 6378375

正在处理第 8/15 个用户: Balliu (ID: 51026)
  正在查询用户 51026 绑定的地址...
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 586,906.00 CKB
  用户 51026 的链上总权重计算完成: 586,906.00 CKB
  Metaforo 记录的权重: 586906

正在处理第 9/15 个用户: Byakuya (ID: 34079)
  正在查询用户 34079 绑定的地址...
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,188,788.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,309,005.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzda0cr08m8...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 472,839.00 CKB
  用户 34079 的链上总权重计算完成: 2,970,632.00 CKB
  Metaforo 记录的权重: 2970632

正在处理第 10/15 个用户: Pires (ID: 51020)
  正在查询用户 51020 绑定的地址...
    已通过 web3_public_key (0xdccf37ba...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 38,765,432.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 51020 的链上总权重计算完成: 38,765,432.00 CKB
  Metaforo 记录的权重: 38765432

正在处理第 11/15 个用户: Neon (ID: 33888)
  正在查询用户 33888 绑定的地址...
    已通过 web3_public_key (0xbff03d3d...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 100,000.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 33888 的链上总权重计算完成: 100,000.00 CKB
  Metaforo 记录的权重: 100000

正在处理第 12/15 个用户: phill (ID: 34020)
  正在查询用户 34020 绑定的地址...
    已通过 web3_public_key (0xe6b6d31e...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 555,555.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,001,501.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 34020 的链上总权重计算完成: 1,557,056.00 CKB
  Metaforo 记录的权重: 1557056

正在处理第 13/15 个用户: Knight (ID: 33997)
  正在查询用户 33997 绑定的地址...
    已通过 web3_public_key (0xf107a1df...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 90,069.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 290,239.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 118,753.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 100,244.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 100,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 150,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 461,000.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 33997 的链上总权重计算完成: 1,310,305.00 CKB
  Metaforo 记录的权重: 1310305

正在处理第 14/15 个用户: Logics21 (ID: 50903)
  正在查询用户 50903 绑定的地址...
    已通过 web3_public_key (0x43f56f5c...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 75,892.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 50903 的链上总权重计算完成: 75,892.00 CKB
  Metaforo 记录的权重: 75892

正在处理第 15/15 个用户: Ophiuchus (ID: 50987)
  正在查询用户 50987 绑定的地址...
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzda0cr08m8...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzda0cr08m8...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 2,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 2,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 5,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 920,000.00 CKB
  用户 50987 的链上总权重计算完成: 9,920,000.00 CKB
  Metaforo 记录的权重: 9920000


--- 选项 [Yes] 最终权重验证结果 ---

================================================================================
昵称: 5520.bit (ID: 29658)
Metaforo 记录权重: 4,205,768.00
计算出的链上总权重: 4,205,768.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2rz5408dth46e4fvk748pje9096y0zjtsc9m5nt
    权重: 2,006,666.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0sr3r3qpcwwug5u9cf4tx2hj9uffs3m5czz5kw0
    权重: 299,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw5exx3zt8jqhx45vpl9lejsqjy5hs37xg2q5aqu
    权重: 300,102.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2tmu3g683we72naew0klg0ums32ymavds5hh5h0
    权重: 200,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgj2cknw544ymdqzaspnf8kk3fmrhy92jga3m78x
    权重: 200,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq02x39c9va47l8e90xmaf7nqvwsy3eancgk0trj4
    权重: 200,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdak9quxxlk3qjlfmng6s5vhuyr749rr4s56a95y
    权重: 200,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2cc2tzhpm64pegam95s2nj59gs2umhc2qsaehrm
    权重: 200,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0hzzxa37qjsw9x0wr5tt5hyc62fdqu48gsxw9xj
    权重: 200,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdje822v42jcj4z244ntfne52dhk7m4fhc0j0p4a
    权重: 200,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw8zafpk2ue0ajumwe79989vjcye594a5gvgsnaa
    权重: 200,000.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqtyvx057ewukv73t66ksugjwx8p4nsk7dqkw409z
    权重: 0.00 CKB

================================================================================
昵称: Phroi (ID: 46487)
Metaforo 记录权重: 400,000.00
计算出的链上总权重: 400,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfhnyttkppqhkmdgt24f865mkfvxvphhpqh5pqm8
    权重: 400,000.00 CKB

================================================================================
昵称: Michiel (ID: 33832)
Metaforo 记录权重: 1,290,000.00
计算出的链上总权重: 1,290,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdzx545uffra6pzwn5schn5cfpns4nnfacvlc0kk
    权重: 1,290,000.00 CKB

================================================================================
昵称: ckbfansyixiu (ID: 35412)
Metaforo 记录权重: 4,500,000.00
计算出的链上总权重: 4,500,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfd92edamsr7xr5qjplppu3r8ppxdm86csznwssk
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqglz4zvmddz4j0mlk2t78jzh85l2a2dnns2jfmz0
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqflkpj0wp9svsnx38qskardf434nea8z5cyep8c8
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvtzjvwn2uej4ypn2ql92mn6te74cwarrs0rfqnc
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtkvqaq8vyadptalq247q929aq3e6h4kmsaspk6y
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfkmmupfafphz0lduszlha4uhracnrvecshspe03
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0y226497e09cmry7wxgxakqj5xzhjmh8ggpjdvz
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtxzxyjju7vtdpklppn8wgtl45d4sjy5rsm54xur
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtl9t8x22z8q5gex08h77x64rk5ufvdryg6fr6s3
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq04kxv8w4sa09ryn5r8kwppqnzs8fuegrqt7dapy
    权重: 500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqv7hhqh9rxljz7nj8yd4ewldkadklvepwgsnv9zm
    权重: 0.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqwhjj9vmq7k5p8tmud8gqtz9695zwyy0rs9jjc7z
    权重: 0.00 CKB

================================================================================
昵称: miteux (ID: 51047)
Metaforo 记录权重: 18,937,556.00
计算出的链上总权重: 18,937,556.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq24zycexj3jre8w3fsrlz9f0a5lalju5lc54cgnh
    权重: 12,939,805.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvhujnsgm32cp8txwavprlpgmspptfyafsytus5a
    权重: 5,997,751.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqwv85tk6flk5aszmh72axxpecny0uzw8pc0njnuh
    权重: 0.00 CKB

================================================================================
昵称: Methemeticz (ID: 51038)
Metaforo 记录权重: 1,996,228.00
计算出的链上总权重: 1,996,228.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq00g7nu9mwjajgphr9wpzx5zv40dmugg9g7xck29
    权重: 507,966.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd3svphxkm2pw4aurdz7s8egnejerwhheg42y0x7
    权重: 1,488,262.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2e62uqqu36nmg7j6jftrwfv046dxxsqeq5h3n4x
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdh4zhh9xljfn73kxpjzv03ytryglx4rnsyg3tyd
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw9x4fal8r5pa53r8043azmqwk7xccqgdg7tcx94
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgyp2t4wt3qtna7hggt7mfp39zzk7vqu9sltw8z8
    权重: 0.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqw33x25620zghttc2fnr5czmc8xtpwlwrqp2qze5
    权重: 0.00 CKB

================================================================================
昵称: JPD (ID: 34076)
Metaforo 记录权重: 6,378,375.00
计算出的链上总权重: 6,378,375.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq25qt0htn4gg3mgxzfk7u7r26m8htexrvs0s0c0k
    权重: 6,378,375.00 CKB

================================================================================
昵称: Balliu (ID: 51026)
Metaforo 记录权重: 586,906.00
计算出的链上总权重: 586,906.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqf8ew8p4ahl37rzdka3gneg3satyd4xgdcenaa4z
    权重: 586,906.00 CKB

================================================================================
昵称: Byakuya (ID: 34079)
Metaforo 记录权重: 2,970,632.00
计算出的链上总权重: 2,970,632.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvnw3s2htazkfer477f2pyndt3ujwvfsmqejwlvp
    权重: 1,188,788.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdgmvulkjtwrs2xdwn2ezf6t37hrmea2qq54jz6e
    权重: 1,309,005.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgsgnwjejkkdz3wxwqf6p99yx287l8largm76z5n
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgp2s9z734rgf9rz8zxkl5l58z8yvaptrsphhs6k
    权重: 472,839.00 CKB

================================================================================
昵称: Pires (ID: 51020)
Metaforo 记录权重: 38,765,432.00
计算出的链上总权重: 38,765,432.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw62v6ppxujq932epwdys54mpt22mgga5szw257l
    权重: 38,765,432.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqwueumm44ep79d8jtvz2aefz9sjxyf3zncu5yl0r
    权重: 0.00 CKB

================================================================================
昵称: Neon (ID: 33888)
Metaforo 记录权重: 100,000.00
计算出的链上总权重: 100,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq22scz5xdghpea53flwa9tnl9v8t5mp4gqn8u5sg
    权重: 100,000.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqdl7q7nmq72am4qwrj50wtajtu0dl2gzacl2sygv
    权重: 0.00 CKB

================================================================================
昵称: phill (ID: 34020)
Metaforo 记录权重: 1,557,056.00
计算出的链上总权重: 1,557,056.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0cznt3gq3v8tsrgdrefg6u2umn0zkuuqq99zpad
    权重: 555,555.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgwspjefmd6pu6qsg3s5rsspuph2tjk6qspdt7jv
    权重: 1,001,501.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq0xkmf3afm86zlxnk9zpc64efxrewmrxjsh46hmp
    权重: 0.00 CKB

================================================================================
昵称: Knight (ID: 33997)
Metaforo 记录权重: 1,310,305.00
计算出的链上总权重: 1,310,305.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqf0ngchg0t322jg69f4a9zxqxv9sfjef3sam0683
    权重: 90,069.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2khj04f0cyyj645948m3cm7sulaumjtdsf8fwcj
    权重: 290,239.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwyy72u6qpcwkaamyzfjc7t66t46xlssmsc7c400
    权重: 118,753.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0g23h3dnftayrsnvd5mqmkhuwxgxuwrlgff6umv
    权重: 100,244.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2smvjx6aeyg4utgzy0a9tftmj5l0fp94gk3epx9
    权重: 100,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwxm8tnc6cj8zxdltrh3axnhhlzx345tlq5lr7k7
    权重: 150,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdpz3j7t3u90szme07tkxdvld74kmfqglg0jtxew
    权重: 461,000.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq03q7salkxr8q39emgmv3npa4kn240e8rctvru0h
    权重: 0.00 CKB

================================================================================
昵称: Logics21 (ID: 50903)
Metaforo 记录权重: 75,892.00
计算出的链上总权重: 75,892.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvt9mqu693ngdkx3c4s4uasa0esw3lxw5shpkpc5
    权重: 75,892.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq2r74h4evljhrfh3uz2te0y6uney702n9c4pfyet
    权重: 0.00 CKB

================================================================================
昵称: Ophiuchus (ID: 50987)
Metaforo 记录权重: 9,920,000.00
计算出的链上总权重: 9,920,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtlxlndctegk2muj9mx9qp7cqtfvwt3rwqv6xtp5
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwxg033vfjllvxx8vr9ff0xwdy9e56r85qx3rsrv
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwdcfnq86g4nvqjx2mp5ltza9xucja70kswha86q
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdu0ct3lc96tp0wsc4pcps2dutsgl223gss977hk
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0gg6ctatqhkwh7helthnymu8xc8uxzr0c8m8x3k
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqf7q426k2jqynrkvfzsdzu2cl8f3wv7wzqj7kqt3
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdj9wxkekr3gp9pu68lmm8kman6eraf6ygm3y0fj
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtf5ycrtqjxnlpjeg339m8awxk84e4pdacuzy9qw
    权重: 2,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2wnjshh9uvzrcjsz6efqal63473c0hm7s9xa6r9
    权重: 2,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvvp902m75qjy7mdsnm0vkfeu3jpth05vsdu02uu
    权重: 5,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2rd8ker2fa7zk0m0hcgmp9az2g8zjp9ssxusl22
    权重: 920,000.00 CKB
================================================================================

JSON 文件已保存至: /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/Yes_92994150CKB_20260115_120459(UTC+8).json
CSV 文件已保存至: /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/Yes_92994150CKB_20260115_120459(UTC+8).csv

================================================================================
开始处理投票选项: No (ID: 12552)
================================================================================
正在获取投票列表第 1 页...
正在获取投票列表第 2 页...
已获取所有投票数据。

--- 选项 [No] 初始投票数据 ---
昵称            投票时间                        投票权重
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

开始获取选项 [No] 每个用户的链上权重...

正在处理第 1/8 个用户: Garie (ID: 50181)
  正在查询用户 50181 绑定的地址...
    已通过 web3_public_key (0x001863f1...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 4,200,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 4,160,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 4,500,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzda0cr08m8...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 4,360,000.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 50181 的链上总权重计算完成: 17,220,000.00 CKB
  Metaforo 记录的权重: 17220000

正在处理第 2/8 个用户: wade (ID: 51009)
  正在查询用户 51009 绑定的地址...
    已通过 web3_public_key (0xd510a097...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 8,740,371.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,207,190.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,659,998.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 3,771,999.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 2,264,896.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 51009 的链上总权重计算完成: 17,644,454.00 CKB
  Metaforo 记录的权重: 17644454

正在处理第 3/8 个用户: otioa (ID: 51007)
  正在查询用户 51007 绑定的地址...
    已通过 web3_public_key (0xe7173f1d...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 300,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 1,000,000.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 51007 的链上总权重计算完成: 24,000,000.00 CKB
  Metaforo 记录的权重: 24000000

正在处理第 4/8 个用户: Juliann (ID: 50196)
  正在查询用户 50196 绑定的地址...
    已通过 web3_public_key (0x6d414128...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 9,068,631.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 10,864,750.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 50196 的链上总权重计算完成: 19,933,381.00 CKB
  Metaforo 记录的权重: 19933381

正在处理第 5/8 个用户: MissGloria (ID: 50998)
  正在查询用户 50998 绑定的地址...
    已通过 web3_public_key (0xf53f8b91...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 12,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 12,000,000.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 50998 的链上总权重计算完成: 24,000,000.00 CKB
  Metaforo 记录的权重: 24000000

正在处理第 6/8 个用户: kaixin (ID: 50960)
  正在查询用户 50960 绑定的地址...
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzda0cr08m8...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzda0cr08m8...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzda0cr08m8...
    地址 ckb1qzda0cr08m8... 的权重为: 0.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 5,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 5,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 5,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 5,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 5,000,000.00 CKB
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 5,000,000.00 CKB
  用户 50960 的链上总权重计算完成: 30,000,000.00 CKB
  Metaforo 记录的权重: 30000000

正在处理第 7/8 个用户: 22222bit (ID: 50066)
  正在查询用户 50066 绑定的地址...
    已通过 web3_public_key (0xb3bb3dda...) 转换得到 PW Lock 地址
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 22,222.00 CKB
    正在计算地址 ckb1qzl58smqy32... 的链上权重...
    地址在 explorer 中未找到 (404): ckb1qzl58smqy32...
    地址 ckb1qzl58smqy32... 的权重为: 0.00 CKB
  用户 50066 的链上总权重计算完成: 22,222.00 CKB
  Metaforo 记录的权重: 22222

正在处理第 8/8 个用户: KevinW (ID: 50133)
  正在查询用户 50133 绑定的地址...
    正在计算地址 ckb1qzda0cr08m8... 的链上权重...
    地址 ckb1qzda0cr08m8... 的权重为: 20,000,000.00 CKB
  用户 50133 的链上总权重计算完成: 20,000,000.00 CKB
  Metaforo 记录的权重: 20000000


--- 选项 [No] 最终权重验证结果 ---

================================================================================
昵称: Garie (ID: 50181)
Metaforo 记录权重: 17,220,000.00
计算出的链上总权重: 17,220,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2nlqmnve6vzzqwmc9dnjvynd9e09sse2grwn7sw
    权重: 4,200,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgxkjdncvqgw8hfqt78q8sewfj4asydsgceadv0k
    权重: 4,160,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd28grvhrgvsnn3fqec8f7ap6fzqc74gsq6sdwcq
    权重: 4,500,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0tlc8uq7umetq0nq08aqxtgwrp22xa0jglzfasu
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdupej27yxwepx2peph9g2zdmwwq778slscy3lm5
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd7g36dl9akqqeekrcp7auh33qt23cjk0swhpkjv
    权重: 4,360,000.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqgqrp3lrrkcggt2x5rwspl67qewwg5g2hcpvtygs
    权重: 0.00 CKB

================================================================================
昵称: wade (ID: 51009)
Metaforo 记录权重: 17,644,454.00
计算出的链上总权重: 17,644,454.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0cffqnutceepn6txjc5u26zhvwn40e9qsxyyzg0
    权重: 8,740,371.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdk33ez8y6agzc72yxdgagffjquak5sx2qsy42nx
    权重: 1,207,190.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq25pyglgsqpqukzcc0gptrrldqmhhrwn9qnjgyl3
    权重: 1,659,998.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvmnqkv0zmlkev6nhu8uljh69lagj7egpgfm3x6g
    权重: 3,771,999.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2d9kpx5q8jtj72ahwl5qy6nsv7x9lqztclm6eus
    权重: 2,264,896.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqw4zzsfwry9624uz2dmmv86c5lvlwm570ccj2stp
    权重: 0.00 CKB

================================================================================
昵称: otioa (ID: 51007)
Metaforo 记录权重: 24,000,000.00
计算出的链上总权重: 24,000,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2e33v7azym5az5ta950afg2t72q56mfxcz09g5v
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtq29u0r2nefacwk2frzmng8mtkuvc2lpgze2v2v
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwrreprsqre5tmhf00x0usq6dhsq68gfhcff90t4
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqv527lh24sgfs55nec348arwfzjc54jsnsc2an25
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd5grymm3elduwhvaagplmdu9hcaj2p55ggv8udf
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq259lyvym09exvxvds6s4sr280p7970zxqca3mqt
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwum7mftus46haevgkemhf7q5vheumh90c5akdsz
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq23xwa02ejjvdjdyxd5avfm3ee02wyrz7qwsku9h
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwawpcz3h8x55gc3x30wx3959sr8qtynssclqw55
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwfr288gq236dtr9mc869dwr0ck6py38ncyrdlj5
    权重: 300,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2tq9ayfx6pccndrgrpdcl80upgky5tjxcyp74c5
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqt5p4fv4lgljp5vxppsffng5ykpa7evw6s9dnh9r
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfw4ps22xe0zjnx2qgnw05h6ghwe0gg7lq2sddjh
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgt8vfg4zyk02vhmeum9d0kxl6qek9y2rqyuwmlh
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfwnnlkxkgw75qx0ruknmrgr8s0z35wk6swuj3c6
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqgtund9lhsaawts0pvtm8z9qlv893q7nhgktw553
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqg37f4wmyvxrlslcymmvs5z3j8zufw6hagq9stuv
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfdujan34ct6hq8hl9svh3wk3mkkqchtrs0nszvf
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqtmfnwesx22zesrwxdf2hss937vf2xnp4gjsrcvg
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdhwgfgp996r7qjgzcy9tpcvse6nezjdvg5fp96l
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfs0gz0f7n3k24rqldpwanve6nkldj7vgsh0w5dp
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdrut0tl7lrt0yfnxqde3rrt96v3v3skdqfnzqpj
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqv3ma3kyl4sh6zxk66w2zpcth4gmp8eryg65um3s
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqd9h4nwwzpdmtexud4t65xm480vmd6fxwgvjua0e
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2ts2v8jjuarumz0yvvm7en6kp4l4ruhhcm400p9
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwjz5rp9ju470n3errhgeflnvthlxugk9ssyg77c
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw46l3s96tg0xurnx7wmskcvnnav4uh4xqelphgg
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2hdz5uucs6ghqps0sxseyt53qy74xvgvgy5q0jj
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvgqjzgk0xy6yqam2hgrv5mheepuhdza0g7j3clf
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqga60dezpavnufsrvasl8zz2g5uewzxhggy4dpqh
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq0qmg56wa7gmtcqex2a7mj2mv4pd4262wsfujk73
    权重: 1,000,000.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq08zul36l6a4gp23lm8azzqctc88xmra0scv0xec
    权重: 0.00 CKB

================================================================================
昵称: Juliann (ID: 50196)
Metaforo 记录权重: 19,933,381.00
计算出的链上总权重: 19,933,381.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwr985zpl8lw9k6eqaaf526qweclgh5z0q8k3ghg
    权重: 9,068,631.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvms4223sumhv3ex7ucjk43mxec2453j0c9gdygh
    权重: 10,864,750.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqtdg9qj32yqphe42a3700rf9le0lalr8pqlm5ymh
    权重: 0.00 CKB

================================================================================
昵称: MissGloria (ID: 50998)
Metaforo 记录权重: 24,000,000.00
计算出的链上总权重: 24,000,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq084vxx0euhc36tcnsyjf4ny590v94rjpsv8pttm
    权重: 12,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqwgd9av2fhmndvvqklw7f7v6vmn4faanvcn879gl
    权重: 12,000,000.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcq04879ez40q29z9f7xf3gz5rfh2uh24jhsuj5nra
    权重: 0.00 CKB

================================================================================
昵称: kaixin (ID: 50960)
Metaforo 记录权重: 30,000,000.00
计算出的链上总权重: 30,000,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfg779ryncmyvd0sf8ud2g23s4l0m6u95gypr0y6
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdh9pw6ktcf8tvq0hedrgpmjmhumj2pscghf8qm3
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdnetnkt45q7jshvfzlgxr0an6mvvjmwtgz9lxnz
    权重: 0.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqw208dq57wm9u8kyqvgekcz9nlj97lntrqkf4rwn
    权重: 5,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqg9tfnasncvu2sfgu55av7e60nv48260vclne5sz
    权重: 5,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2fzjdqq3tn2xyw2jurtennwks7uztpfeqa5qjyc
    权重: 5,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqv26thzjwl09selm8mscgdx5gq504yeydqtqj3jr
    权重: 5,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvactr7302q7d2php7v7dfjuhzqtmhxkvg637g7r
    权重: 5,000,000.00 CKB
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsq2zakxet2tryz6mwhadqwc8v8czmwrn5pgjq2h2u
    权重: 5,000,000.00 CKB

================================================================================
昵称: 22222bit (ID: 50066)
Metaforo 记录权重: 22,222.00
计算出的链上总权重: 22,222.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfmmaugarkeg9f2jwe69455024d90ytc0g2h7ngu
    权重: 22,222.00 CKB
  - 地址: ckb1qzl58smqy32hnrq6vxjedcxe2fugvnz497h7yvwqvwel40uh4rltcqdnhv7a4lnu9csdkr5yvukqdp3ufysrzuqye97ds
    权重: 0.00 CKB

================================================================================
昵称: KevinW (ID: 50133)
Metaforo 记录权重: 20,000,000.00
计算出的链上总权重: 20,000,000.00
----------------------------------------
绑定的地址及各自权重:
  - 地址: ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvnyvfytcls75sqf3hjj5wd9pu5zujhf9cfnlx49
    权重: 20,000,000.00 CKB
================================================================================

JSON 文件已保存至: /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/No_152820057CKB_20260115_120459(UTC+8).json
CSV 文件已保存至: /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/No_152820057CKB_20260115_120459(UTC+8).csv

================================================================================
所有投票选项处理完毕！
共生成 4 个文件:
  - /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/Yes_92994150CKB_20260115_120459(UTC+8).json
  - /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/Yes_92994150CKB_20260115_120459(UTC+8).csv
  - /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/No_152820057CKB_20260115_120459(UTC+8).json
  - /Users/aabbcc/Documents/nervos/code/github/ckbfans/ckb-dao-watchdog/dao-v1.0/./vote_result/66568/No_152820057CKB_20260115_120459(UTC+8).csv
aabbcc@192 ckb-dao-watchdog % 
```

## 许可证

MIT 许可证
