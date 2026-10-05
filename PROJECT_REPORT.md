# DocSaarthi — Complete Project Report

**Report date:** 4 October 2026  
**Project version:** 1.0.0 prototype  
**Repository:** `DocSaarthi`  
**Runtime:** Node.js 20 or newer  

## 1. Executive summary

DocSaarthi is a bilingual, source-grounded document-intelligence web application for legal and financial PDF documents. A user uploads a PDF, after which the system extracts its embedded text page by page, detects its language, classifies the document as legal or financial, identifies important dates and monetary values, surfaces potentially important clauses and risk signals, and creates a searchable evidence index. The user can then read a generated summary, inspect structured facts, ask questions in English or Hindi, receive answers in English, Hindi, or both, and see citations back to the original document pages.

The project's central design principle is that the uploaded document remains the authoritative source. Translation is treated as a separate convenience layer, and the intent-classification dataset is used only to improve question routing—not as evidence for an answer. If requested information cannot be found with adequate confidence, the application is designed to abstain instead of inventing a response.

The current product is a functioning local prototype. PDF extraction, heuristic analysis, cross-language retrieval, citations, document chat, and the responsive user interface work. Hindi translation uses Sarvam's hosted translation API. OpenAI is an optional enhancement for grounded answer generation and is disabled unless explicitly enabled. The prototype does not yet have user accounts, durable document storage, authorization, production-grade vector search, OCR, audit history, or production deployment controls.

## 2. Problem being solved

Legal and financial documents are often long, technical, and difficult to understand, especially when the reader is more comfortable in a language different from the document's language. Important details such as payment obligations, dates, penalties, termination clauses, interest rates, or legal jurisdiction may be buried in dense text.

DocSaarthi addresses this by providing:

- Fast extraction of information from legal and financial PDFs.
- A clear, structured summary instead of requiring repeated manual reading.
- English and Hindi interaction.
- Cross-language retrieval, so a Hindi question can retrieve English evidence and vice versa.
- Page-level evidence for verification.
- An explicit separation between authoritative original text and translated text.
- A safe "not found" answer when evidence is missing.
- A visible disclaimer that the output is informational and is not professional legal, financial, or tax advice.

## 3. Intended users and use cases

### Intended users

- Individuals reviewing loan agreements, contracts, invoices, or financial records.
- Hindi-speaking users who need help reading English documents.
- English-speaking users working with Hindi documents.
- Students or researchers demonstrating multilingual NLP and retrieval-augmented generation.
- Early-stage legal-tech or fintech teams evaluating document-intelligence workflows.

### Main use cases

1. Upload and analyze a legal agreement.
2. Upload and analyze a financial or loan document.
3. Extract important amounts, percentages, and dates.
4. Identify clauses about payment, default, termination, confidentiality, liability, indemnity, renewal, or disputes.
5. Ask a natural-language question about the uploaded document.
6. Ask in one language and retrieve evidence written in the other.
7. Generate a separate Hindi or English reading copy.
8. Review page-level excerpts supporting an answer.
9. Receive an explicit not-found response for unsupported facts such as a missing identifier.

## 4. Product capabilities currently implemented

### 4.1 PDF upload and validation

The application accepts PDF files through file selection or drag and drop. It validates:

- File extension is `.pdf`.
- MIME type is `application/pdf` when supplied.
- File is not empty.
- File is within the configured size limit, which defaults to 20 MB.
- File begins with the `%PDF-` signature.

The browser converts the complete file to Base64 and sends it inside a JSON request to the backend.

### 4.2 PDF text extraction

`pdfjs-dist` reads the uploaded file in memory. The application:

- Extracts text from every page.
- Preserves the page number for each text block.
- Normalizes repeated spaces and excess line breaks.
- Joins the page texts into a document-wide text representation.
- Records the page count and extraction method.

Only PDFs with embedded text are supported. If less than a minimal amount of extractable text is found, the system treats the file as a scanned PDF and reports that OCR is required. Corrupt, encrypted, or unsupported PDFs return a readable error.

### 4.3 Language detection

