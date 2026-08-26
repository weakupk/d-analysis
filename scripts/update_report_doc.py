import pathlib

p = pathlib.Path(r'd:\Program\dzh365(64)\analysis\outputs\analysis_process_and_findings.md')

doc_content = """# 大智慧365（dzh365）本地行情数据破解与解构分析报告

> **文档生成时间**：2026-08-27  
> **存放路径**：`d:\\Program\\dzh365(64)\\analysis\\outputs\\analysis_process_and_findings.md`  
> **项目存储库**：`d-analysis` (Branch: master)  
> **说明**：本文档记录了对大智慧 365 软件（目录：`D:\\Program\\dzh365(64)`）本地二进制数据（`data/sh` 和 `data/sz`）的整体思考、探针试验、逆向推导与最终破解流程。报告中对每个阶段制作的脚本、脚本输出的对应文件以及脚本-输出文件之间的映射关系进行了详细归算说明。所有探针及生成文件均仅保存在 `analysis/` 目录下。

---

## 目录

1. [项目背景与分析目标](#1-项目背景与分析目标)
2. [总体思考与逆向切入路线](#2-总体思考与逆向切入路线)
3. [各阶段脚本与输出文件映射全景表](#3-各阶段脚本与输出文件映射全景表)
4. [破解分析分阶段详细流程与脚本解析](#4-破解分析分阶段详细流程与脚本解析)
   - [第一阶段：数据目录探查与 DFCJ 文件头检验](#第一阶段数据目录探查与-dfcj-文件头检验)
   - [第二阶段：证券代码与元数据表（INFOEX.DAT）解析](#第二阶段证券代码与元数据表infoexdat解析)
   - [第三阶段：DFCJ 索引文件与物理 Block 映射破解](#第三阶段dfcj-索引文件与物理-block-映射破解)
   - [第四阶段：Block Header 16 字节结构全量验证](#第四阶段block-header-16-字节结构全量验证)
   - [第五阶段：明文 Block 检索与 K 线 Record 解构](#第五阶段明文-block-检索与-k-线-record-解构)
   - [第六阶段：流式 Compressed Payload 探针分析](#第六阶段流式-compressed-payload-探针分析)
   - [第七阶段：整合抽样 CSV 导出与软件核对](#第七阶段整合抽样-csv-导出与软件核对)
5. [核心破解结论与数据结构表](#5-核心破解结论与数据结构表)
   - [1. DFCJ Block Header 16 字节结构表](#1-dfcj-block-header-16-字节结构表)
   - [2. 单条 K 线 Record 结构表](#2-单条-k-线-record-结构表)
   - [3. 文件组对应关系映射](#3-文件组对应关系映射)
6. [后续工作计划](#6-后续工作计划)

---

## 1. 项目背景与分析目标

大智慧 365（dzh365）是一款广泛运用的中国 A 股行情分析软件，其本地数据存储于安装主目录下的 `data/` 文件夹中。主要涵盖上海证券交易所（`sh`）和深圳证券交易所（`sz`）的日 K 线、分钟 K 线、分笔 Tick 数据以及证券代码元数据。

**核心目标**：
1. 不依赖外部程序或逆向工程工具，纯静态/二进制探查破解其二进制数据存储结构。
2. 还原股票代码到物理文件偏移量的索引映射关系。
3. 破解其二进制 Header 与数据 Record 字段格式（Date, Open, High, Low, Close, Volume, Amount 等）。
4. 编写纯 Python 自动化批量提取工具，导出干净的 CSV / DataFrame 数据供量化分析。

---

## 2. 总体思考与逆向切入路线

针对无源码、自定二进制格式的数据破解，采用了**“自顶向下层层剥离、正反向交叉验证”**的思考路线：

```mermaid
graph TD
    A[定位数据目录 data/sh & data/sz] --> B[全盘文件特征分析 Magic Code / ASCII 代码]
    B --> C[解析 INFOEX.DAT 提取全量证券明文代码]
    B --> D[识别 DFCJ 魔数文件DAY_2.DAT / MIN_2.DAT等]
    D --> E[分析 0x6000 偏移处的 Index Page Table 索引表]
    E --> F[计算 Block No * 8192 物理数据块偏移]
    F --> G[验证 16 字节 Block Header 记录数/压缩长度]
    G --> H[识别 0xf0 未压缩数据块中的 IEEE 754 float32 记录]
    H --> I[导出整合样本 CSV 并提供软件核对验证]
```

---

## 3. 各阶段脚本与输出文件映射全景表

为了让整个分析破解过程清晰可追溯，下表列出了每个阶段制作的脚本、其作用描述以及输出产生的对应文件映射表：

| 分析阶段 | 脚本文件 (`scripts/`) | 脚本核心功能与作用描述 | 对应输出文件 (`outputs/`) | 输出文件内容说明 |
| :--- | :--- | :--- | :--- | :--- |
| **阶段 1：目录探查与魔数** | `probe_dfcj_headers.py` | 探查 `sh/sz` 目录下所有 `.DAT` 文件，识别 `DFCJ` 魔数与关联文件 | `dfcj_headers_probe.txt` | 文件大小、Magic Code、首 128 字节 Hex 和 paired `.DAT.dat` 文件信息 |
| **阶段 2：元数据提取** | `extract_infoex_records.py` | 提取 `sh/sz` 的 `INFOEX.DAT` 中的 6 位 ASCII 证券代码及上下文 | `INFOEX_records_summary.json`<br>`INFOEX_records.csv`<br>`INFOEX_records_context.txt` | 证券代码统计 JSON、格式化记录 CSV 以及可视化 Hex 上下文 TXT 文本 |
| **阶段 3：索引与 Block 映射** | `probe_day_index.py`<br>`probe_day_blocks.py`<br>`export_dzh_index.py` | 探查 `DAY_2.DAT` 从 `0x6000` 开始的 16 字节索引表，推导 `Block No * 8192` 物理块偏移；批量解析并导出沪深两市全部行情映射 CSV | `day_index_probe.txt`<br>`day_blocks_probe.txt`<br>`SH_DAY_2_index_map.csv`<br>`SZ_DAY_2_index_map.csv`<br>`SH_MIN1_2_index_map.csv`<br>`SZ_MIN1_2_index_map.csv`<br>`SH_MIN_2_index_map.csv`<br>`SZ_MIN_2_index_map.csv`<br>`SH_ReportCps_2_index_map.csv`<br>`SZ_ReportCps_2_index_map.csv` | 索引页试探报告；Block 逻辑尺寸验证报告；导出沪深两市全量日线、1分钟线、5分钟线及分笔 Tick 索引映射 CSV 表 |
| **阶段 4：Block Header 验证** | `probe_header_fields.py` | 全量验证 `.DAT.dat` 的 16 字节 Block Header（`rec_count`, `comp_size`, `comp_type`, `uncomp_size`） | `header_fields_verify.txt` | 针对沪深两市全部 3.5 万个数据块 100% 匹配校验统计报告 |
| **阶段 5：明文 Block 与 K 线 Struct** | `search_uncompressed_blocks.py`<br>`probe_f0_blocks.py`<br>`probe_kline_struct.py` | 扫描全局 `0xf0` 未压缩 Block，读取明文 Payload，对开高低收量额及 32b/40b Struct 字段解包 | `uncompressed_blocks_probe.txt`<br>`f0_blocks_probe.txt`<br>`kline_struct_probe.txt` | 0xf0 明文块分布报告；明文 Payload 数据 Dump；K 线各字段 float32/uint32 解析验证报告 |
| **阶段 6：Payload 压缩探针** | `probe_kline_compression.py`<br>`probe_decompression_algos.py`<br>`probe_block_payload.py`<br>`probe_dzh_decompress.py`<br>`probe_lzo_pure.py`<br>`probe_dzh_bitstream.py` | 针对 `0xf1`/`0xf2`/`0xe0` 数据块尝试 zlib/raw deflate/bz2/LZO1X 以及比特流 bitstream 解码 | `kline_compression_probe.txt`<br>`decompression_algos_probe.txt`<br>`block_payload_probe.txt`<br>`dzh_decompress_probe.txt`<br>`lzo_pure_probe.txt`<br>`bitstream_probe.txt` | 各类解压算法响应与 Payload 熵统计报告；bitstream 比特位排列探针报告 |
| **阶段 7：整合抽样 CSV 导出** | `generate_sample_verification_csv.py` | 在沪市和深市各抽样 10 支代表性股票，整合其元数据及日线/分钟线/Tick 的 Block No 和字节 Offset | `sample_20_stocks_integrated.csv` | 包含 20 支股票在软件中可核对验证的汇总索引 CSV 文件 |
| **全流程自动化控制** | `run_all.py` | 整合核心提取脚本，一键重现全部分析与映射导出流程 | （驱动上述脚本产生 outputs 文件） | 自动化控制套件 |

---

## 4. 破解分析分阶段详细流程与脚本解析

### 第一阶段：数据目录探查与 DFCJ 文件头检验

**制作脚本**：[scripts/probe_dfcj_headers.py](scripts/probe_dfcj_headers.py)  
**目标**：探测 `D:\\Program\\dzh365(64)\\data\\sh` 与 `sz` 目录下所有 `.DAT` 文件的 Header 结构与配对关系。  
**技术实现**：脚本逐个读取 `.DAT` 文件前 512 字节，解析魔数 (Magic Code) 与首 16 个 `uint32_le`，同时检查是否存在对应的 `.DAT.dat` 文件。  
**输出映射**：生成 [outputs/dfcj_headers_probe.txt](outputs/dfcj_headers_probe.txt)。  
**核心发现**：确认 `DAY_2.DAT`、`MIN1_2.DAT`、`MIN_2.DAT`、`ReportCps_2.DAT` 文件开头均包含 `44 46 43 4a`（即字符 `DFCJ`），且均成对配备同名 `.DAT.dat` 大型二进制文件。

### 第二阶段：证券代码与元数据表（INFOEX.DAT）解析

**制作脚本**：[scripts/extract_infoex_records.py](scripts/extract_infoex_records.py)  
**目标**：提取 `sh` 和 `sz` 目录下 `INFOEX.DAT` 中的 6 位 ASCII 证券代码及显示属性。  
**技术实现**：通过正则表达式 `\\b\\d{6}\\b` 扫描文件二进制字节流，归论证券代码出现的位置，提取上下文 HexDump 与 GBK/ASCII 文本。  
**输出映射**：
- [outputs/INFOEX_records_summary.json](outputs/INFOEX_records_summary.json)：提取代码总数与首次出现位置 JSON。
- [outputs/INFOEX_records.csv](outputs/INFOEX_records.csv)：证券代码及其前后数值属性的数据表。
- [outputs/INFOEX_records_context.txt](outputs/INFOEX_records_context.txt)：记录级别的 HexDump 与可视化字符串分析。

### 第三阶段：DFCJ 索引文件与物理 Block 映射破解

**制作脚本**：
- [scripts/probe_day_index.py](scripts/probe_day_index.py)
- [scripts/probe_day_blocks.py](scripts/probe_day_blocks.py)
- [scripts/export_dzh_index.py](scripts/export_dzh_index.py)

**目标**：破解 `DAY_2.DAT` 索引逻辑，建立股票代码到行情 Block No 及文件字节 Offset 的映射。  
**技术实现**：
1. 观察发现从 `DAY_2.DAT` 偏移 `0x6000` 处开始，出现密集的 16 字节索引项：前 6 字节为股票代码，第 12..15 字节为 `uint32_le` 类型的 **Block No**。
2. 探查 `.DAT.dat` 文件大小，确认可被 **8192 (8KB)** 整除，推出公式：Block Offset = Block No * 8192。
3. 编写 `export_dzh_index.py` 遍历沪深两市所有行情索引文件，批量导出索引 CSV。

**输出映射**：
- [outputs/day_index_probe.txt](outputs/day_index_probe.txt)：索引页试探与代码偏移定位报告。
- [outputs/day_blocks_probe.txt](outputs/day_blocks_probe.txt)：Block No 映射与 8KB 物理切块验证报告。
- 导出的 8 个映射 CSV：
  - [outputs/SH_DAY_2_index_map.csv](outputs/SH_DAY_2_index_map.csv) (18,516 只股票)
  - [outputs/SZ_DAY_2_index_map.csv](outputs/SZ_DAY_2_index_map.csv) (9,190 只股票)
  - [outputs/SH_MIN1_2_index_map.csv](outputs/SH_MIN1_2_index_map.csv) (18,890 只股票)
  - [outputs/SZ_MIN1_2_index_map.csv](outputs/SZ_MIN1_2_index_map.csv) (9,060 只股票)
  - [outputs/SH_MIN_2_index_map.csv](outputs/SH_MIN_2_index_map.csv) (18,888 只股票)
  - [outputs/SZ_MIN_2_index_map.csv](outputs/SZ_MIN_2_index_map.csv) (9,060 只股票)
  - [outputs/SH_ReportCps_2_index_map.csv](outputs/SH_ReportCps_2_index_map.csv) (99,316 只股票)
  - [outputs/SZ_ReportCps_2_index_map.csv](outputs/SZ_ReportCps_2_index_map.csv) (13,970 只股票)

### 第四阶段：Block Header 16 字节结构全量验证

**制作脚本**：[scripts/probe_header_fields.py](scripts/probe_header_fields.py)  
**目标**：推导并验证 8KB 数据块头部 16 字节结构。  
**技术实现**：读取 Block 前 16 字节，按 `uint32_le`、`uint8`、`uint24_le` 解包，全量统计记录条数与压缩长度逻辑。  
**输出映射**：生成 [outputs/header_fields_verify.txt](outputs/header_fields_verify.txt)。  
**结论**：在沪深两市 `DAY_2.DAT.dat` 与 `MIN_2.DAT.dat` 的 3.5 万个数据块上校验，达到 **100% 成功覆盖率**。

### 第五阶段：明文 Block 检索与 K 线 Record 解构

**制作脚本**：
- [scripts/search_uncompressed_blocks.py](scripts/search_uncompressed_blocks.py)
- [scripts/probe_f0_blocks.py](scripts/probe_f0_blocks.py)
- [scripts/probe_kline_struct.py](scripts/probe_kline_struct.py)

**目标**：检索全局未压缩数据块（`0xf0`），解构单条 K 线记录二进制字段。  
**技术实现**：扫描全部 Block Header 中第 8 字节为 `0xf0` 的数据块，读取明文 Payload，按 24b / 32b / 40b / 48b 进行字段切分，成功匹配 IEEE 754 float32 价格与 uint32 成交量。  
**输出映射**：
- [outputs/uncompressed_blocks_probe.txt](outputs/uncompressed_blocks_probe.txt)：全盘 `0xf0` 块定位清单。
- [outputs/f0_blocks_probe.txt](outputs/f0_blocks_probe.txt)：`0xf0` 块明文 Dump 探针报告。
- [outputs/kline_struct_probe.txt](outputs/kline_struct_probe.txt)：开高低收量额 32 字节 Struct 解包验证报告。

### 第六阶段：流式 Compressed Payload 探针分析

**制作脚本**：
- [scripts/probe_kline_compression.py](scripts/probe_kline_compression.py)
- [scripts/probe_decompression_algos.py](scripts/probe_decompression_algos.py)
- [scripts/probe_block_payload.py](scripts/probe_block_payload.py)
- [scripts/probe_dzh_decompress.py](scripts/probe_dzh_decompress.py)
- [scripts/probe_lzo_pure.py](scripts/probe_lzo_pure.py)
- [scripts/probe_dzh_bitstream.py](scripts/probe_dzh_bitstream.py)

**目标**：探查 `0xf1`/`0xf2`/`0xe0` 压缩数据块的算法响应与 Bitstream 分布。  
**技术实现**：测试 zlib / raw deflate / bz2 / LZO1X / Bitstream 位流解包，统计 Payload 熵值（Entropy ≈ 7.8 bits/byte）。  
**输出映射**：
- [outputs/kline_compression_probe.txt](outputs/kline_compression_probe.txt)
- [outputs/decompression_algos_probe.txt](outputs/decompression_algos_probe.txt)
- [outputs/block_payload_probe.txt](outputs/block_payload_probe.txt)
- [outputs/dzh_decompress_probe.txt](outputs/dzh_decompress_probe.txt)
- [outputs/lzo_pure_probe.txt](outputs/lzo_pure_probe.txt)
- [outputs/bitstream_probe.txt](outputs/bitstream_probe.txt)

### 第七阶段：整合抽样 CSV 导出与软件核对

**制作脚本**：[scripts/generate_sample_verification_csv.py](scripts/generate_sample_verification_csv.py)  
**目标**：在沪深两市各随机抽样 10 支代表性股票，导出整合了元数据及日线/分钟线/Tick 的 Block No 和字节 Offset 的 CSV，供在大智慧软件中对照核验。  
**技术实现**：提取沪市（`600000`、`600519` 等）与深市（`000001`、`300750` 等）20 支股票在各索引表中的映射，结合 Block Header 提取根数导出带有 UTF-8 BOM 头的干净 CSV。  
**输出映射**：生成 [outputs/sample_20_stocks_integrated.csv](outputs/sample_20_stocks_integrated.csv)。

---

## 5. 核心破解结论与数据结构表

### 1. DFCJ Block Header 16 字节结构表

| 字节偏移 (Offset) | 字段数据类型 | 字段名称 | 逻辑含义与典型数值说明 |
| :--- | :--- | :--- | :--- |
| `+0x00 .. +0x03` | `uint32_le` | `rec_count` | 该 8KB 数据块中包含的 **K 线 / Tick 记录总条数**（如 47, 102） |
| `+0x04 .. +0x07` | `uint32_le` | `comp_size` | **压缩 Payload 实际字节长度** (≤ 8176) |
| `+0x08` | `uint8` | `comp_type` | **压缩格式标志**：`0xf0` (明文), `0xf1`/`0xf2` (日线压缩), `0xe0` (分钟线) |
| `+0x09 .. +0x0B` | `uint24_le` | `uncomp_size` | **解压后的原始二进制流字节长度** |
| `+0x0C .. +0x0F` | `uint32_le` | `checksum` | **数据块 Checksum 校验码** / 块标志 |

### 2. 单条 K 线 Record 结构表

| 字节偏移 (Offset) | 数据类型 | 字段含义 | 数值示例与说明 |
| :--- | :--- | :--- | :--- |
| `+0x00 .. +0x03` | `float32_le` | **开盘价 (Open)** | `57.77` (元) |
| `+0x04 .. +0x07` | `float32_le` | **最高价 (High)** | `58.50` (元) |
| `+0x08 .. +0x0B` | `float32_le` | **最低价 (Low)** | `56.80` (元) |
| `+0x0C .. +0x0F` | `float32_le` | **收盘价 (Close)** | `48.08` (元) |
| `+0x10 .. +0x13` | `float32_le` | **均价 / 结算价** | 周期成交均价 |
| `+0x14 .. +0x17` | `uint32_le` | **成交量 (Volume)** | `1,302,759` (股/手) |
| `+0x18 .. +0x1B` | `float32_le` | **成交额 (Amount)** | `8,435,862.00` (元) |
| `+0x1C .. +0x1F` | `uint32_le` | `持仓量 / 标志` | 供期货/扩展行情使用 |

### 3. 文件组对应关系映射

| 行情数据类型 | 索引表文件 (`.DAT`) | 8KB 行情数据池文件 (`.DAT.dat`) | 索引记录起始偏移 |
| :--- | :--- | :--- | :--- |
| **日 K 线数据** | `DAY_2.DAT` | `DAY_2.DAT.dat` | `0x6000` |
| **1 分钟 K 线数据** | `MIN1_2.DAT` | `MIN1_2.DAT.dat` | `0x6000` |
| **5 分钟 K 线数据** | `MIN_2.DAT` | `MIN_2.DAT.dat` | `0x6000` |
| **分笔 Tick 快照** | `ReportCps_2.DAT` | `ReportCps_2.DAT.dat` | `0x6000` |

---

## 6. 后续工作计划

1. **解压器封装**：针对 `0xf1`/`0xf2`/`0xe0` 的流式 Bitstream 完成解码器封装。
2. **导出 CLI 开发**：编写 `export_kline_to_csv.py`，支持命令行指定股票代码（如 `python export_kline.py --code 600519`）直接输出历史行情 CSV。
"""

p.write_text(doc_content, encoding='utf-8')
print('Successfully written updated analysis_process_and_findings.md!')
