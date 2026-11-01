# POLYMARKET BOT

7 Polymarket Up/Down bots, rebuilt from the public trades of 7 real wallets that made
**$3,359,960** between them. None of them predicts Bitcoin.

One file per bot, about 30 lines each. **Paper only:** they write to `ledger.json`.
There is no code in this repo that can place a real order or touch a wallet.

> Article with the math, one real market per bot and the embedded posts:
> "7 Polymarket Bots Made $3.36M Without Predicting Bitcoin" by @Scratcherrrr on X.

## the 7 bots

| file | rebuilt from | made | the rule |
|---|---|---|---|
| `sniper99.py` | BoneOhio | +$353,669 | last 2 min of BTC 5m, buy the side already at 94-99c |
| `ladder.py` | Haunting-Cheese | +$556,440 | penny bids 1-8c on both sides, wait for a panic seller |
| `cheapside.py` | pspspsps5 | +$299,217 | late in the window: loser for pennies, leader at 80-85c |
| `pairs.py` | 0xb55fa | +$1,290,000 | bid both sides so Up + Down costs at most $0.96 |
| `maker15.py` | gabigol | +$354,210 | BTC 15m, rest a ladder under the bid, never sell |
| `dipchase.py` | dangerously-skip-permissions | +$254,190 | pair early, dip bids 12-19c, chase the leader, small hedge |
| `lock.py` | almach | +$252,234 | keep buying the weaker side until both outcomes are green |

Profit numbers are all-time, at the moment each wallet was checked (Oct 2026).
Their code is not public. These files are my rebuild of what the fills show, not their bots.

| shared file | what it does |
|---|---|
| `pm.py` | finds the live Up/Down window, reads the order book, keeps the paper ledger |
| `run.py` | paper-runs the bots every 5 seconds on the live books, day stop at -$50 |
| `report.py` | one line per bot, optional Grok read on which bot to pause |
| `sim.py` | offline test on a fake BTC random walk, no internet needed |

## the one formula under all seven

A share pays $1 if its side wins and $0 if it loses. Buy at price `p`, real chance of
winning `q`:

```
expected profit per share = q - p
```

Every bot is a different way to find trades where `q > p` without forecasting anything.
Up + Down always pays exactly $1, so `pairs.py` and `lock.py` work on the sum:
if one share of each cost less than $1, you made the difference whatever Bitcoin does.

## run it on your computer

```bash
git clone https://github.com/scartcher/POLYMARKET-BOT
cd POLYMARKET-BOT
pip install -r requirements.txt

python sim.py                  # 6 h offline test first, no internet
python run.py                  # all 7, paper, live Polymarket books, every 5 s
python run.py sniper99 lock    # only these two
python report.py               # markets, green, spent, paper pnl per bot
```

## run it inside Grok Bot

1. Open your Grok Bot's computer, click **Take over**, open the terminal.
2. Get the files:
   ```bash
   cd /workspace && git clone https://github.com/scartcher/POLYMARKET-BOT
   cd POLYMARKET-BOT
   pip install -r requirements.txt
   ```
3. Save your xAI key without it showing on screen (only `report.py grok` needs it):
   ```bash
   read -rs -p "xai key: " K && printf 'XAI_API_KEY=%s\n' "$K" > .env && unset K && chmod 600 .env
   ```
4. Start the desk on paper and leave it running in the terminal:
   ```bash
   python run.py
   ```
5. Click **I'm done** and tell the bot:
   `Every morning at 9, in /workspace/POLYMARKET-BOT run python report.py grok and send me the answer.`

Grok reads the table and tells you which bot to keep, which to pause, and the one
number that made it decide.

Tip: paste the whole article into your Grok Bot and say
"build bot #4 on paper and show me the ledger after one hour."

## built so it can't hurt you

- **Paper only.** Bots write to `ledger.json`. No keys, no wallet, no order endpoint.
- **One order per price per market**, max $50 a side unless a bot sets a smaller cap.
- **Day stop.** Paper P&L hits -$50 and `run.py` stops everything.
- **Honest fills.** A resting bid only fills if the ask actually comes down to it.
- `report.py` never trades, it only reads the ledger.

## the honest catch

`python sim.py` is the 6 hour test from the article: random BTC, fair odds, no rebates,
nobody panic-selling.

```
bot         mkts  green     spent       pnl
maker15       25     10   1479.93   +141.55
sniper99      67     64   1379.96    -17.55
lock          25      7   4901.71    -55.87
cheapside     71      9    956.02   -184.28
dipchase      73     21   2799.98   -241.42
ladder        68      3    796.99   -272.00
pairs         73     27   4469.97   -349.03
```

They all lose a little. The real wallets win on three things this code does not give you:
speed, maker rebates (gabigol $41,838, dangerously-skip-permissions $139,939) and other
traders dumping into their bids. Run a week on paper before you even think about real money.

## files it creates

- `ledger.json` every paper order, filled or resting, and every settled window

Not financial advice. Polymarket is not available in every country, check your local rules.

MIT license.
