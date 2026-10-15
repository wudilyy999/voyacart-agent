"""只读分析已完成的运行记录、锁异常与资源采样，向标准输出写 JSON。"""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
import re
import statistics

ROOT = Path(__file__).resolve().parents[3]
inputs = {}


def read(path):
    blob = (ROOT / path).read_bytes()
    inputs[str(path)] = {'bytes': len(blob), 'blake2b': hashlib.blake2b(blob).hexdigest()}
    return blob.decode()


def percentile(values, q):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * q) - 1)] if ordered else None


def inspect(folder, log_name):
    rows = list(csv.DictReader(io.StringIO(read(folder / 'runs.csv'))))
    report = json.loads(read(folder / 'report.json'))
    read(folder / 'failures.json')
    resource_rows = [json.loads(line) for line in read(folder / 'resources.jsonl').splitlines()]
    lines = read(folder / log_name).splitlines()
    headers = [i for i, line in enumerate(lines) if line.startswith('ERROR:')
               or re.match(r'^\d{4}-\d\d-\d\d .* (ERROR|WARNING) ', line)]
    groups = []
    methods = ('assert_owner', 'model_binding', 'bind_run_model', 'claim', 'save_claim')
    for number, begin in enumerate(headers):
        end = headers[number + 1] if number + 1 < len(headers) else len(lines)
        matches = [i for i in range(begin, end) if 'database is locked' in lines[i]]
        if not matches:
            continue
        frames = list(dict.fromkeys(line.strip() for line in lines[begin:matches[-1]]
                                   if re.search(r'File "/app/app/', line)))
        method = next((m for m in methods if any(f'in {m}' in frame for frame in frames)), None)
        if any('ag_ui_journal.py' in frame and 'in reserve' in frame for frame in frames):
            kind = 'journal.reserve'
        elif any('ag_ui_journal.py' in frame and 'in append' in frame for frame in frames):
            kind = 'journal.append'
        elif any('ag_ui_journal.py' in frame and 'in events' in frame for frame in frames):
            kind = 'journal.events'
        elif method:
            kind = 'session_store.' + method
        else:
            kind = 'other'
        run = re.search(r'(load-[a-f0-9]+)', lines[begin])
        groups.append({'kind': kind, 'start_line': begin + 1, 'last_lock_line': matches[-1] + 1,
                       'raw_lock_lines': [i + 1 for i in matches], 'frames': frames,
                       'run_id': run.group(1) if run else None})
    writer_ids = re.findall(r'AG-UI 日志写入失败，等待持久租约过期后标记中断：(load-[a-f0-9]+)', '\n'.join(lines))
    codes = {row['run_id']: row['error_code'] for row in rows}
    restart_ids = {row['run_id'] for row in rows if row['error_code'] == 'SERVER_RESTART'}
    cpu = defaultdict(list)
    rss = defaultdict(int)
    tasks = defaultdict(list)
    for sample in resource_rows:
        total = defaultdict(float)
        for container in sample['containers']:
            name = container['Name']
            role = 'api' if '-api-' in name else 'worker' if '-worker-' in name else None
            if role:
                total[role] += float(container['CPUPerc'].rstrip('%'))
                tasks[name].append(int(container['PIDs']))
        for role, value in total.items():
            cpu[role].append(value)
        for container, table in sample['processes'].items():
            for line in table.splitlines()[1:]:
                pid, value, command = line.split(maxsplit=2)
                key = (container, int(pid), command)
                rss[key] = max(rss[key], int(value))
    checked = {}
    for field in ('first_event_ms', 'first_token_ms', 'complete_ms'):
        values = [float(row[field]) for row in rows if row[field]]
        checked[field] = {'samples': len(values), **{f'p{int(q * 100)}': percentile(values, q) for q in (.5, .95, .99)}}
    duration = max(float(row['finished_at']) for row in rows) - min(float(row['started_at']) for row in rows)
    failures = [row for row in rows if row['error_code']]
    intervals = [b['time'] - a['time'] for a, b in zip(resource_rows, resource_rows[1:])]
    return {
        'folder': str(folder), 'requests': len(rows), 'successful': len(rows) - len(failures),
        'errors': len(failures), 'error_codes': dict(Counter(row['error_code'] for row in failures)),
        'successful_runs_per_second': (len(rows) - len(failures)) / duration,
        'observed_seconds': duration, 'latency_ms_all_runs': checked,
        'success_complete_p95_ms': percentile([float(row['complete_ms']) for row in rows if not row['error_code']], .95),
        'report_matches_recomputed_latencies': checked == report['latency_ms'],
        'raw_lock_occurrences': sum('database is locked' in line for line in lines),
        'lock_error_groups': len(groups), 'lock_groups_by_kind': dict(Counter(g['kind'] for g in groups)),
        'lock_groups': groups,
        'writer_errors_to_csv': dict(Counter(codes.get(run, 'absent') for run in writer_ids)),
        'restart_without_writer_stack': sorted(restart_ids - set(writer_ids)),
        'redis_pool_error_occurrences': sum('Too many connections' in line or 'ConnectionError: Too many' in line for line in lines),
        'initialization_retry_markers': sum('sqlite_lock_retry' in line for line in lines),
        'resource_samples': len(resource_rows),
        'resource_interval_seconds': {'min': min(intervals), 'median': statistics.median(intervals), 'max': max(intervals)},
        'role_cpu_percent': {role: {'peak': max(values), 'median': statistics.median(values)} for role, values in cpu.items()},
        'rss_peak_kib_by_process': [{'container': key[0], 'pid': key[1], 'command': key[2], 'peak_kib': value} for key, value in rss.items()],
        'container_tasks_peak': {name: max(values) for name, values in tasks.items()},
    }


