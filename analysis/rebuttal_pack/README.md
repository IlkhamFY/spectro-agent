# Rebuttal pack

Rescores the locked IRSpectra-Bench n=500 headline and the other deposited runs. Writes Wilson intervals, paired tests, breakdowns, a structure gallery, and two print figures.

```bash
python analysis/rebuttal_pack/run_all.py
```

Needs RDKit, NumPy, Matplotlib, and Pillow. The script reads expansion deposits from git object `48fcd30153df5e331fab43cfa514763db8ee3891` and the resolved corpus already in this repo. It does not call a model and it does not edit locked benchmark files.

Outputs land in `outputs/`. `REPORT.md` is rewritten by the script.

The gallery uses commercial-pool structures only. CC-BY-NC rows are used in memory for the join and are not written out. NMRTrans files under `inputs/nmrtrans/` are model outputs, not spectra.

Tanimoto in this pack is prediction versus the true structure. It is not a training-set or memorization check.

## Figure checklist

Scored against the attached style spec, 0 to 2. Both print figures are 180 mm wide.

| # | Item | Score |
|---|---|---|
| 1 | Final width 180 mm, type 5 to 8 pt | 2 |
| 2 | One sans family, embedded. Bold only on panel letters. Caption in serif | 2 |
| 3 | Panel letters bold, lowercase, same corner | 2 |
| 4 | Headline solver in one accent. Baselines grey. Other models keep one hue | 2 |
| 5 | Every accuracy has a Wilson interval and an n | 2 |
| 6 | Values sit on the data. Legends are short | 2 |
| 7 | At least four data panels | 2 |
| 8 | Molecules from one RDKit helper, same pixel size | 2 |
| 9 | Accuracy panels share a 0 to 100 scale | 2 |
| 10 | No top or right spines, no 3D, no heavy grid | 2 |
| 11 | Panels answer slice gaps, input ablation, size, and failure mode | 2 |
| 12 | Vector PDF and 300 dpi PNG | 2 |

Total 24/24. Calibration and cost are not plotted. The deposits have neither a confidence nor a token or time log, and the report says so instead of drawing stand-in points.