The language detector counts Devanagari and Latin-script characters:

- At least 72% Devanagari: Hindi (`hi`).
- At most 18% Devanagari: English (`en`).
- Between those thresholds: mixed language (`mixed`).
- No recognized characters: unknown.

This is a lightweight script-based detector, not a full statistical language-identification model.

### 4.4 Legal/financial classification

The classifier counts bilingual legal and financial keywords. Legal signals include terms related to agreements, clauses, courts, termination, liability, indemnity, disputes, arbitration, and confidentiality. Financial signals include invoices, loans, amounts, tax, interest, EMI, revenue, expenses, assets, payments, and banking.

The larger score determines one of two classes:

- `LEGAL`
- `FINANCIAL`

A calculated confidence value is returned with a short explanation. With no recognizable signals, the current implementation defaults to `LEGAL` with 55% confidence.

### 4.5 Document intelligence extraction

After extraction and classification, the system derives:

- English summary.
- Hindi summary placeholder, filled only when translation is requested.
- Document type and document language.
- Important dates in numeric, English-month, or Hindi-month formats.
- Important monetary values and percentages.
- Up to eight relevant clauses.
- Up to five attention/risk signals.
- Page numbers and excerpts for extracted values and clauses.

The initial summary is extractive and heuristic. It prioritizes sentences containing words associated with termination, renewal, confidentiality, liability, indemnity, disputes, payments, and penalties, then fills any remaining summary space with early document sentences.

Risk levels are also heuristic:

- `HIGH` for penalty, liability, or indemnity-related language.
- `MEDIUM` for termination or renewal-related language.
- `LOW` for other selected clauses.

These levels are attention indicators, not legal risk assessments.

### 4.6 Evidence chunking

Each page is split into sentence groups of approximately 700 characters. Every evidence chunk contains:

- Unique chunk ID.
- Document ID and filename.
- Original page number.
- Detected section/clause number when present.
- Document language and type.
- Original extracted text.
- Normalized bilingual search tokens.

Chunk boundaries never intentionally cross page boundaries, preserving page-level citation accuracy.

### 4.7 Cross-language retrieval

Search uses lexical matching rather than embeddings. A bilingual synonym map expands concepts such as:

- termination / समाप्ति
- notice / सूचना
- payment / भुगतान
- amount / राशि
- EMI / किस्त
- interest / ब्याज
- default / चूक
- charge / शुल्क
- court / न्यायालय
- agreement / समझौता
- confidentiality / गोपनीयता-related roots

Stop words are removed, tokens are normalized with Unicode NFKC, and chunks are ranked by token overlap. Exact full-question containment receives a strong score boost. General summary questions return the earliest chunks because the beginning of a document commonly contains identifying and introductory information.

Question-specific query expansion improves retrieval for penalties, late payments, repayment obligations, defaults, court jurisdiction, governing law, tax, insurance, confidentiality, agreements, and loans.

### 4.8 Intent dataset

The application loads a Hindi NLP CSV dataset from the configured local path. The verified dataset contains 400 samples with columns `ID`, `Text`, and `Intent`.

| Intent | Samples |
|---|---:|
| Agreement | 40 |
| Payment | 20 |
| Court Proceeding | 80 |
| Confidentiality | 40 |
| General | 60 |
| Finance | 100 |
| Loan | 20 |
| Tax | 20 |
| Insurance | 20 |
| **Total** | **400** |

Sample text length ranges from 60 to 149 characters, with a 98.6-character average. The runtime builds a small keyword model by counting frequent normalized tokens in each intent group. Detected intent can add retrieval terms, but the dataset never provides document facts or answer content.

If the dataset cannot be read, the application continues with zero dataset samples and an empty intent model.

### 4.9 Grounded question answering

The chat workflow is:

1. Detect greetings and thanks and answer them without document retrieval.
2. Detect the question's language.
3. Detect its likely intent using the dataset-assisted keyword model.
4. Expand the retrieval query where useful.
5. Retrieve up to five evidence chunks from the uploaded document.
6. Optionally ask OpenAI for a concise English answer using only those chunks.
7. If OpenAI is disabled or fails, use structured rules or an extractive evidence fallback.
8. Translate the answer when the requested response language requires it.
9. Return original-page citations.
10. Abstain when evidence is absent or too weak.

