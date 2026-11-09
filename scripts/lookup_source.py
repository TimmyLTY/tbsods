"""Recover the original WildChat conversation using the compact conversation ID."""
from pathlib import Path
import argparse
import json
from datetime import datetime
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('conversation_id', help='Source shard filename:zero-based row, as stored in the release')
    parser.add_argument('--wildchat-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    anchors = pq.read_table(ROOT/'data/annotated_turns',
                            columns=['turn_index', 'current_user_turn'],
                            filters=[('conversation_id', '=', args.conversation_id)]).to_pylist()
    if not anchors:
        parser.error('conversation_id not found in the release')
    shard, row = args.conversation_id.rsplit(':', 1)
    row = int(row)
    parquet = pq.ParquetFile(args.wildchat_dir/shard)
    offset = 0
    for group in range(parquet.num_row_groups):
        count = parquet.metadata.row_group(group).num_rows
        if offset <= row < offset + count:
            raw = parquet.read_row_group(group).slice(row-offset, 1).to_pylist()[0]
            users = [m for m in raw['conversation'] if m['role'] == 'user']
            anchor = anchors[0]
            assert users[anchor['turn_index']]['content'] == anchor['current_user_turn'], 'Source revision does not match the release'
            args.output.write_text(json.dumps(raw, ensure_ascii=False, indent=2,
                default=lambda v: v.isoformat() if isinstance(v, datetime) else str(v))+'\n')
            print('Wrote', args.output)
            return
        offset += count
    raise ValueError('Source row is outside the shard')


if __name__ == '__main__':
    main()
