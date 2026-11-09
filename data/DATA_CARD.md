# TBSODS data card

## Resource and unit

207,047 user turns in 63,559 education-related conversations. All six axes are machine annotations from the frozen v8 run. There are 201,525 task-present turns, including 595 without a boundedness label, and 5,522 `no_task` turns. There are 23,647 conversation-level source proxies; they count metadata values, not people.

Each row includes the exact original user message, the preceding assistant response used as annotation context (`previous_assistant_turn`), and the conversation selection label (`education_relevance`). User text and assistant context were verified against local WildChat during the original export. Full history remains recoverable through the shard/row locator. No text normalization or label correction was applied.

## Source and construction

Source: `allenai/WildChat-1M`, default configuration, train split. The manuscript records revision `7d6490e462285cf85d91eabea0f9a954fbddcd1f`; local Parquet filenames and row offsets are preserved against that release layout. The upstream revision is a source version locator, not a newly generated checksum.

The manuscript describes: English-language and redaction filters (473,202 conversations); Qwen3-8B screening; `gpt-4o-mini-2024-07-18` education-relevance classification of candidates/uncertain cases; retention of core-education and learning-adjacent conversations (63,682); then turn annotation and exclusion of 123 conversations with unresolved annotation failures, leaving 63,559. Final conversation categories are 43,375 core-education and 20,184 learning-adjacent conversations. Conversation selection does not imply every retained message is educational, or that its author is a student.

The released cohort and labels come from the historical canonical turn export built on 3 August 2026 from the v8 annotation batch of 30 July 2026. The recorded annotation configuration is `gpt-5.6-luna`, reasoning effort `none`, maximum completion length 512, with no explicit temperature. These strings describe the historical run. Historical prompts and schema are included in `taxonomy/` with publication-aligned field names (`task_dialogue_act`, `boundedness`). The renaming changes no annotation values, label definitions or decision rules.

## Metadata interpretation

`country` and `state` use the original conversation-level IP-derived metadata underlying the paper. They do not establish nationality, culture, ethnicity, native language or residence. `userid` retains the historical paper-analysis encoding of the conversation's modal user-side hashed IP, formerly stored as `proxy_id`. It provides one consistent grouping key; shared networks and changing IPs make it an imperfect person proxy. No new hash is generated.

`timestamp` is the original conversation-level UTC timestamp, defined upstream as the last turn time. It is shared by all rows of a conversation. It does not recover the unavailable individual user-message sending times. Repeated-use ordering follows the paper's convention.

`conversation_id` now directly encodes the source shard filename and row offset. `turn_index` selects a user message within that original conversation. The two columns replace the old internal conversation ID and redundant source fields.

## Known annotation and sequence properties

- 595 task-present null boundedness labels: 594 `other`, one `answer`. These are historical annotation omissions. Null for `no_task` means not applicable; the distinction is determined directly from the task dialogue act label.
- 14,042 task-present turns have no operation label. One `no_task` turn contains `continue`. They are retained unchanged.
- 634 conversations contain gaps in retained raw user-turn indices. Use `turn_index` to detect strict adjacency; retained-turn ranks are computed at analysis time.
- The historical schema allowed nullable boundedness without enforcing its task-present condition. Shape validation does not establish annotation accuracy.

The manuscript's human-reference comparisons are a separate evidence layer; neither all 207,047 annotations nor the codebook examples should be described as independently adjudicated human gold.

## Scope of use

Designed for descriptive study of requested work, constraints, materials, disclosures, expressed stances and observed sequences. The dataset is not a population-representative sample. Observational group differences and subsequent feedback associations do not identify causal model effects or latent satisfaction. Absence of a later observed message does not establish withdrawal.

Text may contain personal or sensitive disclosures despite upstream de-identification. This local package preserves the requested original resource. Any future public release should carry the final author-selected license and the upstream attribution; this package itself has not been published.

## Files

14 Zstandard-compressed Parquet shards, preserving the source shard partition. Each file is below 16 MiB in the prepared export. The resource has no train/test split; all retained rows belong to the analysis cohort.

The frozen selection and annotation layer is supplied separately in `frozen/`. It rebuilds the complete 16-field release when joined to the pinned WildChat source; see [REPRODUCIBILITY.md](../REPRODUCIBILITY.md). The 9 November 2026 reconstruction matched all 207,047 rows and all 16 fields, including original text and context.