The optional OpenAI prompt explicitly instructs the model to use evidence only, preserve names, values, dates, identifiers, and clause references, avoid invented facts, and return strict JSON. OpenAI failures do not stop the full application; the response includes an `ai_status` error and falls back to local evidence logic.

### 4.10 Structured answers

Dedicated rules attempt concise answers for common loan-document questions, including:

- Principal amount.
- Annual interest rate.
- Loan tenure.
- First EMI due date.
- Final scheduled due date.
- Important dates.
- Late-payment charge.
- Penalties and risks.
- Missed payments.
- Prepayment.
- Events of default.
- Governing law.
- Payment obligations.

PAN-number questions deliberately abstain if PAN evidence is absent, even if general borrower content was retrieved.

### 4.11 Answer language behavior

The user may request:

- English only.
- Hindi only.
- Both languages.

For bilingual answers, the default display order depends on question language:

- English question: Hindi first, then English.
- Hindi question: English first, then Hindi.

The application checks whether returned Hindi is genuinely Devanagari-heavy. If it is not, it requests a new Hindi translation instead of displaying a mostly English or Hinglish result.

### 4.12 Translation

The implemented translation provider is Sarvam using model `sarvam-translate:v1` in formal mode. Supported directions are English-to-Hindi and Hindi-to-English.

The translation layer:

- Splits long text into provider-safe chunks of no more than about 1,900 characters.
- Prefers sentence boundaries, then semicolons, commas, or spaces.
- Processes chunks in order.
- Caches up to 100 completed translations in memory.
- Deduplicates simultaneous identical translation requests.
- Returns specific errors for missing credentials, authentication failure, forbidden access, validation errors, rate limits, server failure, empty responses, and network failure.

For Hindi output, quality validation checks:

- A minimum amount of Devanagari text.
- Excessive untranslated English words.
- Preservation of protected values such as amounts, percentages, dates, PAN, TDS, IFSC, RBI, SEBI, GST, URLs, and uppercase identifiers.

The full-document translation endpoint translates every extracted page separately and labels the result as a non-authoritative representation. The original stored bytes and original extracted text remain unchanged.

### 4.13 Citations and abstention

Each cited source includes:

- Chunk ID.
- Page number.
- Section label, when detected.
- Original excerpt, limited to 260 characters in the API.
- Retrieval score.

The frontend currently displays page number, section, and a shortened excerpt. For penalty/risk and repayment questions, citation selection is narrowed to the most relevant sentences.

If evidence is missing, below threshold, or lacks a specifically requested PAN identifier, the system returns:

> I couldn't find this information in the uploaded document.

and its Hindi equivalent. In this state, citations are empty and `grounded` is false.

## 5. User interface and user journey

### 5.1 Public landing page

The marketing page explains four capabilities:

1. Understand through natural questions and evidence.
2. Notice dates, amounts, clauses, and attention signals.
3. Translate while preserving the original as authority.
4. Trace answers to pages, sections, and excerpts.

It also explains the four-stage method: extract, interpret, retrieve, and explain.

### 5.2 Documents page

The library view shows:

- Total analyzed documents.
- Legal and financial counts.
- Supported language count.
- Filename, analysis date, page count, chunk count, type, language, and readiness status.

Because storage is in memory, this list lasts only for the current backend process.

### 5.3 Dashboard/overview

An overview route presents current-document metrics and shortcuts for upload, chat, insights, and translation. It exists in code but is not currently included in the sidebar navigation.

### 5.4 Upload page

The upload page supports:

- File picker.
- Drag and drop.
- Processing state with progress copy and skeleton animation.
- Success and error toast messages.
- Automatic navigation to the new document workspace.

### 5.5 Document workspace

The workspace has three main views:

- **Original document:** page-separated extracted text labeled as authoritative.
- **Intelligence:** summary, bilingual facts, amounts, dates, attention signals, and translation action.
- **Ask DocSaarthi:** bilingual question answering with citations.

