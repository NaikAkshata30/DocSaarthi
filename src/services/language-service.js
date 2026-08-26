export function detectLanguage(text=''){const hi=(text.match(/[\u0900-\u097F]/g)||[]).length,en=(text.match(/[A-Za-z]/g)||[]).length,total=hi+en;if(!total)return'unknown';const ratio=hi/total;return ratio>=.72?'hi':ratio<=.18?'en':'mixed'}
export const answerOrder=lang=>lang==='en'?['hi','en']:['en','hi'];
