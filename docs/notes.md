\# Analysis Notes



This repository is used to analyze local Dazhihui 365 data files.



\## Current findings



\### SH/INFOEX.DAT

\- Contains 6-digit security codes in plain text.

\- Appears to be a structured metadata table, not a price history file.

\- Code fields are stable and occur with repeated nearby patterns.

\- Likely contains security metadata such as:

&#x20; - code

&#x20; - market

&#x20; - category

&#x20; - display/format attributes

&#x20; - numeric properties



\### DFCJ-prefixed files

Several `.DAT` files start with the magic `DFCJ`, suggesting a custom Dazhihui container/header format.



\### Raw XML files

Files under `Raw/` are XML pools and appear to contain watchlist / pool data.



\## Open questions

\- Exact record layout in INFOEX.DAT

\- Relationship between .DAT and .DAT.dat files

\- Meaning of repeated numeric and float fields

\- Mapping between file headers and index files



\## Next steps

\- Improve field extraction around code offsets

\- Build a file map for SH / SZ / HK / FI

\- Extract small samples from raw files for deeper analysis

