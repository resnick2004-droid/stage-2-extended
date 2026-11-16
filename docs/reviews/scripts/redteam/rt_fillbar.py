"""Red team, independent of track D's code: does F-01's fill-bar rule ("on the fill bar a stop touch is a loss and a
target touch is not counted"; stop first on a later two-barrier bar) bias the lift over the mirror when both sides are
settled by it? Same fills settled two ways: (a) F-01's bar rules on 1-minute bars, (b) the exact one-second path after
the trigger second. Driftless walk; increments Gaussian or Student-t(3) (fat tails), scaled to sd `sig` ticks a minute.
Resistance approached from below; break = buy stop at L+1 (fill L+2, or open+1 on a gap); fade = sell limit at L (fill
on a bar trading L+1). bias = lift(bar rules) - lift(exact). Usage: rt_fillbar.py sig S R tails trials seed"""
import sys
import numpy as np


def settle_bar(hi, lo, m, F, side, S, tgt):
    stop, targ = F - side * S, F + side * tgt
    h, l = hi[m:], lo[m:]
    st = (l <= stop) if side > 0 else (h >= stop)
    tg = ((h >= targ) if side > 0 else (l <= targ)).copy()
    tg[0] = False
    js = st.argmax() if st.any() else 10 ** 9
    jt = tg.argmax() if tg.any() else 10 ** 9
    return 0.0 if js == jt == 10 ** 9 else float(jt < js)


def settle_path(path, F, side, S, tgt):
    st = (path <= F - side * S) if side > 0 else (path >= F - side * S)
    tg = (path >= F + side * tgt) if side > 0 else (path <= F + side * tgt)
    js = st.argmax() if st.any() else 10 ** 9
    jt = tg.argmax() if tg.any() else 10 ** 9
    return 0.0 if js == jt == 10 ** 9 else float(jt < js)


def main():
    sig, S, R, tails, trials, seed = float(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
    rng = np.random.default_rng(seed)
    minutes, T = 120, 7200
    tgt = int(round(R * S))
    acc = {k: [] for k in ("brk_bar", "brk_exact", "fad_bar", "fad_exact")}
    amb_brk = []
    done = 0
    while done < trials:
        n = 200
        if tails == "t3":
            inc = rng.standard_t(3, size=(n, T)) / np.sqrt(3.0)
        else:
            inc = rng.standard_normal((n, T))
        p = np.cumsum(np.rint(inc * sig / np.sqrt(60.0)).astype(np.int32), axis=1)
        L = rng.integers(1, max(2, int(3 * sig)), size=n)
        bars = p.reshape(n, minutes, 60)
        o, hi, lo = bars[:, :, 0], bars.max(axis=2), bars.min(axis=2)
        for i in range(n):
            hit = np.flatnonzero(p[i] >= L[i] + 1)
            if not len(hit):
                continue
            t = hit[0]
            m = t // 60
            if m >= minutes - 1 or t % 60 == 0 and m > 0 and o[i, m] >= L[i] + 1 and False:
                continue
            Fb = (o[i, m] + 1) if o[i, m] >= L[i] + 1 else (L[i] + 2)
            Ff = L[i]
            path = p[i, t + 1:]
            acc["brk_bar"].append(0.5 * (settle_bar(hi[i], lo[i], m, Fb, +1, S, tgt) - settle_bar(hi[i], lo[i], m, Fb, -1, S, tgt)))
            acc["brk_exact"].append(0.5 * (settle_path(path, Fb, +1, S, tgt) - settle_path(path, Fb, -1, S, tgt)))
            acc["fad_bar"].append(0.5 * (settle_bar(hi[i], lo[i], m, Ff, -1, S, tgt) - settle_bar(hi[i], lo[i], m, Ff, +1, S, tgt)))
            acc["fad_exact"].append(0.5 * (settle_path(path, Ff, -1, S, tgt) - settle_path(path, Ff, +1, S, tgt)))
            amb_brk.append(float(lo[i, m] <= Fb - S or hi[i, m] >= Fb + S))
        done += n
    v = {k: np.array(x) for k, x in acc.items()}
    nb = len(v["brk_bar"])
    db = v["brk_bar"] - v["brk_exact"]
    df = v["fad_bar"] - v["fad_exact"]
    print(f"sig={sig:g} S={S} R={R} tails={tails} fills={nb}: fill bars reaching a stop {100 * np.mean(amb_brk):.2f}%")
    print(f"   break: bar {100 * v['brk_bar'].mean():+.2f}  exact {100 * v['brk_exact'].mean():+.2f}  bias {100 * db.mean():+.2f} (se {100 * db.std(ddof=1) / np.sqrt(nb):.2f})")
    print(f"   fade : bar {100 * v['fad_bar'].mean():+.2f}  exact {100 * v['fad_exact'].mean():+.2f}  bias {100 * df.mean():+.2f} (se {100 * df.std(ddof=1) / np.sqrt(nb):.2f})")


if __name__ == "__main__":
    main()
