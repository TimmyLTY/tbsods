# Reproduce the TBSODS resource

The repository supports three operations: use the annotated turns directly, rebuild them from WildChat plus frozen decisions, and recompute the analysis figures. The first-release reconstruction preserves the historical model outputs. It does not send requests to Qwen or an OpenAI API.

## 1. Install

Use Python 3.12 or later. The complete workflow was checked with Python 3.14.7 and the versions in `requirements.txt`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 2. Obtain the exact WildChat source

Use the non-toxic `allenai/WildChat-1M` default configuration, training split, revision `7d6490e462285cf85d91eabea0f9a954fbddcd1f`. Its 14 original Parquet shards contain 837,989 conversations. The download is approximately 3.1 GiB. Preserve the original shard names and row order; the resource uses positional locators.

The files are available in the [versioned source directory](https://huggingface.co/datasets/allenai/WildChat-1M/tree/7d6490e462285cf85d91eabea0f9a954fbddcd1f/data). This standard-library download command places them under `raw/`, which is excluded from Git:

```bash
python - <<'PY'
from pathlib import Path
from urllib.request import urlretrieve

revision = "7d6490e462285cf85d91eabea0f9a954fbddcd1f"
target = Path("raw/WildChat-1M/data")
target.mkdir(parents=True, exist_ok=True)
for i in range(14):
    name = f"train-{i:05d}-of-00014.parquet"
    url = f"https://huggingface.co/datasets/allenai/WildChat-1M/resolve/{revision}/data/{name}"
    print(name, flush=True)
    urlretrieve(url, target / name)
PY
```

Existing local copies of these same shards can be supplied through `--wildchat-dir`; another download is unnecessary.

## 3. Rebuild the published cohort

```bash
python scripts/rebuild_dataset.py \
  --wildchat-dir raw/WildChat-1M/data \
  --output-dir rebuilt/annotated_turns \
  --verify-against data/annotated_turns
```

The output directory must be empty. Omit `--verify-against` when only reconstructing: the reconstruction itself does not read `data/annotated_turns`. Verification compares all 207,047 rows, all 16 fields and their row order. Parquet compression metadata and file bytes may differ; the data values must agree exactly.

The reconstruction joins:

- `data/frozen/selection.parquet`: 473,202 clean-English conversation locators, with Qwen routing, GPT decisions and retained-turn counts.
- `data/frozen/annotations.parquet`: 207,047 retained turn locators, education labels, six-axis annotations and the existing `userid` encoding. It contains no conversation text.
- Raw WildChat: exact user text, the immediately preceding assistant response and conversation-level `timestamp`, `country`, `state` and `model`.

The stored `userid` is the historical analysis encoding of the conversation's modal hashed-IP proxy. Reusing this encoding preserves the original grouping and bootstrap order. No new hash is created during reconstruction.

The frozen decisions trace the original selection:

| Stage | Conversations |
| --- | ---: |
| WildChat source | 837,989 |
| Conversation language is English | 478,498 |
| Redaction, toxicity and nonempty user-text checks | 473,202 |
| Qwen candidate or uncertain routing | 175,234 |
| Valid GPT education-relevance decision | 173,278 |
| Core education or learning-adjacent | 63,682 |
| Final retained annotation cohort | 63,559 |

Among the 63,682 education-positive conversations, 123 have zero retained turns after unresolved annotation failures. A retained conversation can have gaps in user-turn indices: only keys present in `annotations.parquet` enter the final resource. Reconstruction therefore does not label or retain additional messages simply because they appear in a selected conversation.

`data/SOURCE.json` records the source and historical model settings. The historical prompts and schema are in `taxonomy/`, with field names aligned to the paper as `task_dialogue_act` and `boundedness`. These are name-aligned transcriptions; labels and decision rules are unchanged. These support interpretation of the original run; this release does not include an executable workflow for obtaining new Qwen or OpenAI annotations. A new model run would constitute a new annotation version, even with the same prompt.

## 4. Recompute the analysis figures

```bash
python scripts/reproduce.py --results-dir results
```

This reads `data/annotated_turns`, writes nine PNGs to `figures/` and retains aggregate estimates under `results/`. To analyze the reconstructed copy independently, use it in place of `data/annotated_turns` in a separate checkout. Exact reconstruction makes the two input datasets interchangeable.

The descriptive display contains only model and China–United States comparisons; the original 232-test BH family is retained. Feedback models retain their original controls, including the historical region variable. The repeated-use calculation uses the same 200 source proxies and 5,000 whole-source bootstrap samples. See [figures/README.md](figures/README.md) for the paper-to-code mapping.

## Verification scope

The 9 November 2026 preparation compared the complete rebuilt dataset with the release and verified the frozen labels against the historical canonical annotation export. All values agreed, including source text and context. The nine analysis figures were also regenerated, and seven underlying result tables (802 rows) were compared with the paper’s stored results: counts and repeated-use bootstrap results agreed exactly; the largest numerical difference in estimates, intervals or adjusted values was below 8 × 10⁻¹⁴. Known missing boundedness annotations and index gaps remain part of the frozen resource; see [DATA_CARD.md](data/DATA_CARD.md).

The 500/100-turn human-reference workbooks, the 300-conversation education validation sample and their scoring pipelines are not included in this first release. Their validation results are reported in the manuscript. The first-release figure workflow also omits the separate equal-source and operation-count sensitivity reruns reported in the appendices; it reproduces the main overall analyses. The released silver annotations do not substitute for those human references.
