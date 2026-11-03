"""Main-result figures at final print size. Style comes from paperstyle only."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from paperstyle import (
    PALETTE, add_mol, figsize, panel_label, save_fig,
)

from chem import changed_atoms, mol, tanimoto


def mol_ok(it):
    return mol(it["smiles"]) is not None and mol(it["opus"][0]) is not None

HERE = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

MODEL_COLOR = {
    "Opus": PALETTE["accent"],
    "NMRTrans": PALETTE["grey_dark"],
    "grok-4.6": PALETTE["orange"],
    "grok-4.6-clean": PALETTE["navy"],
    "gemini-3.7-flash": PALETTE["teal"],
    "gpt-5.6-sol": PALETTE["royal"],
    "gpt-5.6-luna": PALETTE["violet"],
    "composer-2.5": PALETTE["slate"],
    "Fable": PALETTE["green"],
    "Sonnet": PALETTE["blue"],
    "Haiku": PALETTE["grey"],
}


def _xerr(p, lo, hi):
    """Wilson bounds can sit a float above 1. Clamp so Matplotlib accepts the bar."""
    return [[max(0.0, (p - lo) * 100.0)], [max(0.0, (hi - p) * 100.0)]]


def _lighten(hex_color, amount=0.45):
    rgb = np.array(mpl.colors.to_rgb(hex_color))
    return mpl.colors.to_hex(rgb + (1.0 - rgb) * amount)


def _row(rows, name, metric):
    for r in rows:
        if r["name"] == name and r["metric"] == metric:
            return r
    raise KeyError((name, metric))


def _paired_bars(ax, entries, title, letter):
    """entries: list of (label, top1_row, top3_row, color). Top of the axis is the first entry."""
    n = len(entries)
    y = np.arange(n)
    h = 0.34
    for i, (label, top, rec, color) in enumerate(entries):
        light = _lighten(color, 0.42)
        yy = n - 1 - i
        for row, dy, col, name in (
            (rec, 0.18, light, "top-3"),
            (top, -0.18, color, "top-1"),
        ):
            p, lo, hi = row["p"], row["lo"], row["hi"]
            ax.barh(yy + dy, p * 100, height=h, color=col, zorder=2)
            ax.errorbar(
                p * 100, yy + dy,
                xerr=_xerr(p, lo, hi),
                fmt="none", ecolor="black", elinewidth=0.5, capsize=1.2, zorder=3,
            )
            ax.text(hi * 100 + 1.3, yy + dy, f"{p * 100:.1f}", va="center", ha="left", fontsize=5, color=PALETTE["ink"])
        # n sits on the tick
    ax.set_yticks(y, [entries[n - 1 - i][0] for i in range(n)])
    ax.set_xlabel("Accuracy (%)")
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_title(title)
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(facecolor=PALETTE["accent"], label="top-1"),
        Patch(facecolor=PALETTE["accent_light"], label="top-3"),
    ], loc="upper right")
    tag(ax, letter)


def _dots(ax, series, title, letter, ylabel):
    """series: list of (name, rows, color) where rows have name, p, lo, hi, k, n."""
    # categories from the first series, which is in display order
    cats = [r["name"] for r in series[0][1]]
    y = np.arange(len(cats))[::-1]
    offsets = np.linspace(-0.12, 0.12, len(series)) if len(series) > 1 else [0.0]
    for (name, rows, color), off in zip(series, offsets):
        by = {r["name"]: r for r in rows}
        xs, xlo, xhi, ys = [], [], [], []
        for i, cat in enumerate(cats):
            r = by[cat]
            xs.append(r["p"] * 100)
            xlo.append((r["p"] - r["lo"]) * 100)
            xhi.append((r["hi"] - r["p"]) * 100)
            ys.append(y[i] + off)
        xlo = [max(0.0, v) for v in xlo]
        xhi = [max(0.0, v) for v in xhi]
        ax.errorbar(xs, ys, xerr=[xlo, xhi], fmt="o", color=color, ms=2.6, elinewidth=0.5, capsize=1.0, label=name, zorder=3)
    labels = []
    by0 = {r["name"]: r for r in series[0][1]}
    for cat in cats:
        r = by0[cat]
        labels.append(f"{cat} ({r['n']})")
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Top-1 accuracy (%)")
    ax.set_title(title)
    ax.grid(axis="x", lw=0.3, color=PALETTE["grey_light"], zorder=0)
    if len(series) > 1:
        ax.legend(loc="center right")
    tag(ax, letter)


def _forest(ax, rows, title, letter):
    rows = list(rows)
    y = np.arange(len(rows))[::-1]
    for i, r in enumerate(rows):
        color = MODEL_COLOR.get(r["b"], PALETTE["accent"])
        if r["a"] == "Opus" and r["b"] == "NMRTrans":
            color = PALETTE["accent"]
        ax.errorbar(
            r["diff"] * 100, y[i],
            xerr=_xerr(r["diff"], r["lo"], r["hi"]),
            fmt="o", color=color, ms=3, elinewidth=0.6, capsize=1.2,
        )
        ax.text(r["hi"] * 100 + 1.2, y[i], f"{r['diff'] * 100:+.1f}", va="center", fontsize=5)
    ax.axvline(0, color=PALETTE["grey"], lw=0.6, ls=(0, (2, 2)))
    short = {"NMRTrans": "NMRTrans", "grok-4.6": "Grok", "gemini-3.7-flash": "Gemini", "gpt-5.6-sol": "GPT-5.6 Sol"}
    ax.set_yticks(y, [f"vs {short.get(r['b'], r['b'])} ({r['n']})" for r in rows])
    ax.set_xlabel("Top-1 difference (points)")
    ax.set_title(title)
    if rows:
        lo = min(r["lo"] for r in rows) * 100 - 6
        hi = max(r["hi"] for r in rows) * 100 + 10
        ax.set_xlim(lo, hi)
    tag(ax, letter)


def _hist(ax, values, title, xlabel, letter, note):
    vals = np.asarray(values, dtype=float)
    ax.hist(vals, bins=np.linspace(0, 1, 11), color=PALETTE["accent"], edgecolor="white", linewidth=0.3)
    if len(vals):
        med = float(np.median(vals))
        ax.axvline(med, color=PALETTE["ink"], lw=0.6, ls=(0, (2, 2)))
        note = f"median {med:.2f}\n{note}"
    ax.set_xlim(0, 1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Wrong rank-1 answers")
    ax.set_title(title)
    ax.text(0.98, 0.95, note, transform=ax.transAxes, ha="right", va="top", fontsize=5, color=PALETTE["grey_dark"])
    tag(ax, letter)


def _pick_gallery(items, k_ok=3, k_near=2, k_far=3):
    # Small commercial molecules draw cleanly at print size. Far misses stay formula-correct
    # so the panel shows a wrong constitution, not an unreadable string.
    pool = [it for it in items if it.get("pool") == "commercial" and it.get("opus") and mol_ok(it) and it["hac"] <= 22]
    def diverse(cands, k):
        chosen = []
        if k <= 0:
            return chosen
        for it in cands:
            if any((tanimoto(it["smiles"], c["smiles"]) or 0) > 0.55 for c in chosen):
                continue
            chosen.append(it)
            if len(chosen) == k:
                break
        return chosen

    ok = [it for it in pool if it["opus_top1"]]
    ok.sort(key=lambda it: it["hac"])
    # spread across size: take from each tercile first
    if ok:
        cuts = [ok[0], ok[len(ok) // 2], ok[-1]]
        rest = [it for it in ok if it not in cuts]
        successes = diverse(cuts + rest, k_ok)
    else:
        successes = []

    near = [it for it in pool if (not it["opus_top1"]) and it.get("tani") is not None and it["tani"] >= 0.55 and it["opus_formula_ok"]]
    near.sort(key=lambda it: -it["tani"])
    nears = diverse(near, k_near)

    far = [it for it in pool if (not it["opus_top1"]) and it.get("tani") is not None and it["tani"] < 0.30 and it["opus_formula_ok"]]
    far.sort(key=lambda it: it["tani"])
    fars = diverse(far, k_far)
    examples = []
    for it in successes:
        examples.append((it, "correct"))
    for it in nears:
        examples.append((it, f"near {it['tani']:.2f}"))
    for it in fars:
        examples.append((it, f"far {it['tani']:.2f}"))
    return examples


def _draw_pair(fig, spec, it, caption, label=None):
    ax_t = fig.add_subplot(spec[0])
    ax_p = fig.add_subplot(spec[1])
    pred = it["opus"][0]
    ok = bool(it["opus_top1"])
    add_mol(ax_t, it["smiles"], caption="truth", ok=True)
    hi = [] if ok else changed_atoms(it["smiles"], pred)
    add_mol(ax_p, pred, caption=caption, ok=ok, highlight=hi or None, color=None if ok else PALETTE["accent"])
    if label:
        tag(ax_t, label)


def tag(ax, letter):
    bb = ax.get_position()
    ax.figure.text(bb.x0 - 0.008, bb.y1 + 0.006, letter,
                   fontsize=8, fontweight="bold", ha="right", va="bottom", color="black")


def save_exact(fig, stem):
    """Write at the figure's own size. Tight cropping changes the print width."""
    fig.savefig(f"{stem}.pdf")
    fig.savefig(f"{stem}.png", dpi=300)
    plt.close(fig)
    return f"{stem}.pdf", f"{stem}.png"


