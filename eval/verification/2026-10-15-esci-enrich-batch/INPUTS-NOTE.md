# 证据文件处理说明

各轮目录里的 `inputs.jsonl` 是增强脚本写出的输入副本，与 `eval/verification/2026-10-14-t2-input-plan/enrichment-inputs.jsonl` 逐字节相同（`cmp` 逐一核对，共 7 份：本目录 run-1 至 run-5，`../2026-10-15-esci-enrich/` 的 run-1、run-2）。
为避免仓库里重复保存 7 份各 18.9MB 的相同内容，提交前删除了这些副本，各轮 `manifest.json` 中的 `inputs_fingerprint` 仍可核对输入。
各轮 `requests.jsonl`（原始请求与响应账本）以 gzip 无损压缩为 `requests.jsonl.gz`，内容未改。
