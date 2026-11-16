import {obterPosicao, erroLocalizacao} from './mobile.mjs';

// A consulta gratuita aceita somente o GPS atual do próprio aparelho, nunca pontos manuais ou rascunhos.
export async function localizarAtual(geolocation, signal, fetcher=fetch) {
  if(!geolocation)throw new Error('Localização indisponível. Marque o ponto no mapa ou preencha a referência.');
  let pos;
  try{pos=await obterPosicao(geolocation,signal);}
  catch(erro){throw new Error(erroLocalizacao(erro.code));}
  if(!pos||signal.aborted)return null;
  const {latitude,longitude,accuracy}=pos.coords;
  if(!Number.isFinite(latitude)||!Number.isFinite(longitude)||Math.abs(latitude)>90||Math.abs(longitude)>180) {
    throw new Error('O aparelho não retornou coordenadas válidas. Confira o ponto no mapa.');
  }
  const posicao={latitude,longitude,origem:'gps',precisao_m:Number.isFinite(accuracy)?Math.min(100000,Math.max(0,accuracy)):null};
  const referencia='Ponto GPS: '+latitude.toFixed(6)+', '+longitude.toFixed(6);
  const resultado={posicao,bairro:'',local:referencia,aviso:''};
  try {
    const url=new URL('https://api.bigdatacloud.net/data/reverse-geocode-client');
    url.search=new URLSearchParams({latitude,longitude,localityLanguage:'pt'});
    const r=await fetcher(url.href,{signal:AbortSignal.any([signal,AbortSignal.timeout(8000)]),credentials:'omit',referrerPolicy:'no-referrer'});
    if(!r.ok)throw new Error('consulta indisponível');
    const dados=await r.json();
    const texto=v=>typeof v==='string'?v.trim().slice(0,100):'';
    const regiao=texto(dados.locality)||texto(dados.city);
    if(!regiao)throw new Error('região não identificada');
    resultado.bairro=regiao;
    resultado.local=[...new Set([regiao,texto(dados.city),texto(dados.principalSubdivision),texto(dados.countryName)].filter(Boolean))].join(', ').slice(0,170)+' · '+referencia;
  } catch {
    if(signal.aborted)return null;
    resultado.aviso='O GPS foi obtido, mas a região não pôde ser consultada. Preencha o bairro e confira a referência.';
  }
  return signal.aborted?null:resultado;
}

export async function prepararAutomatico(analisar, localizar, signal) {
  const resultados=await Promise.allSettled([analisar(),localizar()]);
  if(signal.aborted)return null;
  const [foto,localizacao]=resultados.map(r=>r.status==='fulfilled'?r.value:null);
  const avisos=resultados.filter(r=>r.status==='rejected').map(r=>r.reason?.message||'Não foi possível completar a preparação.');
  if(localizacao?.aviso)avisos.push(localizacao.aviso);
  return {foto,localizacao,avisos};
}
