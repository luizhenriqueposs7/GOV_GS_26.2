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
  return Object.fromEntries(['descricao', 'bairro', 'local', 'contexto', 'latitude', 'longitude']
    .map(k => [k, String(dados[k] || '')]));
}

export function criarRascunho(campos, estado) {
  const {foto, origemGeo, precisaoGeo, envioId, assinatura, rascunhoId} = estado;
  return {id:rascunhoId, campos:dadosRascunho(campos), foto, origemGeo, precisaoGeo,
    envioId, assinatura, salvoEm:new Date().toISOString()};
}

export function mesmoRascunho(salvo, id) {return Boolean(id && salvo?.id === id);}

export async function bloquearDurante(controles, acao) {
  const anteriores = controles.map(n=>[n,n.disabled]);
  anteriores.forEach(([n])=>n.disabled=true);
  try {return await acao();} finally {anteriores.forEach(([n,antes])=>n.disabled=antes);}
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
    if (!foto || foto.size > 8 * 1024 * 1024) throw new Error();
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
