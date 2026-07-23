.PHONY: all run push ai clean

all: run

run:
	@echo "[*] Executing MCP bioinformatics pipeline..."
	bash run_mcph_pipeline.sh

push:
	@echo "[*] Syncing workspace checkpoint with GitHub..."
	git add .
	git commit -m "Auto-checkpoint: MCP pipeline execution completed safely"
	git push origin main

ai:
	@python3 agents/bio_agent.py "$(prompt)"

clean:
	@echo "[*] Cleaning temporary files..."
	rm -rf .snakemake/ temp/
