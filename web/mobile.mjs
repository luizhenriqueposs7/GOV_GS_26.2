export async function abrirCamera(dispositivos, signal) {
  if(signal.aborted)return null;
  const captura=dispositivos.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false}).then(stream=>{
    if(signal.aborted){stream.getTracks().forEach(t=>t.stop());return null;}
    return stream;
  });
  let cancelar;
  const cancelada=new Promise(resolve=>{cancelar=()=>resolve(null);signal.addEventListener('abort',cancelar,{once:true});});
  try{return await Promise.race([captura,cancelada]);}
  finally{signal.removeEventListener('abort',cancelar);}
}

export function obterPosicao(geolocation, signal) {
  if(signal.aborted)return Promise.resolve(null);
  let cancelar;
  const espera=new Promise((resolve,reject)=>{
    cancelar=()=>resolve(null);signal.addEventListener('abort',cancelar,{once:true});
    geolocation.getCurrentPosition(resolve,reject,{enableHighAccuracy:true,timeout:20000,maximumAge:0});
  });
  return espera.finally(()=>signal.removeEventListener('abort',cancelar));
}

export function erroLocalizacao(codigo) {
  return ({1:'A permissão de localização foi bloqueada. Ative-a nas configurações do site ou marque o ponto no mapa.',
    2:'A posição do aparelho está indisponível. Tente novamente ou marque o ponto no mapa.',
    3:'O GPS demorou para responder. Tente novamente ou marque o ponto no mapa.'})[codigo] || 'Não foi possível obter a localização. Use o mapa ou preencha o local manualmente.';
}

export function coordenadas(latitude, longitude, confirmado, origem = 'manual', precisao = null) {
  if (!latitude.trim() && !longitude.trim()) return null;
  if (!latitude.trim() || !longitude.trim()) throw new Error('Preencha as duas coordenadas ou deixe ambas vazias.');
  const lat = Number(latitude.replace(',', '.')), lon = Number(longitude.replace(',', '.'));
  if (!Number.isFinite(lat) || !Number.isFinite(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180) {
    throw new Error('Informe coordenadas válidas: latitude entre -90 e 90 e longitude entre -180 e 180.');
  }
  if (!confirmado) throw new Error('Confira e confirme que as coordenadas correspondem ao local do problema.');
  return {latitude: lat, longitude: lon, origem, precisao_m: precisao, confirmado: true};
}

export function dadosRascunho(dados) {
  return Object.fromEntries(['descricao', 'bairro', 'local', 'contexto', 'latitude', 'longitude', 'passagem-trecho', 'passagem-condicao']
    .map(k => [k, String(dados[k] || '')]));
}

export function criarRascunho(campos, estado) {
  const {foto, origemGeo, precisaoGeo, envioId, assinatura, rascunhoId, previaFoto, regiaoAuto} = estado;
  return {id:rascunhoId, campos:dadosRascunho(campos), foto, origemGeo, precisaoGeo,
    envioId, assinatura, previaFoto, regiaoAuto, salvoEm:new Date().toISOString()};
}

export function vinculoPassagem(trecho, condicao) {
  if(!trecho)return null;
  if(!['acesso','calcada','rampa','entrada'].includes(trecho))throw new Error('Confira o trecho do percurso.');
  if(!['bloqueado','dificultado','nao_verificado'].includes(condicao))throw new Error('Informe a condição da passagem.');
  return {percurso_id:'ponto-ubs-demo',trecho_id:trecho,condicao};
}

export function assinaturaPedido(dados) {
  const {passagem,...semVinculo}=dados;
  return JSON.stringify(passagem?dados:semVinculo);
}

export function mesmoRascunho(salvo, id) {return Boolean(id && salvo?.id === id);}

const bloqueios=new WeakMap();
export async function bloquearDurante(controles, acao) {
  const entradas=controles.map(n=>{
    let estado=bloqueios.get(n);
    if(!estado){estado={ativos:0,anterior:n.disabled};bloqueios.set(n,estado);}
    estado.ativos++;n.disabled=true;return [n,estado];
  });
  try {return await acao();}
  finally {entradas.forEach(([n,estado])=>{estado.ativos--;n.disabled=estado.ativos>0||estado.anterior;if(!estado.ativos)bloqueios.delete(n);});}
}

export async function reduzirFoto(arquivo) {
  if (!['image/jpeg', 'image/png'].includes(arquivo.type) || arquivo.size > 32 * 1024 * 1024) {
    throw new Error('Escolha uma foto JPEG ou PNG de até 32 MB. Para HEIC, exporte uma cópia em JPEG.');
  }
  let imagem;
  try {
    imagem = await createImageBitmap(arquivo);
    const escala = Math.min(1, 2048 / Math.max(imagem.width, imagem.height));
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(imagem.width * escala));
    canvas.height = Math.max(1, Math.round(imagem.height * escala));
    canvas.getContext('2d').drawImage(imagem, 0, 0, canvas.width, canvas.height);
    const foto = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', .85));
    if (!foto || foto.size > 3 * 1024 * 1024) throw new Error();
    return foto;
  } catch {
    throw new Error('Não foi possível preparar a foto. Tente outra imagem JPEG ou PNG.');
  } finally { imagem?.close(); }
}

export function rascunho(acao, valor) {
  return new Promise((resolve, reject) => {
    const abrir = indexedDB.open('citizentech-rascunho', 1);
    abrir.onupgradeneeded = () => abrir.result.createObjectStore('dados');
    abrir.onerror = () => reject(new Error('O navegador não permitiu salvar o rascunho neste aparelho.'));
    abrir.onsuccess = () => {
      const db = abrir.result, tx = db.transaction('dados', acao === 'get' ? 'readonly' : 'readwrite');
      const store = tx.objectStore('dados');
      const req = acao === 'put' ? store.put(valor, 'pedido') : store.get('pedido');
      let resultado;
      req.onsuccess = () => {
        resultado = req.result;
        if (acao === 'delete' || acao === 'atualizar') {
          resultado = acao === 'delete' && valor === undefined || mesmoRascunho(req.result, acao === 'delete' ? valor : valor.id);
          if(resultado) {
            if(acao === 'delete') store.delete('pedido'); else store.put(valor, 'pedido');
          }
        }
      };
      tx.oncomplete = () => {db.close(); resolve(resultado);};
      tx.onerror = tx.onabort = () => {db.close(); reject(new Error('Não foi possível acessar o rascunho. Confira o armazenamento do navegador.'));};
    };
  });
}
