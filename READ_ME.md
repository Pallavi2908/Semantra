# Semantra

An AI-powered tool to assist users in verifying and understanding medical queries. By leveraging advanced NLP techniques, Semantra aims to make research-backed knowledge readily available so as to combat the increasing dangers of medical misinformation.

Currently, Semantra focuses on addressing queries from:

- COVID-19
- General queries regarding nutritional health and supplements
- vaccines, in general

#### As of May 2025, Semantra works on data extracted from over 150+ open-access research papers, collected from various scientific websites,i.e. ScienceDirect and arXiv.org

🔗 Live Demo: [Semantra](https://semantra-s9mw.onrender.com/static/)

## Features

- Semantra provides a comprehensive readable report addressing the user's query, breaking it down into sections for ease of understanding. The report also mentions cited research papers & conflicting findings, if present.

- User-friendly UI for ease of use.

- Only relevant papers (no older than 2020 and peer-reviewed) have been used.

## Getting Started / How to Install

#### Prerequisites

- Python 3.x
- Latest version of pip installed

#### Installation steps

1. Clone the respository

```
git clone https://github.com/Pallavi2908/Semantra.git
cd Semantra
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Start the FastAPI server via Uvicorn

```
uvicorn api:app --reload
```

The website is almost ready to be used locally however there's one step left. Kindly check out the [Notes](#notes-) section.

## 🛠️ Tech Stack

**Backend:**

- **[FastAPI](https://fastapi.tiangolo.com/)** – High-performance Python web framework
- **[Uvicorn](https://www.uvicorn.org/)** – ASGI server for serving FastAPI
- **[Weaviate](https://weaviate.io/)**– Vector database for semantic similarity search
- **[Mistral 7B](https://mistral.ai/news/announcing-mistral-7b/)** – Open-weight LLM for generating AI-based medical responses
- Python libraries:
  - `requests`, `pandas`, `scikit-learn`, `uuid`, `json`, etc.

**Frontend:**

- Static HTML/CSS served through FastAPI

**DevOps:**

- [Render](https://render.com/) – Cloud hosting (Free Tier)
- [GitHub Actions](https://github.com/features/actions) – CI/CD workflow to ping the server periodically

## Notes 📝

- In static/index.html kindly change the JavaScript code section in which the try/catch block is executed such that request is sent to /query and not the Render website.

```
    try {
        const res = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });
```

- If you're using the Render free tier, the server may spin down due to inactivity. This project uses a GitHub Actions CI/CD workflow to automatically ping the backend every 14 minutes and keep it alive.
