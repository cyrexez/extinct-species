# Extinct Species Explorer

**Extinct Species Explorer is a scalable biodiversity platform for monitoring wildlife. Its multithreaded ETL pipeline ingests IUCN Red List data and transforms nomenclature via GBIF. Using Google Gemini AI, it generates photorealistic imagery and ecological insights. Built as a Nigerian pilot, the architecture is ready for global conservation.**

---

## 🚀 Key Features

- **Automated ETL Pipeline**: Custom streaming engine to fetch and process thousands of species records from the IUCN Red List API.
- **Multithreaded Enrichment**: Uses `ThreadPoolExecutor` for high-speed data retrieval of population trends and environmental threats.
- **Nomenclature Transformer**: Integrates with the **GBIF API** to automatically map Latin scientific names to English common names.
- **AI-Powered Visuals**: Leverages **Google Gemini 2.5 Flash** to generate photorealistic wildlife imagery and biologist-level ecological insights.
- **Interactive UI**: A streamlined Streamlit interface for searching and filtering species by biological class and extinction risk.

## 🛠️ Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **AI/LLM**: [Google Gemini AI](https://ai.google.dev/)
- **Environment & Dependency Manager**: [uv](https://github.com/astral-sh/uv)
- **Data Libraries**: Pandas, Requests, Beautiful Soup
- **External Data**: IUCN Red List v4 API, Wikipedia API, GBIF API

## 📂 Project Structure

- `app.py`: Main application entry and routing logic.
- `pages/search.py`: Interactive search grid with conservation status filters.
- `pages/detail.py`: AI-enriched species profiles with dynamic image generation.
- `nigeria_extinction_final_clean.csv`: The processed and enriched dataset.
- `pyproject.toml`: Project metadata and dependency locking via `uv`.

## ⚙️ Setup & Installation

This project uses **uv** for ultra-fast, reproducible environments.

1. **Clone the repo**:
   ```bash
   git clone [https://github.com/cyrexez/extinct-species.git](https://github.com/cyrexez/extinct-species.git)
   cd extinct-species
   ```
2. **Install Dependencies:**:
   ```bash
   uv sync
   ```
3. **Configure Environment: Create a .env file in the root directory:**:
   ```bash
   GOOGLE_API_KEY=your_gemini_key
   IUCN_TOKEN=your_iucn_token
   ```
4. **Run the App**:
   ```bash
   uv run streamlit run app.py
   ```
   📜 License
   Conservation Research Project. Data sourced from IUCN Red List.
