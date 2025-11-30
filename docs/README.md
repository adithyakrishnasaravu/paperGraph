## Gaussian Splatting Research Knowledge Graph

An agentic system that extracts semantic relationships from academic papers and builds a queryable knowledge graph in Postgres.

**Overview**

This project processes Gaussian Splatting research papers to extract:

- Entities (concepts, methods, datasets, metrics, authors)

- Semantic relationships (introduces, improves_on, evaluates_on, extends)

- Evidence snippets with confidence scores

- Built with Python, OpenAI GPT-4o-mini, and Postgres (via Supabase).

**Features**

- LLM-based entity and relationship extraction

- Typed property graph stored in Postgres

- Proof-of-concept pipeline processing 50 papers

- SQL-queryable knowledge graph with evidence tracking

**Project Structure**

```text
gaussian_splatting_graph/
├── data/
│   └── raw/               # PDF papers (49 of them)
├── src/
│   ├── agents/            # LLM extraction agents
│   ├── parsers/           # PDF text extraction
│   ├── database/          # Postgres graph database layer
│   └── pipeline/          # End-to-end processing pipeline
├── sql/
│   └── schema.sql         # Database schema definition
├── docs/
│   └── DOCUMENTATION.md   # Full design documentation
    ├── README.md          # Readme file
    └── imp_image.png      # Architecture diagram of the system
└── requirements.txt
└── .gitignore
```

**Setup**
1. **Clone and install dependencies**
```bash
git clone <link>
cd gaussian_splatting_graph
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set up environment variables**
Create ```.env``` file:

Supabase Database Connection: Get this from your Supabase project settings > Database > Connection string

```bash
DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```
OpenAI API Key: Get this from https://platform.openai.com/api-keys
```bash
OPENAI_API_KEY=sk-your-key-here
```

3. **Set up the database**
- Create a Supabase project at [https://supabase.com](url)
- Run ```sql/schema.sql``` in the SQL Editor
- Update ```.env``` with your connection details

4. **Add papers**
- Place PDF files in data/raw/ directory.

**Usage**: Run the full pipeline
Process all papers in data/raw/:

```bash
python src/pipeline/test_pipeline.py
```
Process in batches (10 papers at a time):

```bash
python src/pipeline/test_pipeline.py 0 10   # Papers 0-9
python src/pipeline/test_pipeline.py 10 10  # Papers 10-19
```

**Query the graph**: Example queries in Supabase SQL Editor:

Papers that improve on 3D Gaussian Splatting:

```sql
SELECT DISTINCT p.properties->>'title' AS paper_title, e.confidence
FROM nodes m
JOIN edges e ON e.target_node_id = m.id
JOIN edge_types et ON et.id = e.edge_type_id
JOIN nodes p ON p.id = e.source_node_id
WHERE m.properties->>'name' ILIKE '%3D Gaussian Splatting%'
  AND et.type_name = 'improves_on';
```
Most commonly used datasets:

```sql
SELECT d.properties->>'name' AS dataset, COUNT(*) as usage_count
FROM nodes d
JOIN node_types nt ON nt.id = d.node_type_id
JOIN edges e ON e.target_node_id = d.id
WHERE nt.type_name = 'Dataset'
GROUP BY d.properties->>'name'
ORDER BY usage_count DESC;
```
More examples in ```docs/DOCUMENTATION.md```:

**Architecture**

```text
PDFs → PDFParser → ExtractionAgent → GraphDatabase → Postgres → Queries
         │              │                  │              │
    Extract text    metadata          nodes/edges    SQL queries
                    entities
                    relationships
```

<img width="1408" height="736" alt="image" src="https://github.com/user-attachments/assets/4b5e54da-998a-41d6-9a3a-5574e7cb3119" />


**Key Design Decisions**
- Typed property graph in Postgres (flexible JSONB + relational tables)
- LLM-based extraction with structured prompts and JSON output
- Evidence tracking for every relationship with confidence scores

Requirements
- Python 3.8+
- OpenAI API key
- Postgres database (Supabase recommended)

Cost Estimate

~$0.03 per paper for LLM extraction (GPT-4o-mini)
~$1.50-$2 for 50 papers

Documentation

Full documentation including:

- System architecture
- Graph schema design
- Entity extraction strategy
- Scalability and limitations
- Example queries and results

See docs/DOCUMENTATION.md

**- Adithya Saravu**



