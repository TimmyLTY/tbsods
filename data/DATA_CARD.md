# TBSODS data card

## Resource and unit
There are 201,525 task-present turns, including 595 without a boundedness label, and 5,522 `no_task` turns. There are 23,647 conversation-level source proxies; they count metadata values, not people.

Each row includes the exact original user message, the preceding assistant response used as annotation context (`previous_assistant_turn`), and the conversation selection label (`education_relevance`). Full history remains recoverable through the shard/row locator.

## Source and construction

Source: `allenai/WildChat-1M`, default configuration, train split. The manuscript records revision `7d6490e462285cf85d91eabea0f9a954fbddcd1f`.

The manuscript describes: English-language and redaction filters (473,202 conversations); Qwen3-8B screening; `gpt-4o-mini-2024-07-18` education-relevance classification of candidates/uncertain cases; retention of core-education and learning-adjacent conversations (63,682); then turn annotation and exclusion of 123 conversations with unresolved annotation failures, leaving 63,559. Final conversation categories are 43,375 core-education and 20,184 learning-adjacent conversations. Conversation selection does not imply every retained message is educational, or that its author is a student.


## Scope of use

Designed for descriptive study of requested work, constraints, materials, disclosures, expressed stances and observed sequences. The dataset is not a population-representative sample. Observational group differences and subsequent feedback associations do not identify causal model effects or latent satisfaction. Absence of a later observed message does not establish withdrawal.

Text may contain personal or sensitive disclosures despite upstream de-identification.

## Files

14 Zstandard-compressed Parquet shards, preserving the source shard partition. The resource has no train/test split; all retained rows belong to the analysis cohort.

The frozen selection and annotation layer is supplied separately in `frozen/`. It rebuilds the complete 16-field release when joined to the pinned WildChat source; see [REPRODUCIBILITY.md](../REPRODUCIBILITY.md).
