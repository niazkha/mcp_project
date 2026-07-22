#!/bin/bash
set -e

echo "=== Step 1: Setting up environment ==="
VCF_INPUT="05_variants/mcph_variants.vcf.gz"
FILTERED_VCF="06_annotation/mcph_filtered.vcf.gz"

mkdir -p 06_annotation

echo "=== Step 2: Variant filtering ==="
bcftools view -i 'QUAL>20 && DP>10' "$VCF_INPUT" -Oz -o "$FILTERED_VCF"
bcftools index -t "$FILTERED_VCF"

echo "=== Step 3: Extracting HGVS variants ==="
python3 -c "
import gzip
with gzip.open('$FILTERED_VCF', 'rt') as f, open('06_annotation/variants_for_vep.txt', 'w') as out:
    for line in f:
        if not line.startswith('#'):
            parts = line.strip().split('\t')
            chrom, pos, ref, alt = parts[0].replace('chr', ''), parts[1], parts[3], parts[4]
            out.write(f'{chrom}:g.{pos}{ref}>{alt}\n')
"

echo "=== Step 4: Running Annotation Script ==="
python3 -c "
import requests, json

print(f\"{'VARIANT':<15} {'GENE':<12} {'CONSEQUENCE':<25} {'IMPACT':<10}\")
print('-' * 65)

try:
    with open('06_annotation/variants_for_vep.txt') as f:
        for line in f:
            variant = line.strip()
            if not variant: continue
            url = f'https://rest.ensembl.org/vep/human/hgvs/{variant}?'
            try:
                response = requests.get(url, headers={'Content-Type': 'application/json'}, timeout=3)
                if response.ok:
                    data = response.json()
                    for entry in data:
                        tc_list = entry.get('transcript_consequences', [{'gene_symbol': 'N/A', 'consequence_terms': ['intergenic'], 'impact': 'MODIFIER'}])
                        for tc in tc_list:
                            print(f\"{variant:<15} {tc.get('gene_symbol', 'N/A'):<12} {', '.join(tc.get('consequence_terms', [])):<25} {tc.get('impact', 'N/A'):<10}\")
                            break
                else:
                    print(f\"{variant:<15} Error or variant not found\")
            except requests.exceptions.RequestException:
                print(f\"{variant:<15} Offline/Network unreachable (Skipped API)\")
except FileNotFoundError:
    print('variants_for_vep.txt not found.')
"

echo "=== Pipeline Finished Successfully ==="
