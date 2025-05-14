# import requests
# import json

# url = "https://api.semanticscholar.org/graph/v1/paper/search"
# params = {
#     "query": "covid vaccine OR vaccine myths",
#     "offset": 0,
#     "limit": 10,
#     # Include nested fields for references and their details
#     "fields": "title,abstract,authors,year,url,references.citedPaper.title,references.citedPaper.authors,references.citedPaper.year,references.citedPaper.url"
# }

# all_papers = []

# while True:
#     response = requests.get(url, params=params)
#     data = response.json()

#     papers = data.get("data", [])
#     if not papers:
#         break

#     for paper in papers:
#         paper_data = {
#             "title": paper.get("title", ""),
#             "abstract": paper.get("abstract", ""),
#             "authors": [author["name"] for author in paper.get("authors", [])],
#             "year": paper.get("year", ""),
#             "url": paper.get("url", ""),
#             "references": []
#         }

#         # Extract cited papers from references
#         for ref in paper.get("references", []):
#             cited_paper = ref.get("citedPaper", {})
#             if cited_paper:  # Only include if citedPaper exists
#                 cited_data = {
#                     "title": cited_paper.get("title", ""),
#                     "authors": [author["name"] for author in cited_paper.get("authors", [])],
#                     "year": cited_paper.get("year", ""),
#                     "url": cited_paper.get("url", "")
#                 }
#                 paper_data["references"].append(cited_data)

#         all_papers.append(paper_data)

#     params["offset"] += params["limit"]

# # Save results to JSON
# with open("papers_with_references.json", "w", encoding="utf-8") as f:
#     json.dump(all_papers, f, indent=2, ensure_ascii=False)

import urllib.request as libreq
with libreq.urlopen('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1') as url:
    r = url.read()
print(r)
