"""顺序测量历史基线；每档独立原始 CSV、服务日志与资源采样。"""
import json
from pathlib import Path
import subprocess
import time

root = Path.cwd()
output = Path(__file__).resolve().parent
for users in [1, 2, 4, 8]:
    stage = output / f'users-{users}'
    stage.mkdir()
    command = ['/tmp/voyacart-loadtest-venv/bin/locust', '-f', 'scripts/loadtest/locustfile.py',
        '--headless', '--host', 'http://127.0.0.1:8084', '--users', str(users), '--spawn-rate', str(users),
        '--run-time', '45s', '--stop-timeout', '180', '--agui-output', str(stage),
        '--csv', str(stage/'locust'), '--csv-full-history']
    started = time.time()
    (stage/'command.json').write_text(json.dumps(command, indent=2)+'\n')
    with (stage/'locust.log').open('w') as log, (stage/'resources.jsonl').open('w') as resources:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        while process.poll() is None:
            sample = subprocess.run(['docker','stats','--no-stream','--format','{{json .}}',
                'voyacart-load-baseline','voyacart-load-mock'], capture_output=True, text=True, check=True)
            resources.write(json.dumps({'time':time.time(), 'containers':[json.loads(line) for line in sample.stdout.splitlines()]})+'\n')
            resources.flush()
            time.sleep(2)
    (stage/'exit.json').write_text(json.dumps({'exit_code':process.returncode,'started_at':started,'finished_at':time.time()})+'\n')
    with (stage/'analysis.log').open('w') as log:
        subprocess.run([str(root/'.venv/bin/python'),'scripts/loadtest/analyze.py',str(stage)],
            stdout=log, stderr=subprocess.STDOUT, check=True)
    with (stage/'backend.log').open('w') as log:
        subprocess.run(['docker','logs','--since',str(int(started)),'voyacart-load-baseline'],
            stdout=log, stderr=subprocess.STDOUT, check=True)
    print(json.dumps({'users':users,'exit':process.returncode,'report':json.loads((stage/'report.json').read_text())}), flush=True)
