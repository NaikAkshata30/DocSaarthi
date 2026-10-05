# DocSaarthi

Bilingual legal and financial document intelligence. The original uploaded PDF is the only primary retrieval source; translations remain separate convenience representations.

## Run

```powershell
npm install
npm start
```

Open `http://localhost:4173`. PDF extraction, intent routing, retrieval, citations, safeguarded answers, and supported English/Hindi translations run locally. Translation uses `data/english-hindi-parallel.csv` as an offline translation memory, so no translation API key is required. Sentences outside that dataset are reported as unsupported rather than guessed. OpenAI remains an explicitly optional enhancement and is used only when `USE_OPENAI=true`.

The 400-row Hindi dataset is used only for supporting query-intent signals across Agreement, Confidentiality, Court Proceeding, Finance, General, Insurance, Loan, Payment, and Tax. It never supplies document facts.

```powershell
npm test
npm run dataset:inspect
```

For production, replace the in-memory repository with encrypted object storage plus a user-scoped database/vector index and authentication middleware. Scanned PDFs require a connected OCR provider.
