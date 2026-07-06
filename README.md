# PCA Neutral Alpha 
## Project Idea
- build a model pipeline where we engineer features / alpha factors, residualise the returns against PCA factors on a rolling basis to use as targets, predict these residualised returns with a basic model (elastic net), construct a PCA factor neutral portfolio, backtest and run everything with high quality data on quantconnect
- use a large US universe as a starting point (elastic net)
- focus on alpha factor research 
- evaluate factors and model on rank IC and ICIR


## (Some) Parameters
- weekly retraining
- daily rebalancing
- 1 year lookback for the PCA (might need to increase later)
- 1 year lookback for the model (might need to increase later)
- for now just use SP500 constituents (easy benchmarking and mostly liquid enough)
- for testing purposes: run with 1m$ and 1 year of OOS data for now


## Steps
1. create algorithm scaffolding
2. create research notebook to write pipeline parts and inspect / test data
3. write the simplest fully working pipeline possible - make sure everything runs smoothly
4. focus on factor / feature research






























---

## Disclaimer

This repository is strictly for personal educational and research purposes. All code, notes, and implementations are developed entirely independently in my personal time, using publicly available resources, textbook theory, and open datasets. 

The views, expressions, and code contained herein are solely my own and do not reflect the opinions, strategies, or positions of my current or any former employers. This project is not affiliated with, endorsed by, or connected to any commercial entity.
