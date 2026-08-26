# File Map

| File | Suspected Role | Status |
|------|----------------|--------|
| SH/INFOEX.DAT | Security metadata table | Confirmed by text codes |
| SH/DAY_2.DAT | Dazhihui container/header for daily data | Confirmed by DFCJ header |
| SH/DAY_2.DAT.dat | Index/data block associated with daily data | Header probed, paired with DAY_2.DAT |
| SH/MIN1_2.DAT | Dazhihui container/header for 1-min data | Confirmed by DFCJ header |
| SH/MIN1_2.DAT.dat | Data block associated with 1-min data | Header probed, paired with MIN1_2.DAT |
| SH/MIN_2.DAT | Dazhihui container/header for 5-min data | Confirmed by DFCJ header |
| SH/MIN_2.DAT.dat | Data block associated with 5-min data | Header probed, paired with MIN_2.DAT |
| SH/ReportCps_2.DAT | Dazhihui container/header for tick/report data | Confirmed by DFCJ header |
| SH/ReportCps_2.DAT.dat | Data block associated with tick/report data | Header probed, paired with ReportCps_2.DAT |
| SH/EXTDAY.DAT | Extended day-related container | Under analysis |
| SZ/INFOEX.DAT | Shenzhen security metadata table | Confirmed by text codes |
| HK/INFOEX.DAT | Hong Kong security metadata table | Confirmed by text codes |
| FI/INFOEX.DAT | Financial/instrument metadata table | Confirmed by text codes |
| Raw/*.XML | Pool/watchlist definitions | Confirmed XML |
| Extra/EDINFO.INF | Auxiliary info / field formatting | Confirmed by strings |
| Extra/EDENTRY.INF | Auxiliary index / metadata table | Under analysis |
| Extra/EDSTRING.DAT | Auxiliary string table | Under analysis |
| A$/block.ini | Block configuration | Confirmed text |