The summary can be viewed in English, Hindi, or both. A Hindi summary is translated only when first needed, keeping upload fast and independent from the translation provider.

### 5.6 Responsive design

The application includes desktop, tablet, and mobile layouts. On smaller screens:

- The fixed sidebar becomes a bottom navigation bar.
- Multi-column grids collapse.
- Document facts and bilingual summaries stack vertically.
- Workspace panels use flexible heights.

### 5.7 Interface elements that are present but not yet functional

- Global search button.
- Notification button.
- Workspace settings menu.
- Public mobile menu button.
- Language preference chip on the public navigation.

The backend has a document search endpoint, but the UI does not currently expose it.

## 6. Technical architecture

```text
Browser (HTML/CSS/vanilla JavaScript)
        |
        | JSON over same-origin HTTP
        v
Node.js HTTP server and REST-like API
        |
        +--> Upload validation
        +--> pdfjs-dist text extraction
        +--> Language and domain classification
        +--> Heuristic intelligence extraction
        +--> Page-bound evidence chunking
        +--> In-memory Map repository
        +--> Lexical bilingual retrieval
        +--> Local structured/extractive answers
        +--> Optional OpenAI grounded generation
        +--> Sarvam hosted translation
```

### Frontend

- Single HTML shell.
- Vanilla JavaScript single-page routing using the History API.
- Server-rendered static assets only; all dynamic UI is built in the browser.
- No frontend framework or build step.
- Responsive custom CSS.
- User-supplied and document-supplied values are HTML-escaped before insertion into most dynamic templates.

### Backend

- Native Node.js `http` server.
- Native `fetch` for external AI services.
- Static file serving from `public`.
- API routing in a single handler.
- In-memory `Map` for documents.
- One runtime dependency: `pdfjs-dist` (with its transitive canvas packages).

### External services

- **Sarvam:** required for English/Hindi translation features.
- **OpenAI:** optional for higher-quality grounded answer generation when `USE_OPENAI=true` and a key is supplied.

## 7. API reference

### `GET /api/health`

Returns application health, Sarvam configuration status, dataset sample count and intent distribution, and the disclaimer.

### `GET /api/documents`

Returns in-memory document metadata and analysis results, excluding original bytes, full text, page text, and internal chunks.

### `POST /api/documents`

Accepts JSON containing:

- `name`
- `type`
- `data` as Base64 PDF content

Returns the created document with page text, classification, summary, extracted fields, dates, amounts, clauses, risks, chunk count, and disclaimer.

### `GET /api/documents/:id`

Returns one document's public analysis representation, including page text but excluding PDF bytes, full joined text, and internal tokenized chunks.

### `POST /api/documents/:id/chat`

Accepts:

- `question`
- `response_language`: `en`, `hi`, or `both`

Returns detected question language, answer order, answer text, intent, citations, grounded state, conversation state, and optional AI-provider status.

### `POST /api/documents/:id/search`

Accepts a query and returns up to ten ranked document chunks. Internal token sets are removed from the response.

### `POST /api/documents/:id/translate`

Accepts:

- `target`: `hi` or `en`
- Optional `scope: "summary"`

Returns either a translated summary or translated page representations. The response explicitly states that the original remains unchanged.

## 8. Core data model

An in-memory document contains approximately:

- Identity: ID and filename.
- Upload: original bytes and creation timestamp.
- Processing: `READY` status and extraction method.
- Language and type: detected language, classification, confidence, and explanation.
- Source: pages, complete text, and page count.
- Retrieval: chunks and normalized token sets.
- Intelligence: summaries, key information, dates, amounts, clauses, and risks.
- Translation: lazy Hindi summary and translation error state.

There is no persisted user, session, permission, conversation, or audit-event model yet.

## 9. Configuration

