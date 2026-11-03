"""Publication figure style. Tokens from FIGURE_SPEC.md. Style reference only."""
import io, math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

MM = 1 / 25.4
WIDTH_FULL, WIDTH_COL = 180, 88  # mm

PALETTE = {
    "accent": "#b83280", "accent_light": "#d9a7c0", "accent_mid": "#c47aa1",
    "grey_dark": "#5f5f5f", "grey": "#9a9a9a", "grey_light": "#d4d4d4",
    "green": "#7baf9e", "blue": "#8b9ed3", "slate": "#6f799e",
    "orange": "#d97757", "teal": "#10a37f", "royal": "#4285f4",
    "violet": "#6f63b6", "navy": "#3157a4", "ink": "#222222",
}
CYCLE = [PALETTE[k] for k in ("accent", "slate", "green", "orange", "violet", "teal", "navy", "grey")]
CMAP_SEQ = mpl.colors.LinearSegmentedColormap.from_list("accent_seq", ["#ffffff", "#ead0de", "#d9a7c0", "#b83280", "#6d1d4c"])

def apply():
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
        "font.size": 6, "axes.titlesize": 6.5, "axes.titleweight": "normal", "axes.labelsize": 6,
        "xtick.labelsize": 5.5, "ytick.labelsize": 5.5, "legend.fontsize": 5.5,
        "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
        "xtick.major.size": 2, "ytick.major.size": 2, "xtick.major.pad": 1.5, "ytick.major.pad": 1.5,
        "lines.linewidth": 1.0, "lines.markersize": 3, "patch.linewidth": 0.5,
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": PALETTE["ink"],
        "axes.labelcolor": PALETTE["ink"], "xtick.color": PALETTE["ink"], "ytick.color": PALETTE["ink"],
        "axes.prop_cycle": mpl.cycler(color=CYCLE), "axes.titlepad": 3, "axes.labelpad": 2,
        "legend.frameon": False, "legend.handlelength": 1.2, "legend.borderaxespad": 0.2,
        "errorbar.capsize": 1.2, "figure.dpi": 150, "savefig.dpi": 300,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    })
apply()

def figsize(width_mm=WIDTH_FULL, height_mm=100):
    return (width_mm * MM, height_mm * MM)

def panel_label(ax, letter, x=-0.02, y=1.0, fig=None):
    """Bold lowercase 8 pt letter at top-left, outside the axes."""
    ax.text(x, y, letter, transform=ax.transAxes if fig is None else fig.transFigure,
            fontsize=8, fontweight="bold", ha="right", va="bottom", color="black")

def wilson_ci(k, n, z=1.96):
    k, n = np.asarray(k, float), np.asarray(n, float)
    p = np.where(n > 0, k / np.maximum(n, 1), np.nan)
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return c - h, c + h

def mol_image(smiles, size_px=(400, 320), bond_width=2.0, font_px=None, highlight=None, color=None):
    """Black-and-white skeletal formula, transparent background, returns RGBA numpy array."""
    from rdkit import Chem
    from rdkit.Chem import rdDepictor
    from rdkit.Chem.Draw import rdMolDraw2D
    from PIL import Image
    m = Chem.MolFromSmiles(smiles)
    rdDepictor.SetPreferCoordGen(True); rdDepictor.Compute2DCoords(m)
    d = rdMolDraw2D.MolDraw2DCairo(*size_px)
    o = d.drawOptions()
    o.useBWAtomPalette(); o.clearBackground = False; o.bondLineWidth = bond_width
    o.padding = 0.05; o.baseFontSize = 0.9; o.minFontSize = font_px or 22; o.maxFontSize = 40
    o.additionalAtomLabelPadding = 0.1
    if color: o.setHighlightColour(mpl.colors.to_rgba(color, 0.35))
    d.DrawMolecule(m, highlightAtoms=highlight or [], highlightBonds=[])
    d.FinishDrawing()
    return np.asarray(Image.open(io.BytesIO(d.GetDrawingText())).convert("RGBA"))

def add_mol(ax, smiles, caption=None, ok=None, **kw):
    ax.imshow(mol_image(smiles, **kw)); ax.set_axis_off()
    if caption:
        ax.text(0.5, -0.02, caption, transform=ax.transAxes, ha="center", va="top", fontsize=5.5)
    if ok is not None:
        c = PALETTE["teal"] if ok else PALETTE["accent"]
        ax.set_axis_on(); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_visible(True); sp.set_color(c); sp.set_linewidth(0.6)

def save_fig(fig, path_stem):
    for ext in ("pdf", "png"):
        fig.savefig(f"{path_stem}.{ext}", dpi=300, bbox_inches="tight", pad_inches=0.02)
    return f"{path_stem}.pdf", f"{path_stem}.png"
