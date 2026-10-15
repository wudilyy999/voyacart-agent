#!/bin/bash
# 批量增强续跑驱动：网关 5xx、断网等原因中止时自动续跑，每轮证据单独存为 run-N，编号接着已有目录往后排。
# 连续 5 轮缓存都没有新增才停止，每次等待 60 秒（覆盖短时断网）。
cd "$(dirname "$0")/../../.." || exit 1
D=eval/verification/2026-10-15-esci-enrich-batch
C=data/esci/enrichment-batch-v1.jsonl
export LLM_MAX_CONCURRENCY=16 LLM_MIN_INTERVAL_SECONDS=0.2
rows() { [ -f "$C" ] && wc -l < "$C" | tr -d ' ' || echo 0; }
n=1; while [ -e "$D/run-$n" ]; do n=$((n+1)); done
stalls=0
while true; do
  before=$(rows)
  echo "$(date '+%F %T') run-$n start cache_rows=$before"
  if .venv/bin/python -m scripts.esci.enrich_catalog --enrich --prepared eval/verification/2026-10-14-t2-input-plan --output "$D/run-$n" > "$D/run-$n.log" 2>&1; then
    echo "$(date '+%F %T') run-$n completed cache_rows=$(rows)"; break
  fi
  after=$(rows)
  echo "$(date '+%F %T') run-$n exited non-zero cache_rows=$after"
  if [ "$after" -le "$before" ]; then stalls=$((stalls+1)); else stalls=0; fi
  if [ "$stalls" -ge 5 ]; then echo "连续 5 轮没有新增缓存，停止"; break; fi
  n=$((n+1)); sleep 60
done