def fig_main(bundle, result, stem):
    items = bundle["headline"]
    rows = result["headline_rows"]
    fig = plt.figure(figsize=figsize(180, 188))
    gs = fig.add_gridspec(
        3, 3, height_ratios=[1.20, 1.10, 1.15],
        hspace=0.58, wspace=0.58,
        left=0.11, right=0.985, top=0.95, bottom=0.07,
    )

    entries = []
    for label, name, color in (
        ("Opus, n=500", "Opus n=500", PALETTE["accent"]),
        ("NMRTrans, n=500", "NMRTrans n=500", PALETTE["grey_dark"]),
        ("Opus, locked 194", "Opus locked 194", PALETTE["accent_mid"]),
        ("Opus, +106", "Opus +106", _lighten(PALETTE["accent"], 0.25)),
        ("Opus, 200-cut", "Opus expand-500 200", _lighten(PALETTE["accent"], 0.55)),
    ):
        entries.append((label, _row(rows, name, "top-1"), _row(rows, name, "top-3"), color))
    _paired_bars(fig.add_subplot(gs[0, 0]), entries, "Headline set, with the three slices", "a")

    # cross-vendor top-1 on the shared 60. Order by top-1.
    m60 = [r for r in result["model60_rows"] if r["metric"] == "top-1"]
    # drop the clean-clone from this panel; it is a control, plotted nowhere as a second model
    m60 = [r for r in m60 if r["name"] != "grok-4.6-clean"]
    m60 = sorted(m60, key=lambda r: -r["p"])
    ax = fig.add_subplot(gs[0, 1])
    y = np.arange(len(m60))[::-1]
    for i, r in enumerate(m60):
        color = MODEL_COLOR.get(r["name"], PALETTE["grey"])
        ax.barh(y[i], r["p"] * 100, color=color, height=0.62, zorder=2)
        ax.errorbar(r["p"] * 100, y[i], xerr=_xerr(r["p"], r["lo"], r["hi"]),
                    fmt="none", ecolor="black", elinewidth=0.5, capsize=1.1, zorder=3)
        ax.text(r["hi"] * 100 + 1.2, y[i], f"{r['p'] * 100:.0f}", va="center", fontsize=5)
    disp = {"gemini-3.7-flash": "Gemini", "grok-4.6": "Grok 4.6", "gpt-5.6-sol": "GPT-5.6 Sol",
            "gpt-5.6-luna": "GPT-5.6 Luna", "composer-2.5": "Composer", "Opus": "Opus"}
    ax.set_yticks(y, [f"{disp.get(r['name'], r['name'])} ({r['n']})" for r in m60])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Top-1 accuracy (%)")
    ax.set_title("Same 60 compounds, rank-1")
    tag(ax, "b")

    # modality campaign top-1
    order = ["full", "noIR", "noH", "noC", "formulaIR", "noFormula"]
    ab = [r for r in result["ablation_rows"] if r["set"] == "campaign" and r["metric"] == "top-1"]
    ab_by = {r["name"]: r for r in ab}
    ab = [ab_by[k] for k in order if k in ab_by]
    labels = {
        "full": "full",
        "noIR": "no IR",
        "noH": "no 1H",
        "noC": "no 13C",
        "formulaIR": "formula+IR",
        "noFormula": "no formula",
    }
    ax = fig.add_subplot(gs[0, 2])
    y = np.arange(len(ab))[::-1]
    for i, r in enumerate(ab):
        color = PALETTE["accent"] if r["name"] == "full" else PALETTE["grey"]
        ax.barh(y[i], r["p"] * 100, color=color, height=0.62, zorder=2)
        ax.errorbar(r["p"] * 100, y[i], xerr=_xerr(r["p"], r["lo"], r["hi"]),
                    fmt="none", ecolor="black", elinewidth=0.5, capsize=1.1, zorder=3)
        ax.text(min(r["hi"] * 100 + 1.2, 92), y[i], f"{r['k']}/{r['n']}", va="center", fontsize=5)
    ax.set_yticks(y, [f"{labels.get(r['name'], r['name'])} ({r['n']})" for r in ab])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Top-1 accuracy (%)")
    ax.set_title("Later campaign, not the headline")
    tag(ax, "c")

    heavy_nmr = []
    heavy_opus = []
    for r in result["heavy"]:
        heavy_opus.append({k: r[k] for k in ("name", "k", "n", "p", "lo", "hi")})
        nr = r["nmr"]
        heavy_nmr.append({"name": r["name"], "k": nr["k"], "n": nr["n"], "p": nr["p"], "lo": nr["lo"], "hi": nr["hi"]})
    _dots(
        fig.add_subplot(gs[1, 0]),
        [("Opus", heavy_opus, PALETTE["accent"]), ("NMRTrans", heavy_nmr, PALETTE["grey_dark"])],
        "By heavy-atom count", "d", "",
    )
    ring_short = {
        "acyclic": "acyclic",
        "single aliphatic ring": "1 aliph. ring",
        "single aromatic ring": "1 arom. ring",
        "polycyclic aliphatic": "poly. aliph.",
        "polycyclic aromatic": "poly. arom.",
    }
    ring_rows = []
    for r in result["rings"]:
        rr = dict(r)
        rr["name"] = ring_short.get(r["name"], r["name"])
        ring_rows.append(rr)
    _dots(
        fig.add_subplot(gs[1, 1]),
        [("Opus", ring_rows, PALETTE["accent"])],
        "By ring class", "e", "",
    )

    forest_rows = []
    for r in result["paired"]:
        if r["family"] == "n500" and r["metric"] == "top-1":
            forest_rows.append(r)
        elif r["family"] == "cross60" and r["a"] == "Opus" and r["metric"] == "top-1":
            forest_rows.append(r)
    _forest(fig.add_subplot(gs[1, 2]), forest_rows, "Opus minus the other model", "f")

    examples = _pick_gallery(items)
    n_ex = len(examples)
    cols = 4
    rows_g = int(np.ceil(n_ex / cols))
    sub = gs[2, :].subgridspec(rows_g, cols * 2, wspace=0.08, hspace=0.55)
    for i, (it, cap) in enumerate(examples):
        r, c = divmod(i, cols)
        pair = sub[r, c * 2:(c * 2 + 2)].subgridspec(1, 2, wspace=0.04)
        _draw_pair(fig, (pair[0, 0], pair[0, 1]), it, cap, label="g" if i == 0 else None)
        print(f"gallery {cap} hac={it['hac']} top1={it['opus_top1']} tani={it['tani']}")
    fig.text(0.5, 0.032, "Teal frame: rank-1 matches. Magenta frame: it does not. Highlighted atoms sit outside the common substructure.",
             ha="center", va="bottom", fontsize=5.5, fontfamily="serif", color=PALETTE["ink"])
    fig.text(0.5, 0.012, "Every interval is a 95% Wilson interval. Panels b and c use the 60-task slice, not the n=500 headline.",
             ha="center", va="bottom", fontsize=5.5, fontfamily="serif", color=PALETTE["ink"])
    return save_exact(fig, stem), examples