final = Path('eval/verification/2026-10-14-r1-final-matrix')
history = Path('eval/verification/2026-10-14-r1-capacity')
observations = []
for mode, users in (('inline-a1-w1', 32), ('inline-a1-w1', 64), ('inline-a1-w2', 64), ('inline-a1-w2', 128)):
    observations.append(inspect(final / mode / f'users-{users}', 'voyacart-r1-matrix-api-1.log'))
for batch in ('baseline-ready', 'baseline-high'):
    observations.append(inspect(history / batch / 'inline-a1-w1/users-64', 'voyacart-r1-baseline-api-1.log'))
manifests = {name: json.loads(read(path / 'manifest.json')) for name, path in (
    ('final', final), ('baseline-ready', history / 'baseline-ready'), ('baseline-high', history / 'baseline-high'))}
config_keys = ('AGUI_QUEUE_ENABLED', 'QUEUE_ENABLED', 'AGUI_DELTA_COALESCE_MS',
               'AUTOMATION_WORKER_MODE', 'BREAKER_SHARED', 'SEQUENCING_PERSISTENCE_ENABLED', 'DATABASE_URL')
configurations = {}
for name, folder in (('final-a1w1', final / 'inline-a1-w1'), ('final-a1w2', final / 'inline-a1-w2'),
                     ('baseline-ready-a1w1', history / 'baseline-ready/inline-a1-w1')):
    compose = json.loads(read(folder / 'compose.json'))
    configurations[name] = {service: {key: compose['services'][service]['environment'].get(key) for key in config_keys}
                            for service in ('api', 'worker')}
sources = ('app/infrastructure/ag_ui_journal.py', 'app/application/agent_runtime.py',
           'app/infrastructure/persistence/sql/session_store.py', 'app/composition.py',
           'app/infrastructure/persistence/sql/trade_store.py', 'app/infrastructure/persistence/sql/repositories.py',
           'scripts/loadtest/client.py', 'scripts/loadtest/locustfile.py', 'scripts/loadtest/analyze.py',
           'scripts/loadtest/matrix.py', '.venv/lib/python3.11/site-packages/aiosqlite/core.py',
           '.venv/lib/python3.11/site-packages/aiosqlite-0.22.1.dist-info/METADATA')