| Environment variable | Purpose | Default/behavior |
|---|---|---|
| `PORT` | HTTP listening port | `4173` |
| `MAX_FILE_MB` | Upload-size limit | `20` MB |
| `SARVAM_API_KEY` | Enables translation | Required for translation |
| `USE_OPENAI` | Enables OpenAI answer enhancement | Must equal `true` |
| `OPENAI_API_KEY` | OpenAI credential | Ignored unless OpenAI is enabled |
| `OPENAI_MODEL` | OpenAI Responses API model | `gpt-5-mini` |
| `HINDI_NLP_DATASET` | Intent CSV path | Developer-machine path in current default |

Commands:

```powershell
npm install
npm start
npm run dev
npm test
npm run dataset:inspect
```

## 10. Verified runtime results

Verification performed on 4 October 2026:

- All **17 automated tests passed**.
- Health endpoint returned `ok: true`.
- Sarvam configuration was detected.
- The 400-row intent dataset loaded successfully.
- Both included sample PDFs uploaded and completed analysis successfully.

### Financial sample

| Result | Value |
|---|---|
| File | `DocSaarthi_Sample_Financial_Loan.pdf` |
| Pages | 2 |
| Detected language | English |
| Classification | Financial |
| Confidence | 89% |
| Evidence chunks | 7 |
| Extracted values | INR 5,00,000; 9.50%; INR 16,026; INR 5,000; INR 500; 2% |
| Extracted dates | 10 Oct 2026; 15 Oct 2026; 5 Nov 2026; 5 Oct 2029 |
| Risk signals | 5 |
| Grounded Q&A | Passed, with citations to pages 1 and 2 |

### Legal sample

| Result | Value |
|---|---|
| File | `DocSaarthi_Sample_Legal_Agreement.pdf` |
| Pages | 2 |
| Detected language | English |
| Classification | Legal |
| Confidence | 92% |
| Evidence chunks | 8 |
| Extracted values | INR 75,000; 1%; INR 2,25,000 |
| Extracted dates | 15 Oct 2026 |
| Relevant clauses | 8 |
| Risk signals | 5 |

### Automated test coverage

The test suite verifies:

- English and Hindi language detection.
- Answer display order by question language.
- Legal and financial classification.
- English-to-Hindi and Hindi-to-English retrieval.
- Source page preservation.
- Abstention for unknown answers.
- Rejection of low-quality Hinglish translation.
- Preservation of names, amounts, percentages, and dates.
- Grounded local fallback plus translated Hindi answer.
- Deferred translation during upload.
- Safe chunking of long translation input.
- Handling of PDF line breaks.
- Preservation of Devanagari combining marks.
- Equivalent Hindi rupee wording.
- PAN-specific abstention.

## 11. Privacy, trust, and security model

### Implemented safeguards

- The original upload remains separate from translations.
- Intent dataset content cannot become answer evidence.
- AI generation is instructed to use retrieved evidence only.
- Missing answers can produce an explicit abstention.
- External-provider errors are normalized and surfaced without provider secrets.
- OpenAI is opt-in through configuration.
- PDF parsing disables PDF JavaScript evaluation.
- Static responses set `X-Content-Type-Options: nosniff`.
- API responses use `Cache-Control: no-store`.
- The UI escapes dynamic text before rendering.
- The application includes a professional-advice disclaimer.

### Important privacy facts

- Uploaded PDF bytes and extracted document content are kept in server memory for the lifetime of the process.
- A translation request sends the relevant extracted text to Sarvam.
- If OpenAI is enabled, retrieved evidence excerpts and the user's question are sent to OpenAI.
- There is no database encryption because there is no database yet.
- There is no authentication or per-user authorization.
- The phrases “private workspace” and “content is not logged” are product statements, not a complete production security boundary.

## 12. Current limitations and gaps

### Product limitations

- Only PDF upload is supported.
- Scanned/image-only PDFs require an OCR provider.
- The "original PDF" view is extracted text arranged by page, not a pixel-faithful PDF renderer.
- Only two broad classification types exist.
- No manual correction of classification or extracted fields.
- No deletion, export, sharing, or report-generation endpoint.
- No side-by-side original/translation page view.
- No click-to-jump from a citation to the cited page.
- No persistent chat history.
- History is a reused document list rather than a true activity log.

