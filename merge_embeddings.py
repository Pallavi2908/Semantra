import json
from glob import glob

merged = []
invalid_files = []

for file in sorted(glob("vectors/embeddings-*.json")):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print(f"❌ {file} is not a list!")
            invalid_files.append(file)
            continue

        # Check that each item has the expected keys
        for item in data:
            if "embedding" not in item or "chunk_id" not in item:
                print(f"⚠️ Missing keys in {file}: {item}")
                invalid_files.append(file)
                break

        merged.extend(data)

    except json.JSONDecodeError as e:
        print(f"❌ JSON decoding error in {file}: {e}")
        invalid_files.append(file)

# Save valid merged data
with open("merged_embeddings.json", 'w', encoding='utf-8') as f:
    json.dump(merged, f)

print(f"✅ Merged {len(merged)} items successfully!")
if invalid_files:
    print("⚠️ Skipped these invalid files:", invalid_files)
