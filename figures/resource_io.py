"""Read the compact release and derive columns needed by the paper figures."""
import pandas as pd


def read_paper_turns(path, columns):
    derived = {'observed_rank', 'strict_next', 'n_operations'}
    stored = ['userid' if c == 'proxy_id' else c for c in columns if c not in derived]
    if {'observed_rank', 'strict_next'} & set(columns):
        stored += ['conversation_id', 'turn_index']
    if 'n_operations' in columns:
        stored.append('operations')
    frame = pd.read_parquet(path, columns=list(dict.fromkeys(stored)))
    if 'proxy_id' in columns:
        frame = frame.rename(columns={'userid': 'proxy_id'})
    if {'observed_rank', 'strict_next'} & set(columns):
        ordered = frame.sort_values(['conversation_id', 'turn_index'])
        groups = ordered.groupby('conversation_id', sort=False)
        if 'observed_rank' in columns:
            frame['observed_rank'] = groups.cumcount().reindex(frame.index)
        if 'strict_next' in columns:
            frame['strict_next'] = groups.turn_index.shift(-1).eq(ordered.turn_index + 1).reindex(frame.index)
    if 'n_operations' in columns:
        frame['n_operations'] = frame.operations.map(len)
    if 'country' in frame:
        frame['country'] = frame.country.fillna('<missing>').replace('', '<missing>')
    return frame[columns]
