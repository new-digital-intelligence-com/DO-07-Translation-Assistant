#!/usr/bin/env python3
"""Sync index — what was last propagated, from which source state, into which variant.

    sync_index.py --path INDEX status  --family F
    sync_index.py --path INDEX record  --family F --variant V --source-state HASH
                                       [--segments N] [--note TEXT] [--date YYYY-MM-DD]
    sync_index.py --path INDEX freeze  --family F --variant V --reason TEXT
    sync_index.py --path INDEX unfreeze --family F --variant V
    sync_index.py --path INDEX hash FILE...

Nothing in a document store records what a previous run already handled. Without this,
every run either re-proposes work it has done or, worse, treats an untouched variant as
current because the source happens to look familiar.

`--path` takes a directory (the store) or a single file. Given a directory it reads every
`.jsonl` in it and appends to one file per family, so a store only ever gains files and
never needs an existing one replaced — the same constraint the ledger works under, for the
same reason: a connector that can create a file but not update one cannot append.

Append-only. A freeze is a new record, not an edit of an old one, so the history of who
froze what and when survives.
"""
import argparse, hashlib, json, sys
from datetime import date
from pathlib import Path


def is_store(p: Path) -> bool:
    return p.is_dir() or (not p.suffix and not p.exists()) or str(p).endswith('/')


def family_file(path: Path, family: str) -> Path:
    if not is_store(path):
        return path
    path.mkdir(parents=True, exist_ok=True)
    safe = ''.join(c if c.isalnum() or c in '-_' else '-' for c in family)
    return path / f'{safe}.jsonl'


def read_all(path: Path) -> list:
    files = sorted(path.glob('*.jsonl')) if is_store(path) and path.exists() else \
            ([path] if path.exists() else [])
    out = []
    for f in files:
        for line in f.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append(path: Path, family: str, rec: dict) -> Path:
    f = family_file(path, family)
    with f.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return f


def state_of(records: list, family: str) -> dict:
    """Latest record wins per (variant, kind). Append-only, so order is history."""
    synced, frozen = {}, {}
    for r in records:
        if r.get('family') != family:
            continue
        v = r.get('variant')
        if r.get('op') == 'sync':
            synced[v] = r
        elif r.get('op') == 'freeze':
            frozen[v] = r
        elif r.get('op') == 'unfreeze':
            frozen.pop(v, None)
    return {'synced': synced, 'frozen': frozen}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', default='index')
    sub = ap.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('status'); s.add_argument('--family', required=True)

    r = sub.add_parser('record')
    r.add_argument('--family', required=True)
    r.add_argument('--variant', required=True)
    r.add_argument('--source-state', required=True,
                   help='fingerprint of the source at the moment this variant was brought level')
    r.add_argument('--variant-state', default=None)
    r.add_argument('--segments', type=int, default=None)
    r.add_argument('--note', default='')
    r.add_argument('--date', default=None)

    f = sub.add_parser('freeze')
    f.add_argument('--family', required=True); f.add_argument('--variant', required=True)
    f.add_argument('--reason', required=True)

    u = sub.add_parser('unfreeze')
    u.add_argument('--family', required=True); u.add_argument('--variant', required=True)

    h = sub.add_parser('hash'); h.add_argument('files', nargs='+')

    a = ap.parse_args()
    path = Path(a.path)

    if a.cmd == 'hash':
        for name in a.files:
            p = Path(name)
            if not p.exists():
                sys.exit(f'no such file: {p}')
            print(f'{sha(p)}  {p}')
        return

    if a.cmd == 'record':
        rec = {'op': 'sync', 'date': a.date or date.today().isoformat(),
               'family': a.family, 'variant': a.variant,
               'source_state': a.source_state, 'variant_state': a.variant_state,
               'segments': a.segments, 'note': a.note}
        wrote = append(path, a.family, rec)
        print(json.dumps({'recorded': rec, 'upload_this_file': str(wrote)}, indent=2))
        return

    if a.cmd in ('freeze', 'unfreeze'):
        rec = {'op': a.cmd, 'date': date.today().isoformat(),
               'family': a.family, 'variant': a.variant}
        if a.cmd == 'freeze':
            rec['reason'] = a.reason
        wrote = append(path, a.family, rec)
        print(json.dumps({'recorded': rec, 'upload_this_file': str(wrote)}, indent=2))
        return

    st = state_of(read_all(path), a.family)
    if not st['synced'] and not st['frozen']:
        print(json.dumps({
            'family': a.family, 'first_sync': True, 'variants': {},
            'say_this': 'No index entry for this family. This is a first sync: there is no '
                        'previous state to diff against and no conflict to detect. Say so '
                        'before proposing anything.'}, indent=2))
        return

    variants = {}
    for v, rec in st['synced'].items():
        variants[v] = {'last_synced': rec['date'], 'source_state': rec['source_state'],
                       'segments': rec.get('segments'), 'note': rec.get('note', '')}
    for v, rec in st['frozen'].items():
        variants.setdefault(v, {})
        variants[v]['frozen'] = True
        variants[v]['frozen_reason'] = rec.get('reason', '')
        variants[v]['frozen_on'] = rec['date']

    print(json.dumps({
        'family': a.family, 'first_sync': False, 'variants': variants,
        'frozen': sorted(st['frozen']),
        'read_it': 'Compare each variant\'s recorded source_state against the source now. '
                   'Equal means in sync. Different means the source moved. A frozen variant '
                   'is reported behind and never worked on.'}, indent=2))


if __name__ == '__main__':
    main()
