import pymupdf,json,os,re
from langchain_text_splitters import RecursiveCharacterTextSplitter

def clean_processedtext(text):
    return re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

def process(pdf_path:str)->dict:
    doc=pymupdf.open(pdf_path)
    metadata=doc.metadata
    author=metadata.get("author","Unknown")
    full_text=""
    for page in doc:
        full_text += page.get_text()+"\n"
    text=" ".join(full_text.replace("\n"," ").split())
    # text=clean_processedtext(text)
    text = " ".join(text.replace("\n", " ").split())
    split=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks=split.split_text(text)

    #json
    #Holistic view -> understanding the overall meaning of the text. This is for text sumamrization and question answering
    return{
        "metadata":{
            "filename": os.path.basename(pdf_path),
            "chunk_size":300,
            "chunk_overlap":50,
            "total_pages":len(doc),
            "author": author
        },
        "chunks":[
            {
                "chunk_id":f"{os.path.basename(pdf_path)}chunk_{i+1}",
                "text":chunk,
                "page":(i//3)+1
            }
            for i,chunk in enumerate(chunks)
        ]
    }

def process_folder(folder_path: str, output_json: str):
    outputs=[]
    for file in os.listdir(folder_path):
        pdf_path=os.path.join(folder_path,file)
        # print("Processing")
        result=process(pdf_path)
        outputs.append(result)
    with open(output_json,"w",encoding="utf-8") as f:
        json.dump(outputs,f,indent=2,ensure_ascii=False)
    
    print("All done ")

process_folder("data","processes.json")