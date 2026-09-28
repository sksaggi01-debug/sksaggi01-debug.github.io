"""
verify.py - reproduces every number in the portfolio's work samples.

Dr. Sarabjeet Kaur Bedi - https://sksaggi01-debug.github.io/
Standard library only. Exact fractions wherever the answer is rational.
Run:  python3 verify.py   (prints each check; stops at the first failure)
"""
from fractions import Fraction as F
import random


def check(label, got, want):
    assert got == want, f"{label}: got {got}, expected {want}"
    print(f"ok  {label}: {got}")


# ---------------------------------------------------------------------------
# 1. Task authoring - free-entry Cournot with a $30 excise (answer 500)
#    P = 100 - Q, MC = 2*3.50 + 3 = 10, weekly fixed cost = 140 + 60 = 200
# ---------------------------------------------------------------------------
A, MC, FIXED = 100, F(2) * F(7, 2) + 3, 140 + 60


def free_entry(tax):
    """Largest whole number of firms that still earns non-negative profit."""
    n = 0
    while F(A - MC - tax, n + 2) ** 2 - FIXED >= 0:
        n += 1
    return n


def welfare(tax, n=None):
    n = free_entry(tax) if n is None else n
    q = F(A - MC - tax, n + 1)
    Q = n * q
    consumer_surplus = Q * Q / 2
    profits = n * (q * q - FIXED)
    receipts = tax * Q
    return n, Q, A - Q, consumer_surplus + profits + receipts


n0, Q0, P0, W0 = welfare(0)
n1, Q1, P1, W1 = welfare(30)
check("firms before tax", n0, 5)
check("price before tax", P0, 25)
check("firms after tax", n1, 3)
check("price after tax", P1, 55)
check("fall in total surplus", W0 - W1, 500)
check("trap: firms held at 5", W0 - welfare(30, 5)[3], F(1375, 2))  # 687.5


# ---------------------------------------------------------------------------
# 2. Pairwise text evaluation - rent-control figures in the two responses
# ---------------------------------------------------------------------------
base_q, cut = 10_000, F(20, 100)
qd = base_q * (1 + F(4, 10) * cut)
qs_short = base_q * (1 - F(1, 10) * cut)
qs_long = base_q * (1 - F(8, 10) * cut)
check("quantity demanded at the cap", qd, 10_800)
check("short-run shortage", qd - qs_short, 1_000)
check("long-run shortage (Completion A said 1,600)", qd - qs_long, 2_400)


# ---------------------------------------------------------------------------
# 3. Benchmark question - first-price auction, 3 bidders, U[0,1] values
#    Revenue with reserve r: R(r) = 3 * integral_r^1 (2v - 1) v^2 dv
# ---------------------------------------------------------------------------
def revenue(r):
    r = F(r)
    return 3 * ((F(1, 2) - F(1, 3)) - (r ** 4 / 2 - r ** 3 / 3))


check("revenue at optimal reserve 1/2 (option F)", revenue(F(1, 2)), F(17, 32))
check("option A: no reserve", revenue(0), F(1, 2))
check("option C: reserve 2/3", revenue(F(2, 3)), F(1, 2))
check("option D: reserve 1/3", revenue(F(1, 3)), F(14, 27))
check("option G: conditional on sale", revenue(F(1, 2)) / (1 - F(1, 2) ** 3), F(17, 28))
r2 = F(1, 2)
check("option B: two-bidder revenue at reserve 1/2", 2 * ((F(2, 3) - F(1, 2)) - (F(2, 3) * r2 ** 3 - r2 ** 2 / 2)), F(5, 12))
check("option I: 1 - 17/32", 1 - revenue(F(1, 2)), F(15, 32))
check("option J: reserve 2/5", revenue(F(2, 5)), F(657, 1250))
bid_08 = 0.8 - (0.8 ** 3 - 0.5 ** 3) / (3 * 0.8 ** 2)
check("option E: bid at value 0.8 (rounded)", round(bid_08, 3), 0.598)

random.seed(1)
draws, total = 400_000, 0.0
for _ in range(draws):
    v = sorted(random.random() for _ in range(3))
    if v[2] >= 0.5:
        total += max(v[1], 0.5)          # second-price format, same expected revenue
sim = total / draws
assert abs(sim - 17 / 32) < 0.002, sim
print(f"ok  simulation check: {sim:.4f} vs {17/32:.4f}")


# ---------------------------------------------------------------------------
# 4. Peer review - Bertrand with Firm 1 capped at 30, MC 10, Q = 100 - P
# ---------------------------------------------------------------------------
residual_profit = lambda p: (p - 10) * (70 - p)      # Firm 2 after Firm 1 sells 30
best = max(range(10, 71), key=residual_profit)
check("Firm 2 residual-monopoly price", best, 40)
check("Firm 2 residual-monopoly profit", residual_profit(best), 900)
undercut = (100 - F(399, 10)) * (F(399, 10) - 10)
assert undercut > 900
print(f"ok  undercutting at 39.9 pays {float(undercut):.2f} > 900, so no pure-strategy equilibrium")


# ---------------------------------------------------------------------------
# 5. LLM response review - IS-LM with G rising by 30 (key 50)
#    IS: Y = 5(220 + G) - 100r      LM: m = 0.5Y - 25r
# ---------------------------------------------------------------------------
def is_lm(G, m):
    r = F(5 * (220 + G) - 2 * m, 150)
    return 2 * m + 50 * r, r


for m in (500, 1000):
    y0, _ = is_lm(150, m)
    y1, _ = is_lm(180, m)
    check(f"output rise with real balances {m}", y1 - y0, 50)
check("interest rate if L is read as nominal (m = 1000)", is_lm(150, 1000)[1], -1)


# ---------------------------------------------------------------------------
# 6. Adjudication - monopoly, P = 60 - 2Q, MC 12, $8 tax on consumers
# ---------------------------------------------------------------------------
Q_tax = F(60 - 8 - 12, 4)
check("quantity with tax", Q_tax, 10)
check("consumer price (option C)", 60 - 2 * Q_tax, 40)
check("seller receives (option G, also true)", 60 - 2 * Q_tax - 8, 32)


# ---------------------------------------------------------------------------
# 7. Method samples page
# ---------------------------------------------------------------------------
dwl = lambda t: 10 * F(t) ** 2
rev = lambda t: F(t) * (800 - 20 * F(t))
check("marginal excess burden", (dwl(8) - dwl(4)) / (rev(8) - rev(4)), F(3, 14))


def welfare_duopoly(leader):
    a, c1, c2 = 120, 20, 30
    if leader:
        q1 = F(a - 2 * c1 + c2, 2)
        q2 = F(a - c2, 2) - q1 / 2
    else:
        q1, q2 = F(a - 2 * c1 + c2, 3), F(a - 2 * c2 + c1, 3)
    Q = q1 + q2
    P = a - Q
    return Q * Q / 2 + (P - c1) * q1 + (P - c2) * q2


check("Stackelberg minus Cournot total surplus",
      welfare_duopoly(True) - welfare_duopoly(False), F(27775, 72))

alpha, s, x = F(1, 3), 0.2, 0.08
c_now = (1 - s) * (s / x) ** 0.5
c_gr = (1 - float(alpha)) * (float(alpha) / x) ** 0.5
check("golden-rule consumption gain, %", round((c_gr / c_now - 1) * 100, 2), 7.58)

print("\nAll checks passed.")
