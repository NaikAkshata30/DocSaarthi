import fs from 'node:fs';
import path from 'node:path';
import { extractPdf } from '../src/services/document-service.js';
import { classifyDocument } from '../src/services/classification-service.js';
import { detectLanguage } from '../src/services/language-service.js';

const samples = [
  ['Financial_EN_01_Personal_Loan_Agreement.pdf', 'FINANCIAL', 'en'],
  ['Financial_EN_02_Bank_Account_Statement.pdf', 'FINANCIAL', 'en'],
  ['Financial_HI_01_Rin_Swikriti_Patra.pdf', 'FINANCIAL', 'hi'],
  ['Financial_HI_02_Masik_Bank_Vivaran.pdf', 'FINANCIAL', 'hi'],
  ['Legal_EN_01_Residential_Rent_Agreement.pdf', 'LEGAL', 'en'],
  ['Legal_EN_02_Employment_Service_Agreement.pdf', 'LEGAL', 'en'],
  ['Legal_HI_01_Awas_Kirayanama.pdf', 'LEGAL', 'hi'],
  ['Legal_HI_02_Seva_Anubandh.pdf', 'LEGAL', 'hi']
];

const sampleDirectory = path.resolve('output/pdf/test-pack');
const labels = ['LEGAL', 'FINANCIAL'];
const confusionMatrix = Object.fromEntries(
  labels.map(actual => [actual, Object.fromEntries(labels.map(predicted => [predicted, 0]))])
);
const results = [];

for (const [filename, expectedType, expectedLanguage] of samples) {
  const filePath = path.join(sampleDirectory, filename);
  const extracted = await extractPdf(fs.readFileSync(filePath));
  const classification = classifyDocument(extracted.text);
  const predictedLanguage = detectLanguage(extracted.text);

  confusionMatrix[expectedType][classification.document_type] += 1;
  results.push({
    filename,
    expected_type: expectedType,
    predicted_type: classification.document_type,
    type_correct: classification.document_type === expectedType,
    displayed_confidence: classification.confidence,
    expected_language: expectedLanguage,
    predicted_language: predictedLanguage,
    language_correct: predictedLanguage === expectedLanguage
  });
}

const safeDivide = (numerator, denominator) => denominator ? numerator / denominator : 0;
const metrics = {};

for (const label of labels) {
  const truePositive = confusionMatrix[label][label];
  const falsePositive = labels
    .filter(actual => actual !== label)
    .reduce((total, actual) => total + confusionMatrix[actual][label], 0);
  const falseNegative = labels
    .filter(predicted => predicted !== label)
    .reduce((total, predicted) => total + confusionMatrix[label][predicted], 0);
  const precision = safeDivide(truePositive, truePositive + falsePositive);
  const recall = safeDivide(truePositive, truePositive + falseNegative);
  const f1 = safeDivide(2 * precision * recall, precision + recall);

  metrics[label] = { precision, recall, f1 };
}

const correctTypes = results.filter(result => result.type_correct).length;
const correctLanguages = results.filter(result => result.language_correct).length;
const macroF1 = labels.reduce((total, label) => total + metrics[label].f1, 0) / labels.length;

console.log(JSON.stringify({
  evaluation_kind: 'labelled holdout benchmark for the rule-based classifier',
  warning: 'The bundled samples are synthetic and too small for a production accuracy claim.',
  sample_count: results.length,
  classification_accuracy: safeDivide(correctTypes, results.length),
  classification_accuracy_percent: 100 * safeDivide(correctTypes, results.length),
  macro_f1: macroF1,
  per_class: metrics,
  confusion_matrix: confusionMatrix,
  language_accuracy: safeDivide(correctLanguages, results.length),
  language_accuracy_percent: 100 * safeDivide(correctLanguages, results.length),
  results
}, null, 2));
