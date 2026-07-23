# =====================================================================
# MCPH Project Master Makefile (Single Point of Control)
# =====================================================================

SHELL := /bin/bash
REMOTE_USER := researcher
REMOTE_HOST := mcph-cloud-worker
REMOTE_DIR := ~/mcp_project

.PHONY: help sync run-local cloud-deploy pull-results clean

help:
	@echo "Available commands:"
	@echo "  make sync          - Push local WSL code changes to GitHub repository"
	@echo "  make run-local     - Run Nextflow pipeline locally on WSL test subset"
	@echo "  make cloud-deploy  - Push code and trigger headless execution on remote cloud VM"
	@echo "  make pull-results  - Download final variants and reports from cloud storage"
	@echo "  make clean         - Remove temporary files and local cache"

sync:
	@echo "==> Syncing code with GitHub..."
	git add .
	@git diff-index --quiet HEAD || git commit -m "Auto-sync from WSL single-point command center"
	git push origin main

cloud-deploy: sync
	@echo "==> Triggering remote cloud execution..."
	gcloud compute ssh $(REMOTE_USER)@$(REMOTE_HOST) --command="cd $(REMOTE_DIR) && git pull && nextflow run main.nf -profile gcp"

pull-results:
	@echo "==> Pulling results from cloud storage bucket..."
	gsutil -m rsync -r gs://my-mcph-bucket/05_variants/ ./05_variants/
	gsutil -m rsync -r gs://my-mcph-bucket/07_reports/ ./07_reports/
	@echo "==> Retrieval complete. Check 05_variants/ and 07_reports/"

run-local:
	@echo "==> Executing pipeline locally via Nextflow..."
	nextflow run main.nf -profile standard

clean:
	@echo "==> Cleaning up intermediate junk files..."
	rm -rf .nextflow* work/