import os

ref_dir = "/home/researcher/mcp_project/03_reference"
files = os.listdir(ref_dir)

print(f"Contents of {ref_dir}:")
for f in files:
    print(f" - {f}")