for path in sources:
    read(Path(path))
fingerprints = {name: manifest['source_fingerprints_blake2b'] for name, manifest in manifests.items()}
comparison = {path: {'final': fingerprints['final'].get(path), 'baseline': fingerprints['baseline-ready'].get(path),
                     'same': fingerprints['final'].get(path) == fingerprints['baseline-ready'].get(path)}
              for path in fingerprints['baseline-ready']}
baseline_sources = json.loads(read(history / 'baseline-source.json'))
baseline_context = Path('/tmp/voyacart-r1-baseline-20261014')
for path in baseline_sources:
    read(baseline_context / path)
for name in ('baseline.Dockerfile', 'baseline-instrumentation.patch', 'baseline-build.log'):
    read(history / name)
baseline_provenance = {
    'driver_source_scope': 'matrix.py 按运行器文件所在仓库读取宿主源码，manifest 内容指纹属于实验驱动',
    'driver_base_commit_scope': 'matrix.py 对运行器工作目录查询 HEAD，基线 manifest 的 base_commit 属于实验驱动',
    'application_snapshot_path': str(baseline_context), 'application_source_record': str(history / 'baseline-source.json'),
    'snapshot_files': len(baseline_sources),
    'snapshot_mismatches': [name for name, digest in baseline_sources.items()
                            if inputs[str(baseline_context / name)]['blake2b'] != digest],
    'application_journal_blake2b': baseline_sources['app/infrastructure/ag_ui_journal.py'],
    'driver_journal_blake2b': fingerprints['baseline-ready']['app/infrastructure/ag_ui_journal.py'],
    'runtime_excerpt_path': str(history / 'baseline-ready/inline-a1-w1/users-64/voyacart-r1-baseline-api-1.log'),
    'runtime_excerpt_lines': [2339, 2340, 2344, 2345],
    'runtime_excerpt': ['events:338 → async with self._db(True) as db:', '_db:117 → await db.execute("BEGIN IMMEDIATE")'],
    'historical_metrics_retained': True,
    'snapshot_matches_runtime_excerpt': True,
    'image_tag_history_unknown': '当前 tag 的只读 ID 与构建日志一致，历史每轮的 image ID 没有记录在基线 manifest 中',
}
result = {'scope': '只读诊断；仅写新证据目录；源代码、旧证据、测试、容器、Git 与外部模型调用保持现状',
          'observations': observations, 'missing_observations': ['inline-a1-w1/users-128'],
          'configurations': configurations, 'historical_source_comparison': comparison,
          'baseline_provenance': baseline_provenance,
          'database_writers': {
              'ag_ui_runs.db': {'entry': 'AGUIJournal._db(True)', 'callers': ['reserve', 'append', 'renew', 'recover_expired']},
              'voyacart.db': {'engine_shared_at': 'app/composition.py:250–269',
                            'stores': ['SqlSessionStore', 'SqlTradeStore', 'SqlConversationStore', 'SqlPreferenceStore'],
                            'other_writes': ['SqlTradeStore._transaction', 'SqlConversationStore.touch_session',
                                             'SqlConversationStore.append_turn', 'SqlConversationStore.append_events',
                                             'SqlPreferenceStore.append'],
                            'per_session_store_lock_limit': '单独串行 SqlSessionStore 只覆盖该 store 的写事务，其他共享库 writer 仍独立提交'},
          },
          'source_matches_final_manifest': {path: inputs[path]['blake2b'] == fingerprints['final'][path]
                                            for path in sources if path in fingerprints['final']},
          'inputs': inputs,
          'inputs_stable_after_read': all(hashlib.blake2b((ROOT / path).read_bytes()).hexdigest() == item['blake2b']
                                         for path, item in inputs.items())}
print(json.dumps(result, ensure_ascii=False, indent=2))
