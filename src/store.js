const docs=new Map();export const store={set:d=>(docs.set(d.id,d),d),get:id=>docs.get(id),list:()=>[...docs.values()].map(({bytes,chunks,text,pages,...x})=>({...x,chunk_count:chunks.length}))};
