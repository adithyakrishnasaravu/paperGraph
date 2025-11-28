import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const MODEL = "gpt-4o-mini";

export async function extractMetadataTs(paperText: string) {
  const prompt = `
You are an expert at extracting metadata from academic papers.

Paper Text (first few pages):
${paperText.slice(0, 8000)}

Extract the following metadata:
1. title: Full paper title
2. authors: List of author names
3. year: Publication year (integer)
4. abstract: Paper abstract (full text)

Return ONLY valid JSON in this exact format:
{
  "title": "Full Paper Title",
  "authors": ["Author One", "Author Two", "Author Three"],
  "year": 2024,
  "abstract": "Full abstract text here..."
}
`;

  const res = await client.chat.completions.create({
    model: MODEL,
    messages: [
      {
        role: "system",
        content: "You are a precise metadata extractor. Return only valid JSON.",
      },
      { role: "user", content: prompt },
    ],
    response_format: { type: "json_object" },
    temperature: 0.1,
  });

  const content = res.choices[0]?.message?.content || "{}";
  return JSON.parse(content);
}

export async function extractEntitiesTs(paperText: string, paperTitle: string) {
  const prompt = `
You are an expert at analyzing academic papers in computer graphics and 3D reconstruction.

Paper Title: ${paperTitle}
Paper Text: ${paperText.slice(0, 5000)}

Extract the following entities from the paper:
1. Concepts: Key ideas or theoretical contributions
2. Methods: Algorithms or technical approaches
3. Datasets: Evaluation datasets
4. Metrics: Performance measurements

Return ONLY valid JSON with this structure:
{
  "concepts": ["concept1", "concept2"],
  "methods": ["method1", "method2"],
  "datasets": ["dataset1", "dataset2"],
  "metrics": ["metric1", "metric2"]
}
`;

  const res = await client.chat.completions.create({
    model: MODEL,
    messages: [
      {
        role: "system",
        content: "You are an expert at analyzing academic papers. Return only valid JSON.",
      },
      { role: "user", content: prompt },
    ],
    response_format: { type: "json_object" },
    temperature: 0.2,
  });

  const content = res.choices[0]?.message?.content || "{}";
  return JSON.parse(content);
}

export async function extractRelationshipsTs(
  paperText: string,
  paperTitle: string,
  entities: any
) {
  const prompt = `
You are an expert at identifying relationships in academic papers.

Paper Title: ${paperTitle}

Extracted Entities:
${JSON.stringify(entities, null, 2)}

Paper Text: ${paperText.slice(0, 5000)}

Extract relationships of types:
- introduces
- improves_on
- evaluates_on
- measures_with
- extends
- compares_with

Return ONLY a JSON array like:
[
  {
    "source": "entity_name_or_paper_title",
    "relationship": "relationship_name",
    "confidence": 0.95,
    "target": "entity_name",
    "evidence": "very brief explanation from the paper"
  }
]
`;

  const res = await client.chat.completions.create({
    model: MODEL,
    messages: [
      {
        role: "system",
        content: "You are a precise relationship extractor. Return only valid JSON.",
      },
      { role: "user", content: prompt },
    ],
    response_format: { type: "json_object" },
    temperature: 0.2,
  });

  const content = res.choices[0]?.message?.content || "[]";
  return JSON.parse(content);
}
