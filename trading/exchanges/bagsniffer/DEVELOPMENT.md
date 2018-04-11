# Background and development info

## What it's all about
Bagsniffer tracks your cryptocurrency holdings on the exchanges and blockchain addresses that you define. It
automatically keeps track of your trading activity.

### Motivation
I was unable to find a crypto portfolio tracking tool:

- with a reasonable amount of autodiscovery
- where I would not risk disclosing my holdings and trading activity to a centralized 3rd party

### Reason to open source and expectations
I decided to open source Bagsniffer "as is", in case it could be helpful for somebody else, and in the hope that I might 
get one or the other external contribution in return.

Bagsniffer fulfills a private need for me, and I will keep tailoring it to my private portfolio tracking needs. At
this time, I have no big plans to turn this tool into a public service, or to offer a hosted version of it. 

DM me on Twitter (@cryptic_monk) if you want to contribute to Bagsniffer, or have questions. I cannot offer any kind
of support for this tool. 

### Advantages
- keeps track of your portfolio and your trading performance
- close to 100 exchanges supported
- close to 30 blockchains supported
- auto discovery of buys, sells and staking/MN returns
- handles service outages gracefully
- self-hosted, so nobody sees your bags except you
- small number of dependencies, so not very hard to set up

### Limitations
- max granularity of tracking: 1h
- rough entry/exit price calculation based on Coinmarketcap data (can be manually overridden)
- no concept of epochs so far (e.g. trading performance over days/weeks/months/years, ytd etc.)

### Challenges
- requires a bit of know-how to set up (on a VPS, or Raspberry Pi for example)
- configuration is clumsy still, a smoother experience is in preparation

## Development
This is a proof of concept/early alpha version of bagsniffer. It has many limitations and many technical
shortcuts have been taken to reach first results quickly.

### Core architecture
- Bagsniffer is a "daemon" type script designed to run on a server, roughly every hour. On every run, the script
produces the necessary datasets required for frontend display.
- The frontend of Bagsniffer is, for now, a simple collection of HTML/JS/CSS files that display the
.json datasets produced by the script. The frontend can thus be served statically, further increasing security.

### Main components
- chains.py: get onchain holdings via various block explorers
- exchanges.py: get exchange holdings via APIs/ccxt
- coins_manual.py: manual holding entries
- coin_data.py: ticker info via coinmarketcap
- portfolio.py: pulls together the portfolio
- analyzer.py: detects buys/sells/stakes
- config_reader.py: helper to read "human-readable" configuration files
- bagsniffer.py: the main script that calls the other functions and produces frontend output
- config/: human readable configuration files as described in README.md
- webroot/: static files for the frontend, based on Bootstrap
- webroot/data: datasets for the frontend (produced by bagsniffer.py)
- history/: historical portfolio data used for analysis
- cache/: fallback data in case of service outages