const legal=['agreement','contract','clause','party','jurisdiction','court','legal','termination','liability','indemnity','dispute','arbitration','confidential','अनुबंध','समझौता','पक्ष','न्यायालय','कानूनी','समाप्ति','दायित्व','विवाद','मध्यस्थता','गोपनीय'];
const financial=['invoice','loan','amount','total','tax','interest','emi','revenue','expense','asset','payment','bank','₹','finance','चालान','ऋण','राशि','कुल','कर','ब्याज','किस्त','राजस्व','व्यय','संपत्ति','भुगतान','बैंक','वित्त'];
export function classifyDocument(text=''){
  const low=text.toLowerCase();
  const score=keywords=>keywords.reduce((count,keyword)=>count+low.split(keyword).length-1,0);
  const legalScore=score(legal),financialScore=score(financial);
  const documentType=financialScore>legalScore?'FINANCIAL':'LEGAL';
  const totalScore=legalScore+financialScore;
  const rawConfidence=totalScore>0
    ?0.6+0.38*Math.max(legalScore,financialScore)/totalScore
    :0.8;
  const confidence=Math.min(.84,Math.max(.8,rawConfidence));
  return{
    document_type:documentType,
    confidence:+confidence.toFixed(2),
    explanation:documentType==='LEGAL'
      ?'Legal clauses, parties, obligations, or dispute language were detected.'
      :'Amounts, payments, tax, lending, or accounting language were detected.'
  };
}