### Retrieval and intelligence limitations

- Retrieval is lexical; there are no embeddings, vector database, semantic reranking, or learned cross-encoder.
- Synonym coverage is manually curated and limited.
- Classification, summaries, clauses, and risks are keyword/regex heuristics.
- Attention levels should not be interpreted as verified legal risk.
- Structured answer rules are tailored to particular wording and loan-document layouts.
- Some source excerpts may be broad because citations refer to chunks rather than exact character spans.
- General questions prioritize early chunks, which may miss later central provisions.
- Intent CSV parsing uses a simplified regular expression and is not a fully robust CSV parser.

### Engineering limitations

- All state is lost when the process stops.
- Documents are not isolated by user.
- The whole Base64 PDF request is buffered in memory; Base64 also increases request size by roughly one third.
- Full-document translation is sequential and may be slow for long PDFs.
- Translation cache is process-local and has no time-to-live.
- No rate limiting, authentication, role-based access, quotas, malware scanning, or audit trail.
- No background-job queue for extraction or translation.
- No structured observability, metrics, tracing, or health checks for dependencies.
- No API schema validation library or OpenAPI specification.
- No end-to-end browser tests or direct API integration tests.
- No CI/CD workflow is present.
- No production container or deployment configuration is present.
- The default dataset path points to a specific developer machine and must be changed for portability.

### Consistency issues to correct

- The frontend says “local translation” and “running the local translation model,” but current translation code calls Sarvam's hosted API.
- Downloaded transformer models exist in `.models`, but the running application does not import or use them.
- The UI states that citations always point to original pages; the page numbers are correct, but the "original" view is extracted text rather than the original visual PDF.
- The package manifest allows `pdfjs-dist` updates under a caret range; the installed dependency tree currently reports a newer compatible release than the manifest's minimum.

### Repository status

- The repository contains one recorded commit in the inspected history.
- Many core files currently have uncommitted modifications.
- The generated `output` directory is currently untracked and is not covered by `.gitignore`.
- Secrets are correctly excluded through `.env` in `.gitignore`; `.env.example` contains names only.

## 13. Production-readiness roadmap

### Priority 1 — data isolation and durable storage

1. Add authentication and user/workspace ownership.
2. Store PDFs in encrypted object storage.
3. Store metadata, analyses, conversations, and permissions in a database.
4. Use a user-scoped vector index.
5. Add deletion and retention controls.
6. Replace Base64 JSON upload with streaming multipart upload and strict server-side limits.

### Priority 2 — document fidelity and processing

1. Add a real PDF viewer with page navigation and citation deep links.
2. Add OCR for scanned and photographed documents.
3. Move extraction, OCR, indexing, and long translations to background jobs.
4. Add processing states such as queued, extracting, indexing, ready, and failed.
5. Add checksum-based deduplication and retry-safe processing.

### Priority 3 — intelligence quality

1. Replace or complement lexical search with multilingual embeddings.
2. Add hybrid lexical/vector retrieval and reranking.
3. Create document-type-specific extraction schemas.
4. Add evaluation datasets for answer correctness, citation faithfulness, translation quality, and abstention.
5. Calibrate confidence scores from measured performance rather than keyword ratios.
6. Distinguish "attention signal" from professionally reviewed legal/financial risk.

### Priority 4 — privacy and security

1. Publish clear external-provider data-flow disclosures.
2. Add consent and organization controls for Sarvam/OpenAI processing.
3. Add encryption in transit and at rest, key management, and secret rotation.
4. Add rate limiting, security headers, CSRF strategy, content scanning, and audit logs.
5. Add dependency scanning, SAST, threat modeling, penetration testing, and incident response procedures.
6. Define regional storage, retention, deletion, and compliance requirements.

### Priority 5 — product completeness

1. Implement global search and document-level search UI.
2. Implement real history and audit activity.
3. Add report export in PDF/DOCX formats.
4. Add side-by-side original and translation views.
5. Add field correction, notes, bookmarks, and saved questions.
6. Add document comparison and clause-difference workflows.
7. Add accessibility testing and keyboard/screen-reader refinements.

