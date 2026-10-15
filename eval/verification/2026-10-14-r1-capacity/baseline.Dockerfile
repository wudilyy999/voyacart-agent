FROM voyacart-runtime:r1
RUN rm -rf /app/app
COPY app /app/app
COPY configs /app/configs
COPY knowledge /app/knowledge
COPY data/catalog-v3.jsonl /app/catalog/catalog-v3.jsonl
