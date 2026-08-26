const clean=text=>text.replace(/\s+/g,' ').trim();
const value=(text,label)=>text.match(new RegExp(`${label}\\s+(?:₹|Rs\\.?|INR|n)?\\s*([\\d,]+(?:\\.\\d+)?%?(?:\\s+(?:fixed|months))?)`,'i'))?.[1];
const money=v=>v?`₹${v.replace(/^₹/,'')}`:null;
const section=(text,start,end)=>clean(text.match(new RegExp(`${start}\\s+([\\s\\S]*?)(?=${end}|$)`,'i'))?.[1]||'').replace(/\bn\s+(?=\d)/gi,'₹');
const general=q=>/(?:what is this document about|what does this document contain|overview|summari[sz]e|यह दस्तावेज़ किस बारे|दस्तावेज़ के बारे में|सारांश)/i.test(q);

export function structuredAnswer(question,document){
  const q=clean(question),text=clean(document.text||document.pages?.map(p=>p.text).join(' ')||'');
  if(/(?:pan\s*(?:number|नंबर)?|पैन\s*(?:नंबर)?)/i.test(q))return null;
  if(general(q))return document.summary?.english||section(text,'1\\. Parties','4\\. Late Payment')||null;
  if(/(?:principal|loan amount|amount borrowed|how much was borrowed|ऋण की राशि|मूल ऋण|मूलधन)/i.test(q)){const v=value(text,'Principal Amount');return v?`The principal loan amount is ${money(v)}.`:null}
  if(/(?:interest rate|ब्याज दर)/i.test(q)){const v=value(text,'Annual Interest Rate');return v?`The annual interest rate is ${v}.`:null}
  if(/(?:repayment period|loan period|tenure|ऋण की अवधि|पुनर्भुगतान अवधि)/i.test(q)){const v=value(text,'Tenure');return v?`The loan tenure is ${v}.`:null}
  if(/(?:first emi|पहली\s*emi|पहली किस्त)/i.test(q)){const v=text.match(/First EMI(?: Due Date)?\s+(.+?)(?=Final Scheduled|Processing Fee|\d+\.\s)/i)?.[1];return v?`The first EMI due date is ${clean(v)}.`:null}
  if(/(?:final due|final scheduled|अंतिम भुगतान|अंतिम देय)/i.test(q)){const v=text.match(/Final Scheduled Due Date\s+(.+?)(?=Processing Fee|Principal:|\d+\.\s)/i)?.[1];return v?`The final scheduled due date is ${clean(v)}.`:null}
  if(/(?:important dates|महत्वपूर्ण तिथ)/i.test(q)){const dates=document.important_dates?.map(x=>x.value).filter(Boolean)||[];return dates.length?`The important dates are ${dates.join(', ')}.`:null}
  if(/(?:late payment charge|late charge|देर से भुगतान.*शुल्क|विलंब.*शुल्क)/i.test(q)){const v=text.match(/late-payment charge of\s+(?:₹|Rs\.?|INR|n)?\s*([\d,]+)/i)?.[1]||value(text,'Late Charge');return v?`A late-payment charge of ${money(v)} may be applied, subject to applicable law and the lender's policies.`:null}
  if(/(?:misses a payment|missed payment|payment.*fail|भुगतान करने में विफल|भुगतान.*चूक)/i.test(q))return section(text,'4\\. Late Payment','5\\. Prepayment')||null;
  if(/(?:repay.*early|early repayment|prepayment|समय से पहले|पूर्व भुगतान)/i.test(q))return section(text,'5\\. Prepayment','6\\. Default')||null;
  if(/(?:event of default|in the event of default|default|डिफ़ॉल्ट|चूक की स्थिति)/i.test(q))return section(text,'6\\. Default','7\\. Confidentiality')||null;
  if(/(?:which law|governing law|law governs|कौन सा कानून|कानून लागू)/i.test(q))return section(text,'8\\. Governing Law','9\\. Important Dates')||null;
  if(/(?:payment obligations|repayment schedule|भुगतान संबंधी|भुगतान की जिम्मेदार|पुनर्भुगतान)/i.test(q))return section(text,'3\\. Repayment','4\\. Late Payment')||null;
  return null;
}
