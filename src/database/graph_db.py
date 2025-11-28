import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
import os

load_dotenv()

class GraphDatabase:
    """Handles all database operations for the knowledge graph"""

    def __init__(self):
        # Connect to the Postgres database
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.conn.autocommit = False

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Automatically commit or rollback on exit
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
    
    def get_or_create_node_type(self, type_name):
        # get id for a node type
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM node_types WHERE type_name = %s",
            (type_name,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    def get_or_create_edge_type(self, type_name):
        # get id for an edge type ['introduces', 'improves_on']
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM edge_types WHERE type_name = %s",
            (type_name,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    def create_node(self, node_type_name, properties):
        node_type_id = self.get_or_create_node_type(node_type_name)
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO nodes (node_type_id, properties)
            VALUES (%s, %s)
            RETURNING id
            """,
            (node_type_id, Json(properties))
        )
        node_id = cursor.fetchone()[0]
        cursor.close()
        return node_id
    
    def find_node_by_property(self, node_type_name, property_key, property_value):
        cursor = self.conn.cursor()
        node_type_id = self.get_or_create_node_type(node_type_name)
        cursor.execute(
            """
            SELECT id, properties FROM nodes
            WHERE node_type_id = %s
            AND properties->>%s = %s
            LIMIT 1
            """,
            (node_type_id, property_key, property_value)
        )
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {'id': result[0], 'properties': result[1]}
        return None
    
    def get_or_create_node(self, node_type_name, properties, unique_key = 'name'):
        # gets existing node or create new one (prevents duplicates)
        unique_val = properties.get(unique_key)

        if unique_val:
            existing_node = self.find_node_by_property(node_type_name, unique_key, unique_val)
            if existing_node:
                return existing_node['id']
        
        # it doesn't exist -> create it
        return self.create_node(node_type_name, properties)

    def create_edge(self, edge_type_name, source_node_id, target_node_id, properties=None, confidence = 1.0):
        # create an edge between two nodes
        cursor = self.conn.cursor()
        edge_type_id = self.get_or_create_edge_type(edge_type_name)
        try:
            cursor.execute(
                """
                INSERT INTO edges (edge_type_id, source_node_id, target_node_id, properties, confidence)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (edge_type_id, source_node_id, target_node_id) DO NOTHING
                RETURNING id
                """,            
                (edge_type_id, source_node_id, target_node_id, Json(properties or {}), confidence)
            )

            result = cursor.fetchone()
            edge_id = result[0] if result else None
            cursor.close()
            return edge_id
        
        except Exception as e:
            print(f"Error creating edge: {e}")
            cursor.close()
            return None

    def insert_paper(self, metadata):
        # insert a paper + its authors. Returns (paper_id, paper_node_id).
        cursor = self.conn.cursor()

        # 1: create a paper node in graph
        paper_node_id = self.get_or_create_node(
            'Paper',
            {
                'title': metadata['title'],
                'year': metadata.get('year'),
                'abstract': metadata.get('abstract', '')
            },
            unique_key = 'title'
        )

        # 2: insert into legacy papers table
        cursor.execute(
            """
            INSERT INTO papers (node_id, title, year, abstract)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (title) DO UPDATE
            SET year = EXCLUDED.year,
                abstract = EXCLUDED.abstract
            RETURNING id
            """,
            (paper_node_id, metadata['title'], metadata.get('year'), metadata.get('abstract', ''))
        )
        paper_id = cursor.fetchone()[0]
        cursor.close()

        # 3: Authors: nodes + legacy tables + edges
        for idx, author_name in enumerate(metadata.get('authors', [])):
            # graph node
            author_node_id = self.get_or_create_node('Author', {'name': author_name})

            # legacy authors + paper_authors
            c = self.conn.cursor()
            c.execute(
                """
                INSERT INTO authors (node_id, name)
                VALUES (%s, %s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                (author_node_id, author_name)
            )
            row = c.fetchone()
            if row:
                author_id = row[0]
            else:
                c.execute("SELECT id FROM authors WHERE name = %s", (author_name,))
                author_id = c.fetchone()[0]
            c.execute(
                """
                INSERT INTO paper_authors (paper_id, author_id, author_order)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (paper_id, author_id, idx)
            )
            c.close()

            # graph edge paper -> authored_by -> author
            self.create_edge('authored_by', paper_node_id, author_node_id)
        return paper_id, paper_node_id

# testing
def test_basic_node_creation():
    """Test node and edge creation"""
    with GraphDatabase() as db:
        print("Creating nodes...")
        
        # Create two concept nodes
        concept1_id = db.get_or_create_node('Concept', {'name': '3D Gaussian Splatting'})
        concept2_id = db.get_or_create_node('Concept', {'name': 'Neural Radiance Fields'})
        
        print(f"✓ Concept 1 ID: {concept1_id}")
        print(f"✓ Concept 2 ID: {concept2_id}")
        
        # Create a relationship
        print("\nCreating edge: '3D Gaussian Splatting' improves_on 'Neural Radiance Fields'...")
        edge_id = db.create_edge(
            'improves_on', 
            concept1_id, 
            concept2_id,
            properties={'evidence': 'Uses explicit Gaussians instead of implicit neural representations'},
            confidence=0.95
        )
        
        print(f"✓ Created edge with ID: {edge_id}")
        
        print("\n✅ Test completed! Check Supabase to see your graph.")

def test_insert_paper():
    sample = {
        "title": "Test Paper on 3D Gaussian Splatting",
        "authors": ["Alice Example", "Bob Example"],
        "year": 2024,
        "abstract": "This is a test abstract."
    }
    with GraphDatabase() as db:
        pid, pnid = db.insert_paper(sample)
        print(f"paper_id={pid}, paper_node_id={pnid}")
 
if __name__ == "__main__":
    test_insert_paper()