def fig_breakdowns(bundle, result, stem):
    fig = plt.figure(figsize=figsize(180, 172))
    gs = fig.add_gridspec(
        3, 3, height_ratios=[1.20, 1.05, 0.95],
        hspace=0.58, wspace=0.55,
        left=0.14, right=0.985, top=0.95, bottom=0.055,
    )
    _dots(fig.add_subplot(gs[0, 0:2]), [("Opus", result["fg"], PALETTE["accent"])],
          "Functional group present in the true structure", "a", "")

    near = result["near"]
    note = f"formula match {near['formula_ok_misses']}/{near['n_miss']}"
    _hist(fig.add_subplot(gs[0, 2]), near["tanis"], "Tanimoto of wrong rank-1", "Morgan Tanimoto to the truth", "b", note)

    ax = fig.add_subplot(gs[1, 0])
    dists = near["mces_dists"]
    if dists:
        hi = max(dists)
        bins = np.arange(0, hi + 4, 4)
        ax.hist(dists, bins=bins, color=PALETTE["accent"], edgecolor="white", linewidth=0.3)
        med = float(np.median(dists))
        ax.axvline(med, color=PALETTE["ink"], lw=0.6, ls=(0, (2, 2)))
        ax.text(0.98, 0.95, f"median {med:.0f} bonds", transform=ax.transAxes, ha="right", va="top", fontsize=5)
    ax.set_xlabel("MCES distance (bonds)")
    ax.set_ylabel("Wrong rank-1 answers")
    ax.set_title("How many bonds differ")
    tag(ax, "c")

    # formula adherence
    ax = fig.add_subplot(gs[1, 1])
    formula_rows = []
    # Opus and NMRTrans on 500, from the items
    items = bundle["headline"]
    for name, key, color in (
        ("Opus n=500", "opus_formula_ok", PALETTE["accent"]),
        ("NMRTrans n=500", "nmr_formula_ok", PALETTE["grey_dark"]),
    ):
        k = int(sum(it[key] for it in items))
        formula_rows.append((name.replace(" n=500", "") + f" ({len(items)})", k, len(items), color))
    disp = {"gemini-3.7-flash": "Gemini", "grok-4.6": "Grok", "gpt-5.6-sol": "GPT Sol",
            "gpt-5.6-luna": "GPT Luna", "composer-2.5": "Composer", "Opus": "Opus 60"}
    for r in result["model60_rows"]:
        if r["metric"] == "formula" and r["name"] != "grok-4.6-clean":
            formula_rows.append((f"{disp.get(r['name'], r['name'])} ({r['n']})", r["k"], r["n"], MODEL_COLOR.get(r["name"], PALETTE["grey"])))
    y = np.arange(len(formula_rows))[::-1]
    for i, (name, k, n, color) in enumerate(formula_rows):
        p = k / n
        lo, hi = _wilson_pair(k, n)
        ax.barh(y[i], p * 100, color=color, height=0.62, zorder=2)
        ax.errorbar(p * 100, y[i], xerr=_xerr(p, lo, hi),
                    fmt="none", ecolor="black", elinewidth=0.5, capsize=1.0, zorder=3)
        if hi > 0.90:
            ax.text(p * 100 - 1.5, y[i], f"{p * 100:.0f}", va="center", ha="right", fontsize=5, color="white")
        else:
            ax.text(hi * 100 + 1.0, y[i], f"{p * 100:.0f}", va="center", fontsize=5)
    ax.set_yticks(y, [t[0] for t in formula_rows])
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Rank-1 matches the given formula (%)")
    ax.set_title("Formula adherence")
    tag(ax, "d")

    # wall
    ax = fig.add_subplot(gs[1, 2])
    wall = [
        ("verified", 204, PALETTE["teal"]),
        ("misranked", 45, PALETTE["accent"]),
        ("not in list", 251, PALETTE["grey_dark"]),
    ]
    y = np.arange(len(wall))[::-1]
    for i, (name, k, color) in enumerate(wall):
        p = k / 500
        lo, hi = _wilson_pair(k, 500)
        ax.barh(y[i], p * 100, color=color, height=0.62, zorder=2)
        ax.errorbar(p * 100, y[i], xerr=_xerr(p, lo, hi),
                    fmt="none", ecolor="black", elinewidth=0.5, capsize=1.1, zorder=3)
        ax.text(hi * 100 + 1.2, y[i], f"{k}", va="center", fontsize=5)
    ax.set_yticks(y, [n for n, _, _ in wall])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of the 500 (%)")
    ax.set_title("Forward-verify wall, n=500")
    tag(ax, "e")

    # four near / far molecules already chosen? draw a fresh commercial near-miss strip
    examples = _pick_gallery(items, k_ok=0, k_near=2, k_far=2)
    # _pick_gallery with k_ok=0 still runs successes logic but diverse([], 0) returns []
    sub = gs[2, :].subgridspec(1, 8, wspace=0.12, hspace=0.2)
    shown = examples[:4]
    for i, (it, cap) in enumerate(shown):
        pair = sub[0, i * 2:(i * 2 + 2)].subgridspec(1, 2, wspace=0.05)
        _draw_pair(fig, (pair[0, 0], pair[0, 1]), it, cap, label="f" if i == 0 else None)
    fig.text(
        0.5, 0.012,
        "Tanimoto and MCES compare rank-1 to the true structure, not to a training set. "
        "Wall counts are locked. Intervals on them are Wilson intervals.",
        ha="center", va="bottom", fontsize=5.5, fontfamily="serif", color=PALETTE["ink"],
    )
    return save_exact(fig, stem)


def _wilson_pair(k, n):
    from stats import wilson
    _, lo, hi = wilson(k, n)
    return lo, hi


def before_after(before, after, dest, before_label, after_label):
    b = Image.open(before).convert("RGB")
    a = Image.open(after).convert("RGB")
    w = a.width
    b = b.resize((w, max(1, int(b.height * w / b.width))), Image.Resampling.LANCZOS)
    font = ImageFont.truetype(FONT, 28)
    pad = 18
    cap = 44

    def block_h(img):
        return cap + img.height

    canvas = Image.new("RGB", (w + pad * 2, pad + block_h(b) + 12 + block_h(a) + pad), "white")
    draw = ImageDraw.Draw(canvas)
    y = pad
    draw.text((pad, y), before_label, fill="#222222", font=font)
    y += cap
    canvas.paste(b, (pad, y))
    y += b.height + 12
    draw.text((pad, y), after_label, fill="#222222", font=font)
    y += cap
    canvas.paste(a, (pad, y))
    canvas.save(dest, dpi=(150, 150))
    return dest
