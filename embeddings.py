# embeddings.py
import json
import torch #pytorch for gpu computttion
import gc #garbage collector -> prevent memory leaks for large datasets
from transformers import AutoTokenizer #load pretrained tokenizer for tokenizing (text->numerical)
from adapters import AutoAdapterModel #custom adapter i.e specialized version of  a model

BATCH_SIZE = 4
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu') #if gpu is available use that else use cpu

def generate_embeddings(input_json: str, output_json: str):
    with open(input_json, 'r', encoding='utf-8') as f:
        processed_data = json.load(f)

    # Initialize model pehel and before moving to device
    tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
    model = AutoAdapterModel.from_pretrained('allenai/specter2_base')

    # Load adapter THEN move to device -> causing ltos of erros
    model.load_adapter("allenai/specter2", source="hf", set_active=True)
    model = model.to(DEVICE)  # Move entire model to device after loading adapter

    all_embeddings = []

    for doc in processed_data:
        chunk_embeddings = {}
        chunks = doc['chunks']
        filename = doc['metadata']['filename']

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i+BATCH_SIZE]
            text_batch = [
                [filename, chunk['text']]
                for chunk in batch
            ]

            # Inputs already moved to device
            inputs = tokenizer(
                text_batch,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512
            ).to(DEVICE)
            # disable gradient calculations
            with torch.no_grad():
                outputs = model(**inputs) #passes tokenized inputs through the model to generate o/p

            embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            #extract embeddings of token from model's hidden states and convert it into a numPy array

            for chunk, emb in zip(batch, embeddings):
                chunk_embeddings[chunk['chunk_id']] = emb.tolist()
                #store embedding in chunk_embeddings dict with chunk_id as key
            del inputs, outputs, embeddings #delete variables
            torch.cuda.empty_cache() #clear cache
            gc.collect() #garbage colelctor to free up memory

        #final o/p
        all_embeddings.append({
            "filename": filename,
            "embeddings": chunk_embeddings
        })
    # save into json file with indentation and enabled encoding
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_embeddings, f, indent=2, ensure_ascii=False)


#check that this runs only when you run embeddings.py directly and NOT as a module being imported in some other script
if __name__ == "__main__":
    generate_embeddings("processes.json", "embeddings.json")