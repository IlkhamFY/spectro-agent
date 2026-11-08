# IRexp v0.2 counts (8 November 2026)

Counted from the public Hugging Face dataset [ilkhamfy/IRexp](https://huggingface.co/datasets/ilkhamfy/IRexp), release commit `9ee1aa9b2f462cef8cf18489e45a516a4b716193` (`release v0.2`). Hub `main` (`a60074e162dd5fc0b04af45c87eef206108bdf4b`) only updates the dataset card; `data/SHA256SUMS.txt` is identical, and the five JSONL files below match those checksums. Numbers are in `irexp_v02_counts.json`.

## What was counted

The redistributed files are the public downloadable union:

| File | Rows |
|---|---:|
| `data/irexp_commercial.jsonl.gz` | 163,931 |
| `data/irexp_non_commercial.jsonl.gz` | 65,007 |
| `data/irexp_sharealike.jsonl.gz` | 1,897 |
| `data/irexp_other.jsonl.gz` | 5 |
| **Public downloadable** | **230,840** |

`data/irexp_resolved_commercial.jsonl.gz` (67,235) is the commercial rows with a released structure. Its ids are exactly those commercial rows. It is not an extra pool.

The dataset card's research corpus is **239,735**. The other **8,895** rows are the empty/unknown-licence pool. The card says they are not redistributed, and they are not in the Hub files. Modality counts for that slice were not estimated. In the JSON they are `null`.

On the rows that are public:

|  | Public downloadable | Commercial pool |
|---|---:|---:|
| Rows | 230,840 | 163,931 |
| At least one IR band | 230,840 | 163,931 |
| Non-empty ¹H string | 113,131 | 85,006 |
| Non-empty ¹³C string | 99,976 | 74,451 |
| Released structure | 96,956 | 67,235 |
| Complete triple (all four) | **50,668** | **36,927** |
| Unique InChIKey-14 among those triples | **47,901** | **34,612** |

Every public row has at least three IR bands, so the “at least one band” count equals the row count. The commercial complete-triple count on the resolved file is the same 36,927 rows and 34,612 InChIKey-14 keys.

Per-pool complete triples: commercial 36,927, non-commercial 13,739, ShareAlike 2, CC-BY-ND 0. Unique InChIKey-14 inside those pools: 34,612, 13,341, 2, and 0. The public-union unique count (47,901) counts a key once when the same connectivity block appears in more than one pool. Per-pool unique counts sum to 47,955, which is 54 extra memberships.

Full 27-character InChIKeys among complete triples: 48,256 public, 34,892 commercial. The gaps versus InChIKey-14 (355 public, 280 commercial) are keys that share a connectivity block and differ later in the key.

## Definitions

**At least one IR band.** `ir_bands_cm-1` is a list of length at least 1. A second count requires length at least 3. On these files the two counts are equal.

**Non-empty NMR string.** `h_nmr` or `c_nmr` is a string whose `strip()` is not empty. `null`, a missing key, and a non-string fail. No whitespace-only string and no non-string NMR value occurred, so this rule matches a Python truthiness test on the string. It does not parse shifts. A field that is only `1H`, `13C`, `2CO`, or `3 is` still counts.

Inside the complete triples, 25 public rows (19 commercial, 6 non-commercial, none in ShareAlike or CC-BY-ND) have one of those four exact strings. None of the 25 has both fields in that set. They stay in the primary totals. The observed complete-row strings are `h_nmr` = `1H` (3) and `c_nmr` = `13C` (19), `2CO` (2), `3 is` (1).

**Released structure.** `has_structure` is true, or `structure_tier` is `A`, `B`, `C`, or `D`. On every public row those two tests agree with each other and with a non-empty `smiles`. Tier `X` is a withheld structure: `has_structure` is false and `smiles` is null (0 exceptions). A null `structure_tier` is not a released structure. The card's label `none` is this null. The string `none` does not appear.

**Tiers.** Taken from `structure_tier`. Public-file tier counts match `released_tiers` in `data/irexp_release_build_stats.json`. The card's research-corpus tier table sums to 239,735, and A–D sums to 101,624. Subtracting the public-file tiers from that table leaves a residual of 8,895 (A 315, B 2,881, C 793, D 679, X 341, null 3,886). That residual is arithmetic. Those rows were not opened.

**Commercial pool.** Rows in `irexp_commercial.jsonl.gz`. All 163,931 have `license_pool` = `commercial`. The four pool files are disjoint, and each row's `license_pool` matches its file.

**Complete triple.** One row with at least one IR band, a non-empty ¹H string, a non-empty ¹³C string, and a released structure. The previous ICLR manuscript's 39,118 on the 121,233-record corpus is this same four-way conjunction (there called a quadruple). The v0.2 release builder's `full_quadruple` is `has_structure` plus truthy `h_nmr` and `c_nmr`. On the public files that predicate returns the same counts as the complete triple (commercial 36,927, non-commercial 13,739, ShareAlike 2, other 0), which are the values already stored in `irexp_release_build_stats.json`.

**InChIKey-14.** The connectivity block: the substring of `inchikey` before the first hyphen. Every complete-triple row has a standard key `^[A-Z]{14}-[A-Z]{10}-[A-Z]$`, so the block is the first 14 characters. No complete-triple row lacked a key. The unique count is the number of distinct blocks, not the number of rows.

## Card totals this recount reproduces

From the public files, or by summing the card: research corpus 239,735; tiers A–D 101,624 (A 7,366, B 48,669, C 21,455, D 24,134); X 8,473; none 129,638; tiers A–B 56,035; commercial 163,931; resolved commercial 67,235; public downloadable 230,840.

`source_set` on the public files is `pmc_v4` 107,425, `si_2026` 121,527, `chemotion` 1,888. The card's main-text research total is 116,320. The difference is the same 8,895.

The Scientific Data repository states research-corpus figures that include those 8,895 rows (`data/irexp_stats.json`: any ¹H or ¹³C 123,667; quadruples 54,429; 97,374 structure-linked InChIKeys). Those figures were not recomputed here.
