import json
from glob import glob
import os

output = []

for file in sorted(glob("vectors/embeddings-*.json")):
    print(f"📂 Processing: {file}")
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data:
        filename = entry["filename"]
        embeddings = entry["embeddings"]  # a dict

        for chunk_id, embedding in embeddings.items():
            if not isinstance(embedding, list) or len(embedding) != 768:
                print(f"⚠️ Skipping {chunk_id} in {filename} — invalid vector")
                continue

            # Minimal structure for upload — add more if needed
            output.append({
                "chunk_id": chunk_id,
                "embedding": embedding,
                "filename": filename,
                "text": "",         # You can later populate this from `processes.json` if needed
                "page": -1
            })

# Save the flat file
with open("merged_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Converted {len(output)} embeddings into flat format.")
