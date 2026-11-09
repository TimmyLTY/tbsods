"""Rebuild released turns from pinned WildChat files and frozen annotations."""
from pathlib import Path
import argparse
import json
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    ('conversation_id', pa.string()), ('turn_index', pa.int64()),
    ('current_user_turn', pa.string()), ('previous_assistant_turn', pa.string()),
    ('education_relevance', pa.string()), ('task_dialogue_act', pa.string()),
    ('boundedness', pa.string()),
    *[(name, pa.list_(pa.string())) for name in ['support', 'operations', 'disclosures', 'stances']],
    ('timestamp', pa.timestamp('us', tz='UTC')), ('country', pa.string()),
    ('state', pa.string()), ('userid', pa.string()), ('model', pa.string()),
]
SCHEMA = pa.schema(FIELDS)


def rebuild(raw_dir, output_dir, verify_against=None):
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError('Choose an empty output directory; existing data are not overwritten.')
    source = json.loads((ROOT / 'data/SOURCE.json').read_text())
    annotations = pq.read_table(ROOT / 'data/frozen/annotations.parquet').to_pylist()
    selection = {r['conversation_id']: r for r in pq.read_table(ROOT / 'data/frozen/selection.parquet').to_pylist() if r['retained_turns']}
    by_shard = {}
    counts = {}
    for row in annotations:
        cid = row['conversation_id']
        decision = selection[cid]
        assert decision['gpt_valid'] and decision['education_relevance'] == row['education_relevance']
        assert decision['education_relevance'] in ('core_education', 'learning_adjacent')
        shard, _ = cid.rsplit(':', 1)
        by_shard.setdefault(shard, []).append(row)
        counts[cid] = counts.get(cid, 0) + 1
    assert counts == {cid: r['retained_turns'] for cid, r in selection.items()}
    assert len(annotations) == source['released_turns']
    assert len(counts) == source['released_conversations']
    actual_rows = sum(pq.ParquetFile(raw_dir / name).metadata.num_rows for name in by_shard)
    assert actual_rows == source['source_conversations'], 'Use the pinned WildChat snapshot.'
    output_dir.mkdir(parents=True, exist_ok=True)
    verified = 0
    for shard, frozen in sorted(by_shard.items()):
        indices = sorted({int(r['conversation_id'].rsplit(':', 1)[1]) for r in frozen})
        table = pq.read_table(raw_dir / shard, columns=['conversation', 'timestamp', 'country', 'state', 'model'])
        raw = dict(zip(indices, table.take(indices).to_pylist()))
        del table
        user_turns = {}
        for index, conversation in raw.items():
            users = []
            previous = None
            for message in conversation['conversation']:
                if message['role'] == 'user':
                    users.append((message['content'], previous))
                previous = message['content'] if message['role'] == 'assistant' else None
            user_turns[index] = users
        rows = []
        for labels in frozen:
            index = int(labels['conversation_id'].rsplit(':', 1)[1])
            text, context = user_turns[index][labels['turn_index']]
            rows.append(dict(labels, current_user_turn=text, previous_assistant_turn=context,
                             **{col: raw[index][col] for col in ['timestamp', 'country', 'state', 'model']}))
        rebuilt = pa.Table.from_pylist(rows, schema=SCHEMA)
        filename = shard.replace('train-', 'turns-')
        if verify_against is not None:
            expected = pq.read_table(verify_against / filename).cast(SCHEMA).replace_schema_metadata(None)
            if not rebuilt.equals(expected, check_metadata=False):
                fields = [name for name in SCHEMA.names if not rebuilt[name].equals(expected[name])]
                raise ValueError(f'{filename}: rebuilt values differ in {fields}')
            verified += len(rows)
        pq.write_table(rebuilt, output_dir / filename, compression='zstd')
        print(f'{filename}: {len(rows):,} turns', flush=True)
    print(f'Rebuilt {len(annotations):,} turns in {len(selection):,} conversations.')
    if verify_against is not None:
        print(f'Verified all {verified:,} rows and all 16 fields against the release.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wildchat-dir', type=Path, required=True, help='Directory containing the 14 pinned train-*.parquet files')
    parser.add_argument('--output-dir', type=Path, required=True, help='Empty destination for rebuilt turns-*.parquet files')
    parser.add_argument('--verify-against', type=Path, help='Optional released annotated_turns directory for exact value comparison')
    args = parser.parse_args()
    rebuild(args.wildchat_dir, args.output_dir, args.verify_against)


if __name__ == '__main__':
    main()
