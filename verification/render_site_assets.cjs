#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const sharp = require("sharp");

const repo = path.resolve(__dirname, "..");
const sourceArt = process.argv[2];
if (!sourceArt || !fs.existsSync(sourceArt)) {
  throw new Error("Pass the generated hero artwork path as the first argument.");
}

const assets = path.join(repo, "docs", "assets");
fs.mkdirSync(assets, { recursive: true });

const escapeXml = (value) =>
  value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

async function render() {
  await sharp(sourceArt)
    .resize(1600, 900, { fit: "cover", position: "center" })
    .webp({ quality: 88, effort: 6 })
    .toFile(path.join(assets, "semantic-mesh.webp"));

  await sharp(path.join(repo, "assets", "icon.png"))
    .resize(256, 256, { fit: "contain" })
    .png({ compressionLevel: 9 })
    .toFile(path.join(assets, "stunspot-icon.png"));

  const cardWidth = 1280;
  const cardHeight = 640;
  const title = escapeXml("Yammerknit");
  const subtitle = escapeXml("Turn source material into a retrieval-ready semantic mesh.");
  const label = escapeXml("A STUNSPOT AUGMENT");

  const background = await sharp(sourceArt)
    .resize(cardWidth, cardHeight, { fit: "cover", position: "east" })
    .modulate({ brightness: 0.72, saturation: 1.08 })
    .blur(0.35)
    .png()
    .toBuffer();

  const icon = await sharp(path.join(repo, "assets", "icon.png"))
    .resize(138, 138, { fit: "contain" })
    .png()
    .toBuffer();

  const overlay = Buffer.from(`
    <svg width="${cardWidth}" height="${cardHeight}" viewBox="0 0 ${cardWidth} ${cardHeight}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="veil" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#031126" stop-opacity="0.99"/>
          <stop offset="0.56" stop-color="#031126" stop-opacity="0.92"/>
          <stop offset="1" stop-color="#031126" stop-opacity="0.20"/>
        </linearGradient>
        <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#10bdf4"/>
          <stop offset="1" stop-color="#f7b927"/>
        </linearGradient>
      </defs>
      <rect width="1280" height="640" fill="url(#veil)"/>
      <rect x="62" y="58" width="6" height="524" rx="3" fill="url(#line)"/>
      <text x="236" y="128" fill="#7ddcff" font-family="Arial, Helvetica, sans-serif" font-size="24" font-weight="700" letter-spacing="5">${label}</text>
      <text x="88" y="342" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="112" font-weight="800" letter-spacing="-3">${title}</text>
      <text x="94" y="413" fill="#c8d8e8" font-family="Arial, Helvetica, sans-serif" font-size="31" font-weight="400">${subtitle}</text>
      <text x="94" y="470" fill="#c8d8e8" font-family="Arial, Helvetica, sans-serif" font-size="31" font-weight="400">Rupert Giles keeps the source honest.</text>
      <rect x="94" y="526" width="390" height="3" rx="1.5" fill="url(#line)"/>
    </svg>
  `);

  await sharp(background)
    .composite([
      { input: overlay, left: 0, top: 0 },
      { input: icon, left: 88, top: 54 },
    ])
    .png({ compressionLevel: 9, palette: true, quality: 100 })
    .toFile(path.join(assets, "yammerknit-sharecard.png"));
}

render().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
