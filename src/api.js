import { config, DISCLAIMER } from './config.js';
import { store } from './store.js';
import { validateUpload, extractPdf, newDocumentId } from './services/document-service.js';
import { detectLanguage } from './services/language-service.js';
import { classifyDocument } from './services/classification-service.js';
import { analyzeDocument } from './services/intelligence-service.js';
import { chunkPages, retrieve } from './services/rag-service.js';
import { answerQuestion } from './services/ai-service.js';
import { translateText, translationDatasetStatus } from './services/translation-service.js';
import { loadIntentModel, detectIntent, conversationalIntent, retrievalQuery } from './services/intent-service.js';

const intents = loadIntentModel(config.datasetPath);
const json = (response, status, body) => { response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }); response.end(JSON.stringify(body)); };
const read = request => new Promise((resolve, reject) => { let raw = ''; request.on('data', chunk => { raw += chunk; if (raw.length > config.maxFileBytes * 1.5) reject(Error('Request is too large.')); }); request.on('end', () => { try { resolve(JSON.parse(raw || '{}')); } catch { reject(Error('Invalid request.')); } }); request.on('error', reject); });
const publicDoc = document => { const { bytes, chunks, text, pages, ...safe } = document; return { ...safe, pages: pages.map(page => ({ page_number: page.page_number, text: page.text })), chunk_count: chunks.length, disclaimer: DISCLAIMER }; };
function reviveDocument(snapshot,id){
  if(!snapshot||snapshot.id!==id||!Array.isArray(snapshot.pages)||!snapshot.pages.length)return null;
  const pages=snapshot.pages.map((page,index)=>({page_number:Number(page.page_number)||index+1,text:String(page.text||'').slice(0,config.maxFileBytes)}));
  const text=pages.map(page=>page.text).join('\n\n');
  if(!text.trim()||text.length>config.maxFileBytes)return null;
  const document={...snapshot,id,pages,text,page_count:pages.length};
  document.chunks=chunkPages(document);store.set(document);return document;
}
function conversationAnswer(kind, requested, question) {
  const answer = kind === 'greeting'
    ? { english: 'Hello! Ask me a question about the uploaded document.', hindi: 'नमस्ते! अपलोड किए गए दस्तावेज़ के बारे में कोई प्रश्न पूछिए।' }
    : { english: 'You are welcome. Ask me anything about the uploaded document.', hindi: 'आपका स्वागत है। अपलोड किए गए दस्तावेज़ के बारे में कोई प्रश्न पूछिए।' };
  return { question_language: detectLanguage(question), response_language: requested, answer_order: requested === 'en' ? ['en'] : requested === 'hi' ? ['hi'] : ['hi', 'en'], answer, intent: { intent: 'Conversation', score: 1 }, sources: [], grounded: false, conversational: true, ai_status: null };
}

export async function handleApi(request, response, url) {
  try {
    if (request.method === 'GET' && url.pathname === '/api/health') return json(response, 200, { ok: true, translation: translationDatasetStatus(), dataset: { sample_count: intents.sample_count, intents: intents.intents }, disclaimer: DISCLAIMER });
    if (request.method === 'GET' && url.pathname === '/api/documents') return json(response, 200, { documents: store.list() });
    if (request.method === 'POST' && url.pathname === '/api/documents') {
      const input = await read(request), bytes = Buffer.from(input.data || '', 'base64');
      validateUpload({ name: input.name, type: input.type, bytes }, config.maxFileBytes);
      const extracted = await extractPdf(bytes), id = newDocumentId(), language = detectLanguage(extracted.text), classification = classifyDocument(extracted.text);
      const document = { id, filename: input.name, bytes, created_at: new Date().toISOString(), status: 'READY', document_language: language, document_type: classification.document_type, classification_confidence: classification.confidence, classification_explanation: classification.explanation, ...extracted };
      document.chunks = chunkPages(document); Object.assign(document, await analyzeDocument(document)); store.set(document);
      return json(response, 201, { document: publicDoc(document) });
    }
    const match = url.pathname.match(/^\/api\/documents\/([^/]+)(?:\/(chat|translate|search))?$/);
    if (!match) return false;
    const input=request.method==='POST'&&match[2]?await read(request):null;
    const document = store.get(match[1])||reviveDocument(input?.document,match[1]); if (!document) return json(response, 404, { error: 'Document not found.' });
    if (request.method === 'GET' && !match[2]) return json(response, 200, { document: publicDoc(document) });
    if (request.method === 'POST' && match[2] === 'chat') {
      if (!input.question?.trim()) throw Error('Enter a question.');
      const requested = ['en', 'hi', 'both'].includes(input.response_language) ? input.response_language : 'both', conversation = conversationalIntent(input.question);
      if (conversation) return json(response, 200, conversationAnswer(conversation, requested, input.question));
      const intent = detectIntent(input.question, intents), evidence = retrieve(retrievalQuery(input.question, intent), document.chunks);
      return json(response, 200, await answerQuestion(input.question, evidence, intent, requested, document));
    }
    if (request.method === 'POST' && match[2] === 'search') { return json(response, 200, { results: retrieve(input.query || '', document.chunks, 10).map(({ token_set, ...value }) => value) }); }
    if (request.method === 'POST' && match[2] === 'translate') {
      const target = input.target === 'hi' ? 'hi' : 'en';
      if (input.scope === 'summary') { const translated=await translateText(document.summary.english,target); if (target === 'hi') { document.summary.hindi = translated.text; document.translation_error = null; } return json(response, 200, { translation: { document_id: document.id, target_language: target, scope: 'summary', text: translated.text, provider: translated.provider, quality: translated.quality, original_unchanged: true } }); }
      const pages=[];for(const page of document.pages){const translated=await translateText(page.text,target);pages.push({...page,text:translated.text,provider:translated.provider,quality:translated.quality})}
      return json(response, 200, { translation: { id: `tr_${document.id}_${target}`, document_id: document.id, target_language: target, source_language: document.document_language, provider: 'sarvam', original_unchanged: true, pages } });
    }
    return json(response, 405, { error: 'Method not allowed.' });
  } catch (error) {
    const status = error.status || (/limit|large/.test(error.message) ? 413 : 400);
    return json(response, status, { error: error.message, code: error.code || 'REQUEST_FAILED', provider: error.provider || undefined, status });
  }
}
