import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { DOMMatrix, ImageData, Path2D } from '@napi-rs/canvas';

globalThis.DOMMatrix ||= DOMMatrix;
globalThis.ImageData ||= ImageData;
globalThis.Path2D ||= Path2D;

const { handleApi } = await import('./src/api.js');

const app = express();
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), 'public');

app.use(async (request, response, next) => {
  if (!request.path.startsWith('/api/')) return next();
  const url = new URL(request.originalUrl, 'https://docsaarthi.local');
  const handled = await handleApi(request, response, url);
  if (handled === false && !response.headersSent) next();
});

app.use(express.static(root, { index: 'index.html' }));
app.use((_request, response) => response.sendFile(path.join(root, 'index.html')));

export default app;
