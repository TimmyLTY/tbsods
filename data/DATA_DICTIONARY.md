# Data dictionary

One row is one annotated user message. The release has **16 fields**. Empty arrays mean no label was selected.

| Field | Type | Meaning |
| --- | --- | --- |
| `conversation_id` | string | Original WildChat shard filename and zero-based row, joined by `:`; e.g. `train-00000-of-00014.parquet:21442` |
| `turn_index` | int64 | Zero-based index among **all original user messages** in that conversation; gaps in the retained subset remain |
| `current_user_turn` | string | Exact original user text |
| `previous_assistant_turn` | nullable string | Immediately preceding assistant response used as annotation context; null when absent |
| `education_relevance` | string | Conversation-level education-selection label: `core_education` or `learning_adjacent` |
| `task_dialogue_act` | string | **Task dialogue act**: one of `answer`, `create`, `revise`, `other`, `no_task` |
| `boundedness` | nullable string | **Boundedness**: `closed`, `guided`, `open`; null is not applicable for `no_task`, otherwise missing |
| `support` | list of strings | Zero or more of two support labels |
| `operations` | list of strings | Zero or more of 29 requested operations |
| `disclosures` | list of strings | Zero or more of nine disclosures |
| `stances` | list of strings | Zero or more of ten interpersonal stances |
| `timestamp` | timestamp[us, UTC] | Original conversation-level last-turn time; not the current user message's sending time |
| `country` | nullable string | Original conversation-level IP-derived country used in the paper |
| `state` | nullable string | Original conversation-level IP-derived state/region |
| `userid` | string | Existing paper-analysis encoding of the modal conversation-level hashed-IP proxy; retained unchanged |
| `model` | string | Original conversation model version |

`(conversation_id, turn_index)` uniquely identifies a released message. The shard/row locator refers to the `allenai/WildChat-1M` train split at revision `7d6490e462285cf85d91eabea0f9a954fbddcd1f`. Pin this revision when retrieving the source.

`userid` preserves the paper's original source grouping and bootstrap order. It is not an account or a verified person. All five metadata fields use one consistent **conversation-level** convention.

The full 58-label inventory and definitions are in `../taxonomy/taxonomy_definitions.json`. Labels such as `other` must be qualified by axis. The 595 task-present null boundedness labels remain unchanged; detect them with `task_dialogue_act != "no_task"` and `boundedness is null`.

## Retrieve the original conversation and context

```bash
python scripts/lookup_source.py train-00000-of-00014.parquet:21442 \
  --wildchat-dir /path/to/WildChat-1M/data \
  --output original_conversation.json
```

The script retrieves the source row and verifies a released user message against its original text. In the returned `conversation` array, select user-role messages and index by `turn_index`. The original mixed-role array also provides the preceding assistant response used for annotation. That response is also retained in `previous_assistant_turn` for direct reuse without downloading the full source.

`figures/resource_io.py` computes retained-turn rank, strict adjacency and operation counts when the figure scripts request them. They are not stored as dataset columns.

## Frozen reconstruction files

`frozen/annotations.parquet` has one row per retained user turn and ten columns: `conversation_id`, `turn_index`, `education_relevance`, the six annotation axes, and `userid`. It contains no source text or assistant context.

`frozen/selection.parquet` has one row per clean-English conversation (473,202 rows):

| Field | Meaning |
| --- | --- |
| `conversation_id` | The same source shard:row locator used in the turn resource |
| `qwen_label` | Historical first-stage screening label |
| `qwen_valid` | Whether the original Qwen result was valid |
| `send_to_gpt` | Historical routing decision, including uncertain/invalid cases |
| `education_relevance` | GPT conversation label; null when no valid label was retained |
| `gpt_valid` | Validity of the GPT result; null if not routed to GPT |
| `retained_turns` | Number of rows in the final turn resource; zero for excluded conversations |

A positive education label alone does not determine inclusion: 123 education-positive conversations have zero retained turns after annotation failures. The per-turn keys in `annotations.parquet` determine the exact retained messages. See [REPRODUCIBILITY.md](../REPRODUCIBILITY.md) for commands.