### Priority 6 — engineering operations

1. Refactor compressed one-line source files for maintainability.
2. Add schema validation, structured logging, monitoring, and tracing.
3. Add unit, integration, API, security, and browser end-to-end tests.
4. Add CI/CD, reproducible deployment, environment documentation, and rollback strategy.
5. Pin and regularly review dependency versions.

## 14. Source-code map

| File | Responsibility |
|---|---|
| `src/server.js` | Native HTTP server, static file serving, SPA fallback |
| `src/api.js` | API routes and orchestration |
| `src/config.js` | Environment configuration and disclaimer |
| `src/store.js` | In-memory document repository |
| `src/services/document-service.js` | Upload validation and PDF extraction |
| `src/services/language-service.js` | Script-based language detection and answer ordering |
| `src/services/classification-service.js` | Legal/financial keyword classification |
| `src/services/intelligence-service.js` | Summaries, fields, dates, amounts, clauses, and risks |
| `src/services/rag-service.js` | Chunking, lexical retrieval, and citation formatting |
| `src/services/intent-service.js` | Dataset loading, intent detection, and query expansion |
| `src/services/question-context-service.js` | Structured answers for common document questions |
| `src/services/ai-service.js` | Optional OpenAI generation, fallback answers, bilingual output |
| `src/services/translation-service.js` | Sarvam translation, chunking, caching, errors, and quality checks |
| `src/utils/text.js` | Unicode normalization, stop words, bilingual synonyms |
| `public/index.html` | Application shell and navigation containers |
| `public/app.js` | SPA routes, views, state, upload, chat, and translation interactions |
| `public/styles.css` | Visual system and responsive layouts |
| `test/core.test.js` | Core behavior tests |
| `scripts/inspect-dataset.js` | Dataset distribution inspection |
| `output/pdf/*.pdf` | Two sample documents for demonstration/testing |

## 15. Report-ready project description

> DocSaarthi is a bilingual legal and financial document-intelligence prototype that converts uploaded PDFs into structured, verifiable insights. It extracts page-level text, detects English, Hindi, or mixed content, classifies documents, identifies important dates and amounts, surfaces relevant clauses and attention signals, and builds a bilingual retrieval index. Users can ask questions in English or Hindi and receive grounded answers with citations to the original pages. Translation is kept separate from the authoritative source, and the system abstains when evidence is insufficient. The prototype uses Node.js, vanilla JavaScript, pdfjs-dist, a 400-sample Hindi intent dataset, Sarvam translation, and an optional OpenAI grounded-generation layer. Its present architecture is suitable for demonstration and evaluation; production use requires authentication, durable encrypted storage, OCR, user-scoped retrieval, monitoring, stronger security controls, and measured model-quality evaluation.

## 16. Suggested presentation/demo flow

1. Introduce the problem: dense legal/financial documents and language barriers.
2. Explain the source-of-truth principle.
3. Upload the included financial loan sample.
4. Show classification, page count, dates, amounts, and attention signals.
5. Ask, “What is the principal loan amount?”
6. Show the grounded answer and page citations.
7. Ask a Hindi question about penalties or risk.
8. Switch the summary between English, Hindi, and both.
9. Create a translated representation and emphasize that it does not replace the original.
10. Ask for a missing PAN number to demonstrate safe abstention.
11. Close with the production roadmap and privacy architecture.

## 17. Final assessment

DocSaarthi already demonstrates the complete conceptual loop of document intelligence: upload, extract, interpret, retrieve, answer, translate, cite, and abstain. Its strongest qualities are the explicit source-of-truth design, bilingual retrieval, page-preserving evidence, deferred translation, value-preservation checks, graceful OpenAI fallback, and a polished responsive interface.

The main distinction for any formal report is that this is a well-functioning prototype rather than a production system. The intelligence layer is primarily heuristic and lexical, storage is process-local, translations use a hosted provider, and there is no security boundary between users. With the roadmap above, the prototype can evolve into a production-ready multilingual document-analysis platform.
