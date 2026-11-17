async page=>{
 await page.addInitScript(()=>{
   window.__iotTracks=[];window.__iotContexts=[];
   const obter=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
   navigator.mediaDevices.getUserMedia=async p=>{const s=await obter(p);window.__iotTracks.push(...s.getTracks());return s;};
   const AC=window.AudioContext;window.AudioContext=class extends AC{constructor(...a){super(...a);window.__iotContexts.push(this);}};
 });
 await page.reload();
 const envios=[];page.on('request',r=>{if(r.method()!=='GET')envios.push({url:r.url(),method:r.method()});});
 await page.locator('#ouviai-iniciar').click();
 await page.waitForFunction(()=>document.querySelector('#ouviai-microfone-status').textContent.startsWith('Escutando'),{timeout:60000});
 await page.waitForFunction(()=>document.querySelector('#ouviai-eventos').textContent.includes('Microfone · YAMNet'),{timeout:15000});
 const reconhecimento=await page.locator('#ouviai-eventos').textContent();
 await page.locator('#ouviai-parar').click();
 await page.waitForFunction(()=>window.__iotTracks.every(t=>t.readyState==='ended')&&window.__iotContexts.every(c=>c.state==='closed'));
 await page.locator('#ouviai-iniciar').click();
 await page.waitForFunction(()=>window.__iotTracks.length>=2);
 await page.locator('.main-nav [data-view="acompanhar"]').click();
 await page.waitForFunction(()=>window.__iotTracks.every(t=>t.readyState==='ended')&&window.__iotContexts.every(c=>c.state==='closed'));
 await page.evaluate(()=>location.hash='ouviai');
 await page.locator('#ouviai-iniciar').waitFor({state:'visible'});
 const resultados={reconhecimento,recursosEncerrados:await page.evaluate(()=>({tracks:window.__iotTracks.map(t=>t.readyState),contextos:window.__iotContexts.map(c=>c.state)})),envios};
 if(envios.length)throw new Error('Houve upload inesperado durante a escuta.');
 const layouts=[];
 for(const width of [360,390,768,1440]){
   await page.setViewportSize({width,height:844});
   layouts.push(await page.evaluate(()=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,ativar:document.querySelector('#ouviai-iniciar').getBoundingClientRect().width})));
 }
 if(layouts.some(x=>x.overflow||x.ativar<44))throw new Error('Layout inadequado.');
 resultados.layouts=layouts;return resultados;
}
