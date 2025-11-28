import { extractMetadataTs, extractEntitiesTs, extractRelationshipsTs } from "./extractionAgent";

async function main() {
  const sampleText = `
3D Gaussian Splatting for Real-Time Radiance Field Rendering

Abstract: Radiance Field methods have recently revolutionized novel-view synthesis.
We introduce 3D Gaussian Splatting, which uses anisotropic 3D Gaussians for scene
representation. We evaluate on Mip-NeRF 360 and Tanks and Temples, measuring PSNR and SSIM.
`;

  const title = "3D Gaussian Splatting for Real-Time Radiance Field Rendering";

  console.log("=== Metadata (TS) ===");
  const meta = await extractMetadataTs(sampleText);
  console.log(meta);

  console.log("\n=== Entities (TS) ===");
  const entities = await extractEntitiesTs(sampleText, title);
  console.log(entities);

  console.log("\n=== Relationships (TS) ===");
  const rels = await extractRelationshipsTs(sampleText, title, entities);
  console.log(rels);
}

main().catch(console.error);
