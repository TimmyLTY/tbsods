"""Recompute the paper figures from the released Parquet data; write PNG only."""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(results_dir):
    env = dict(os.environ, TBSODS_RESULTS_DIR=str(results_dir), MPLBACKEND='Agg',
               OPENBLAS_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               OMP_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    for script in [
        'descriptive/analyze.py', 'descriptive/plot.py',
        'feedback/run_feedback.py', 'feedback/fit_all_overall.py', 'feedback/plot.py',
        'boundedness/run_boundedness.py', 'boundedness/plot.py',
        'longitudinal/run_analysis.py', 'longitudinal/plot.py',
    ]:
        print('Running', script, flush=True)
        subprocess.run([sys.executable, str(ROOT/'figures'/script)],
                       cwd=ROOT, env=env, check=True)
    print('Reproduced nine PNG figures in figures/.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir', type=Path, help='Keep the computed tables in this directory; otherwise use temporary files')
    args = parser.parse_args()
    if args.results_dir:
        args.results_dir.mkdir(parents=True, exist_ok=True)
        run(args.results_dir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='tbsods-figures-') as temporary:
            run(temporary)


if __name__ == '__main__':
    main()
