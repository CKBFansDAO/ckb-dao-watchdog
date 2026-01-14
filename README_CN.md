# CKB DAO Watchdog 🐕

[English](./README.md)

社区驱动的 CKB DAO 治理投票结果审计和验证工具。

## 概述

CKB DAO Watchdog 是一套开源工具集，使社区成员能够独立验证 DAO 投票结果。通过比对链上数据与平台记录的权重，这些工具有助于确保 CKB DAO 治理的透明性和公正性。

## 功能特点

- **独立验证**：对比链上 Nervos DAO 存款验证投票权重
- **多平台支持**：目前支持 Metaforo（DAO v1.0），DAO v1.1 即将推出
- **透明审计**：导出详细的 JSON/CSV 报告供社区审查
- **双语支持**：提供中英文两个版本

## 目录结构

```
ckb-dao-watchdog/
├── dao-v1.0/                    # DAO v1.0 (Metaforo) 审计工具
│   ├── metaforo_watchdog_en.py  # 英文版
│   └── metaforo_watchdog_cn.py  # 中文版
│
└── dao-v1.1/                    # DAO v1.1 工具（即将推出）
```

## 快速开始

### 环境要求

- Python 3.11+
- 依赖包：

```bash
pip install requests pyckb
```

### 使用方法

```bash
# 进入 dao-v1.0 目录
cd dao-v1.0

# 使用 Metaforo 投票页面 URL 运行
python metaforo_watchdog_cn.py https://dao.ckb.community/thread/vot-ckb-integration-for-rosen-bridge-66568
```

详细使用说明请参阅 [dao-v1.0/README_CN.md](./dao-v1.0/README_CN.md)。

## 工作原理

1. **解析 URL**：从 Metaforo 投票页面 URL 中提取帖子 ID
2. **获取投票选项**：通过 Metaforo API 获取所有投票选项（如 Yes/No）
3. **获取投票者数据**：获取每个选项的所有投票者及其记录的权重
4. **查询链上数据**：对于每个投票者：
   - 获取其绑定的 CKB 地址（Neuron + MetaMask/PW Lock）
   - 通过 Explorer API 查询 Nervos DAO 存款
   - 计算实际链上权重
5. **比对并报告**：比较 Metaforo 权重与链上权重，标记差异

## 输出文件

对于每个投票选项，工具会生成：
- `vote_result_{thread_id}_{选项}_{时间戳}.json`
- `vote_result_{thread_id}_{选项}_{时间戳}.csv`

字段包括：
- `nickname`, `userid` - 用户昵称和 ID
- `total weight(metaforo)` - Metaforo 记录的权重
- `total weight(on chain, floored)` - 计算出的链上权重
- `address`, `address weight(floored)` - 地址及其权重
- `need_review` - 需要人工复核的标记
- `explorer_url` - CKB Explorer 地址链接

## 贡献

欢迎贡献！请随时提交 Issue 或 Pull Request。

## 许可证

MIT 许可证 - 详见 [LICENSE](./LICENSE)。

## 相关链接

- [CKB Community Fund DAO](https://dao.ckb.community)
- [Nervos CKB Explorer](https://explorer.app5.org)
- [CKBFans DAO](https://github.com/ckbfansdao)