import sharp from 'sharp';
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const svgPath = resolve(__dirname, '../public/icons/icon.svg');
const svg = readFileSync(svgPath);

const sizes = [192, 512];

for (const size of sizes) {
  await sharp(svg)
    .resize(size, size)
    .png()
    .toFile(resolve(__dirname, `../public/icons/icon-${size}.png`));
  console.log(`✓ icon-${size}.png`);
}

// Maskable icon (with extra safe-zone padding)
const maskSvg = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#1E4D8C"/>
  <g transform="translate(256,230) scale(0.75)">
    <path d="M0-120 C-66-120-120-66-120 0 C-120 66 0 180 0 180 S120 66 120 0 C120-66 66-120 0-120Z"
          fill="white" opacity="0.95"/>
    <circle cx="0" cy="-8" r="52" fill="#1E4D8C"/>
    <path d="M0-36 L20 12 L0 2 L-20 12Z" fill="white"/>
  </g>
</svg>`);

for (const size of sizes) {
  await sharp(maskSvg)
    .resize(size, size)
    .png()
    .toFile(resolve(__dirname, `../public/icons/icon-${size}-maskable.png`));
  console.log(`✓ icon-${size}-maskable.png`);
}

console.log('Done!');
