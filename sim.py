# sim.py
# offline test, no internet needed: a fake BTC random walk drives fake Up/Down books,
# every bot paper-trades 6 hours of 5 minute and 15 minute windows, then prints the table.
#   python sim.py            6 hours, seed 7 (the run quoted in the article)
#   python sim.py 24 42      24 hours, seed 42
# fair odds, no rebates, nobody panic-selling. expect small losses. that is the point.
import math, random, sys
import pm, run

HOURS = float(sys.argv[1]) if len(sys.argv) > 1 else 6
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)

T0 = 1793000000
clock = [T0]
pm.time.time = run.time.time = lambda: clock[0]
price, opens = {}, {}


def btc(t):
    if t not in price:
        price[t] = price.get(t - 5, 83000) + random.gauss(0, 9)
        if random.random() < 0.004:                       # a sudden $120 move
            price[t] += random.choice([-1, 1]) * 120
    return price[t]


def parse(slug):
    return int(slug.split("-")[3]), int(slug.split("-")[2][:-1])


def p_up(slug, t):
    """fair price of Up: chance BTC ends above the open, given time left"""
    start, mins = parse(slug)
    o = opens.setdefault(slug, btc(start))
    left = max(1, start + mins * 60 - t)
    z = (btc(t) - o) / (9 * math.sqrt(left / 5) + 1e-9)
    return min(0.99, max(0.01, 0.5 * (1 + math.erf(z / math.sqrt(2)))))


def market(slug):
    start, mins = parse(slug)
    end = start + mins * 60
    closed = clock[0] >= end + 30
    won = None
    if closed:
        won = "up" if btc(end - end % 5) >= opens.setdefault(slug, btc(start)) else "down"
    return {"slug": slug, "up": slug + "|up", "down": slug + "|down",
            "closed": closed, "won": won}


def book(token):
    slug, side = token.split("|")
    p = p_up(slug, clock[0])
    p = p if side == "up" else 1 - p
    if random.random() < 0.05:                            # someone sweeps the book
        p += random.uniform(-0.03, 0.03)
    ask = min(0.99, max(0.01, round(p + 0.01, 2)))
    bid = max(0.0, round(p - 0.01, 2))
    return {"bid": bid, "ask": ask, "asks": [(ask, 400), (min(0.99, ask + 0.01), 800)]}


pm.market, pm.book = market, book
bots = [__import__(n) for n in run.ALL]
L, cache = {"orders": [], "settled": {}}, {}
for i in range(int(HOURS * 3600) // 5):
    clock[0] = T0 + i * 5
    run.tick(bots, L, cache)
    if i % 12 == 0:
        pm.settle(L, market)
clock[0] += 3600
pm.settle(L, market)

print(f"{HOURS:g} h simulated, fair market, paper only\n")
print(f"{'bot':<10} {'mkts':>5} {'green':>6} {'spent':>9} {'pnl':>9}")
for b, r in sorted(pm.stats(L).items(), key=lambda kv: -kv[1]["pnl"]):
    print(f"{b:<10} {r['markets']:>5} {r['green']:>6} {r['cost']:>9.2f} {r['pnl']:>+9.2f}")
