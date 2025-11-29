import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.parsers.pdf_parser import PDFParser
from src.agents.extraction_agent import ExtractionAgent
from src.database.graph_db import GraphDatabase


def process_all_papers(start_index=0, batch_size=10):
    agent = ExtractionAgent()
    data_dir = Path('data/raw')
    pdfs = list(data_dir.glob('*.pdf'))

    # Select batch
    end_idx = min(start_index + batch_size, len(pdfs))
    batch = pdfs[start_index:end_idx]

    print(f"Found {len(pdfs)} PDFs\n")
    print(f"Processing batch: indices {start_index}-{end_idx-1} ({len(batch)} papers)\n")

    with GraphDatabase() as db:
        for i, pdf_path in enumerate(batch, start=start_index):
            print("\n" + "="*80)
            print(f"[{i+1}/{len(pdfs)}] Processing: {pdf_path.name}")
            print("="*80)

            # 1) Extract text
            parser = PDFParser(pdf_path)
            raw_text = parser.extract_text()
            print(f"✓ Extracted {len(raw_text)} characters of text")

            # 2) LLM metadata
            metadata = agent.extract_metadata(raw_text)
            print(f"Title: {metadata['title']}")
            print(f"Year: {metadata['year']}")
            print(f"Authors: {', '.join(metadata['authors'][:3])}...")

            # 3) Insert into DB
            paper_id, paper_node_id = db.insert_paper(metadata)
            print(f"→ Stored as paper_id={paper_id}, paper_node_id={paper_node_id}")

            entities = agent.extract_entities(raw_text, metadata['title'])
            relationships = agent.extract_relationships(raw_text, metadata['title'], entities)

            # 4) Insert entities as nodes
            concept_nodes = {}
            for c in entities.get("concepts", []):
                concept_nodes[c] = db.get_or_create_node("Concept", {"name": c})
            
            method_nodes = {}
            for m in entities.get("methods", []):
                method_nodes[m] = db.get_or_create_node("Method", {"name": m})

            dataset_nodes = {}
            for d in entities.get("datasets", []):
                dataset_nodes[d] = db.get_or_create_node("Dataset", {"name": d})

            metric_nodes = {}
            for m in entities.get("metrics", []):
                metric_nodes[m] = db.get_or_create_node("Metric", {"name": m})

            name_to_id = {
                metadata["title"]: paper_node_id,
                **concept_nodes,
                **method_nodes,
                **dataset_nodes,
                **metric_nodes,
            }

            for rel in relationships:
                src = name_to_id.get(rel["source"])
                tgt = name_to_id.get(rel['target'])
                if not src or not tgt:
                    continue
                db.create_edge(
                    rel["relationship"],
                    src,
                    tgt,
                    properties={"evidence": rel.get("evidence", "")},
                    confidence=rel.get("confidence", 1.0),
                )
if __name__ == "__main__":
    import sys
    
    # Read command line args or use defaults
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    process_all_papers(start, batch)

