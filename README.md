# DocSaarthi

Bilingual legal and financial document intelligence. The original uploaded PDF is the only primary retrieval source; translations remain separate convenience representations.

## Run

```powershell
npm install
npm start
```

Open `http://localhost:4173`. `OPENAI_API_KEY` is optional: without it, local extraction, hybrid lexical retrieval, citations, intent hints and safeguarded answers work; with it, fluent bilingual synthesis and translation are enabled.

The 400-row Hindi dataset is used only for supporting query-intent signals across Agreement, Confidentiality, Court Proceeding, Finance, General, Insurance, Loan, Payment, and Tax. It never supplies document facts.

```powershell
npm test
npm run dataset:inspect
```

For production, replace the in-memory repository with encrypted object storage plus a user-scoped database/vector index and authentication middleware. Scanned PDFs require a connected OCR provider.
