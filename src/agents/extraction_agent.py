# OpenAI agent to extract information from a PDF file
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ExtractionAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"

    def extract_entities(self, paper_text, paper_title):
        """Extract entities (Concepts, Methods, Datasets, Metrics) from paper"""
        prompt = f"""You are an expert at analyzing academic papers in computer graphics and 3D reconstruction.
        
        Paper Title: {paper_title}
        Paper Text: {paper_text[:5000]}

        Extract the following entities from the paper:
        1. **Concepts**: Key ideas or theoretical contributions
        2. **Methods**: Algorithms or technical approaches
        3. **Datasets**: Evaluation datasets
        4. **Metrics**: Performance measurements

        Return the entities in a JSON format with the following structure:
        {{
            "concepts": ["concept1", "concept2"],
            "methods": ["method1", "method2"],
            "datasets": ["dataset1", "dataset2"],
            "metrics": ["metric1", "metric2"]
        }}

        Do not include explainations, just the JSON. """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing academic papers."}, 
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {"concepts": [], "methods": [], "datasets": [], "metrics": []}
    
    def extract_relationships(self, paper_text, paper_title, entities):
        """Extract semantic relationships between entities in the paper"""
        prompt = f"""You are an expert at identifying relationships in academic papers.

        Paper Title: {paper_title}

        Extracted Entities: {json.dumps(entities, indent=2)}

        Paper Text: {paper_text[:5000]}

        Extract the following relationships from the paper:
        1. **introduces**: Paper introduces a concept or method
        2. **improves_on**: A method improves upon another method
        3. **evaluates_on**: A paper evaluates performance on a dataset
        4. **measures_with**: Paper measures results with a metric
        5. **extends**: Work extends or builds upon previous research
        6. **compares_with**: Compares performance with another method or approach

        Return the relationships in a JSON format with the following structure:
        [
            {{
                "source": "entity_name",
                "relationship": "relationship_name",
                "confidence": 0.95,
                "target": "entity_name",
                "evidence": "very brief explaination of the paper
            }}
        ]
        Rules:
        - Source should be the paper title or an entity from the extracted list
        - Target should be an entity from the extracted list
        - Confidence: 0.0 to 1.0 (how confident you are)
        - Evidence: 1-2 sentence quote or explanation

        Return only the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create (
                model = self.model,
                messages=[
                    {"role": "system", "content": "You are a precise relationship extractor. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format = {"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            if isinstance(result, dict) and 'relationships' in result:
                return result['relationships']
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except Exception as e:
            print(f"Error extracting relationships: {e}")
            return []   
    def extract_metadata(self, paper_text):
        """Extract paper metadata (title, authors, year, abstract) using LLM"""
        
        prompt = f"""You are an expert at extracting metadata from academic papers.

        Paper Text (first few pages):
        {paper_text[:8000]}

        Extract the following metadata:
        1. **title**: Full paper title
        2. **authors**: List of author names
        3. **year**: Publication year (integer)
        4. **abstract**: Paper abstract (full text)

        Return ONLY valid JSON in this exact format:
        {{
            "title": "Full Paper Title",
            "authors": ["Author One", "Author Two", "Author Three"],
            "year": 2024,
            "abstract": "Full abstract text here..."
        }}

        Do not include explanations, only the JSON object."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise metadata extractor. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
          
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {
                "title": "Unknown",
                "authors": [],
                "year": None,
                "abstract": ""
            }

# test function
def test_extraction():
    """Test the extraction agent"""
    agent = ExtractionAgent()

    # Sample text from a paper
    sample_text = """
    3D Gaussian Splatting for Real-Time Radiance Field Rendering
    
    Abstract: Radiance Field methods have recently revolutionized novel-view synthesis. 
    We introduce 3D Gaussian Splatting, which uses anisotropic 3D Gaussians for scene 
    representation. Our method achieves real-time rendering at 30+ FPS while maintaining 
    high visual quality. We evaluate on Mip-NeRF 360, Tanks and Temples, and Deep Blending 
    datasets, measuring PSNR, SSIM, and LPIPS metrics. Our approach improves upon NeRF 
    by using explicit 3D Gaussians instead of implicit neural representations.
    """

    print("Testing entity extraction")
    entities = agent.extract_entities(sample_text, "3D Gaussian Splatting")

    print("\nExtracted Entities:")
    print(json.dumps(entities, indent=2))
    
    print("\n" + "="*80)
    print("Testing Relationship Extraction...")
    relationships = agent.extract_relationships(sample_text, "3D Gaussian Splatting", entities)
    print("\nExtracted Relationships:")
    print(json.dumps(relationships, indent=2))


if __name__ == "__main__":
    test_extraction()







