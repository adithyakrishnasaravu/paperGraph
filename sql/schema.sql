-- Drop existing tables (clean slate)
DROP TABLE IF EXISTS edges CASCADE;
DROP TABLE IF EXISTS edge_types CASCADE;
DROP TABLE IF EXISTS nodes CASCADE;
DROP TABLE IF EXISTS node_types CASCADE;
DROP TABLE IF EXISTS paper_authors CASCADE;
DROP TABLE IF EXISTS authors CASCADE;
DROP TABLE IF EXISTS papers CASCADE;

--CORE GRAPH TABLES
--- table for academic papers
CREATE TABLE node_types (
    id SERIAL PRIMARY KEY,
    type_name TEXT UNIQUE NOT NULL ,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--  nodes: storage for all entities in the graph
CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    node_type_id INTEGER REFERENCES node_types(id) ON DELETE CASCADE,
    properties JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Edge Types: defines relationship categories
CREATE TABLE edge_types (
    id SERIAL PRIMARY KEY,
    type_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Edges: Relationships between nodes
CREATE TABLE edges (
    id SERIAL PRIMARY KEY,
    edge_type_id INTEGER REFERENCES edge_types(id) ON DELETE CASCADE,
    source_node_id INTEGER REFERENCES nodes(id) ON DELETE CASCADE,
    target_node_id INTEGER REFERENCES nodes(id) ON DELETE CASCADE,
    properties JSONB,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_edge UNIQUE (edge_type_id, source_node_id, target_node_id)
);

-- legacy table for papers
CREATE TABLE papers (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES nodes(id) ON DELETE CASCADE,  -- Link to graph node
    title TEXT NOT NULL,
    year INTEGER,
    abstract TEXT,
    arxiv_id TEXT UNIQUE,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Authors table
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES nodes(id) ON DELETE CASCADE,  -- Link to graph node
    name TEXT NOT NULL UNIQUE,
    affiliation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paper-Author relationship (many-to-many)
CREATE TABLE paper_authors (
    paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
    author_order INTEGER,  -- Track author ordering
    PRIMARY KEY (paper_id, author_id)
);

-- INDEXES FOR PERFORMANCE
-- Graph traversal indexes
CREATE INDEX idx_nodes_type ON nodes(node_type_id);
CREATE INDEX idx_nodes_properties ON nodes USING gin(properties);
CREATE INDEX idx_edges_source ON edges(source_node_id);
CREATE INDEX idx_edges_target ON edges(target_node_id);
CREATE INDEX idx_edges_type ON edges(edge_type_id);
CREATE INDEX idx_edges_confidence ON edges(confidence);

-- Legacy table indexes
CREATE INDEX idx_papers_year ON papers(year);
CREATE INDEX idx_papers_title ON papers(title);
CREATE INDEX idx_papers_arxiv ON papers(arxiv_id);
CREATE INDEX idx_authors_name ON authors(name);

-- SEED DATA: Initial node and edge types
INSERT INTO node_types (type_name, description) VALUES
    ('Paper', 'Academic research paper'),
    ('Author', 'Paper author or researcher'),
    ('Concept', 'Key idea or theoretical contribution'),
    ('Method', 'Algorithm or technical approach'),
    ('Dataset', 'Evaluation dataset'),
    ('Metric', 'Performance measurement'),
    ('Venue', 'Conference or journal');

-- Insert predefined edge types
INSERT INTO edge_types (type_name, description) VALUES
    ('authored_by', 'Paper written by Author'),
    ('cites', 'Paper cites another Paper'),
    ('introduces', 'Paper introduces a Concept or Method'),
    ('improves_on', 'Method improves upon another Method'),
    ('evaluates_on', 'Paper evaluates on a Dataset'),
    ('measures_with', 'Paper uses a Metric'),
    ('extends', 'Work extends previous research'),
    ('compares_with', 'Method compared against another'),
    ('uses', 'Paper uses a Method or Concept'),
    ('published_in', 'Paper published in Venue');

-- EXAMPLES OF QUERIES

-- Query 1: Find all papers that improve on "3D Gaussian Splatting"
-- SELECT 
--     p.title,
--     et.type_name as relationship,
--     n_target.properties->>'name' as improved_method
-- FROM papers p
-- JOIN nodes n_source ON p.node_id = n_source.id
-- JOIN edges e ON n_source.id = e.source_node_id
-- JOIN edge_types et ON e.edge_type_id = et.id
-- JOIN nodes n_target ON e.target_node_id = n_target.id
-- WHERE et.type_name = 'improves_on'
--   AND n_target.properties->>'name' ILIKE '%Gaussian Splatting%';

-- Query 2: Find all concepts introduced by a specific paper
-- SELECT 
--     n.properties->>'name' as concept_name,
--     e.confidence
-- FROM papers p
-- JOIN nodes n_paper ON p.node_id = n_paper.id
-- JOIN edges e ON n_paper.id = e.source_node_id
-- JOIN nodes n ON e.target_node_id = n.id
-- JOIN node_types nt ON n.node_type_id = nt.id
-- JOIN edge_types et ON e.edge_type_id = et.id
-- WHERE p.title ILIKE '%3D Gaussian Splatting%'
--   AND et.type_name = 'introduces'
--   AND nt.type_name = 'Concept';

-- Query 3: Find papers and their evaluation datasets
-- SELECT 
--     p.title,
--     n.properties->>'name' as dataset_name
-- FROM papers p
-- JOIN nodes n_paper ON p.node_id = n_paper.id
-- JOIN edges e ON n_paper.id = e.source_node_id
-- JOIN nodes n ON e.target_node_id = n.id
-- JOIN node_types nt ON n.node_type_id = nt.id
-- JOIN edge_types et ON e.edge_type_id = et.id
-- WHERE et.type_name = 'evaluates_on'
--   AND nt.type_name = 'Dataset';
