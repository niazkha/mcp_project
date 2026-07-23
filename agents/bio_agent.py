import os
import sys
import subprocess
import psutil

def check_resources():
    mem = psutil.virtual_memory()
    print(f"Available RAM: {mem.available / (1024**3):.2f} GB ({mem.percent}% used)")
    if mem.percent > 85:
        print("WARNING: Low memory condition detected. Deferring to low-resource mode.")
        return False
    return True

def run_cmd(command):
    if not check_resources():
        raise RuntimeError("Task aborted due to low system memory to protect environment stability.")
    print(f"-> Executing: {command}")
    res = subprocess.run(command, shell=True, text=True, capture_output=True)
    if res.returncode != 0:
        print(f"Error output:\n{res.stderr}")
        raise RuntimeError(f"Command failed: {command}")
    print(res.stdout)

def main():
    print("--- BIO AGENT: Autonomous Pipeline Initialization ---")
    
    # 1. Ensure directories exist
    os.makedirs("01_raw_data", exist_ok=True)
    os.makedirs("03_reference", exist_ok=True)
    os.makedirs("04_alignments", exist_ok=True)
    os.makedirs("05_variants", exist_ok=True)
    os.makedirs("06_annotation", exist_ok=True)
    os.makedirs("07_reports", exist_ok=True)

    # 2. Check and fetch reference genome if missing
    ref_path = "03_reference/reference.fa"
    if not os.path.exists(ref_path):
        print("[*] Reference genome not found. Downloading reference sequence...")
        run_cmd(f"curl -o {ref_path}.gz https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz")
        run_cmd(f"gunzip {ref_path}.gz")

    # 3. Index reference if not indexed
    if not os.path.exists(f"{ref_path}.bwt"):
        print("[*] Indexing reference genome for BWA...")
        run_cmd(f"bwa index {ref_path}")
    if not os.path.exists(f"{ref_path}.fai"):
        print("[*] Indexing reference genome with samtools...")
        run_cmd(f"samtools faidx {ref_path}")

    # 4. Fetch raw data if missing
    fastq1 = "01_raw_data/SRR1972739_1.fastq"
    if not os.path.exists(fastq1):
        print("[*] Fetching raw sequencing data...")
        run_cmd("fasterq-dump --split-files --outdir 01_raw_data/ SRR1972739")

    # 5. Run Alignment & Variant Calling
    print("[*] Running alignment and variant calling workflow...")
    run_cmd(f"bwa mem {ref_path} 01_raw_data/SRR1972739_1.fastq 01_raw_data/SRR1972739_2.fastq | samtools view -Sb - > 04_alignments/aligned.bam")
    run_cmd("samtools sort 04_alignments/aligned.bam -o 04_alignments/sorted.bam")
    run_cmd("samtools index 04_alignments/sorted.bam")
    run_cmd(f"bcftools mpileup -f {ref_path} 04_alignments/sorted.bam | bcftools call -mv -Oz -o 05_variants/mcph_variants.vcf.gz")
    run_cmd("bcftools index 05_variants/mcph_variants.vcf.gz")

    print("--- BIO AGENT: Execution Completed Successfully ---")

if __name__ == "__main__":
    main()