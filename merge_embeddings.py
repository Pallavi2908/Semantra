import json
from glob import glob

merged = []
invalid_files = []

for file in sorted(glob("vectors/embeddings-*.json")):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print(f" {file} is not a list!")
            invalid_files.append(file)
            continue

        for item in data:
            if "embedding" not in item or "chunk_id" not in item:
                invalid_files.append(file)
                break

        merged.extend(data)

    except json.JSONDecodeError as e:
        print(f"❌ JSON decoding error in {file}: {e}")
        invalid_files.append(file)

with open("merged_embeddings.json", 'w', encoding='utf-8') as f:
    json.dump(merged, f)

print(f" Merged items successfully!")
