export function pontoValido(caso) {
  const g=caso?.localizacao;
  return Boolean(g?.confirmado && Number.isFinite(g.latitude) && Number.isFinite(g.longitude) && Math.abs(g.latitude)<=90 && Math.abs(g.longitude)<=180);
}
export function proximos(caso, casos, raio=100) {
  if(!pontoValido(caso))return [];
  const rad=n=>n*Math.PI/180, a=caso.localizacao;
  return casos.filter(c=>c.id!==caso.id && pontoValido(c)).map(c=>{
    const b=c.localizacao;
    const h=Math.sin(rad(b.latitude-a.latitude)/2)**2+Math.cos(rad(a.latitude))*Math.cos(rad(b.latitude))*Math.sin(rad(b.longitude-a.longitude)/2)**2;
    return {caso:c,metros:6371000*2*Math.asin(Math.sqrt(Math.min(1,h)))};
  }).filter(c=>c.metros<=raio).sort((a,b)=>a.metros-b.metros);
}
export function fase(caso) {return caso.frontend?'confirmado':caso.revisao?'revisado':'pendente';}
export function filtrarCasos(casos, termo='', filtro='todos') {
  const normalizar=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const busca=normalizar(termo.trim());
  return casos.filter(c=>(filtro==='todos'||fase(c)===filtro) && normalizar([c.id,c.descricao,c.bairro,c.local].join(' ')).includes(busca));
}

export function criarMapa(id, statusId, aoEscolher) {
  const container=document.getElementById(id), status=document.getElementById(statusId), L=globalThis.L;
  if(!L) {status.textContent='Mapa indisponível. Use os campos de localização ou a lista de pedidos.';return null;}
  const mapa=L.map(container,{scrollWheelZoom:false,minZoom:3,maxZoom:19}).setView([-23.5443,-46.6432],16);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
    maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a>',
    referrerPolicy:'strict-origin-when-cross-origin',updateWhenIdle:true,keepBuffer:0
  }).on('tileerror',()=>{status.textContent='O mapa base não carregou. Você pode usar as coordenadas ou abrir um registro pela lista.';})
    .on('tileload',()=>{status.textContent=aoEscolher?'Toque no mapa para marcar o problema. Depois confira e confirme o ponto.':'Selecione um ponto ou abra um pedido pela lista.';}).addTo(mapa);
  const camada=L.layerGroup().addTo(mapa);
  let ponto;
  function marcador(latlon,classe,titulo,arrastavel=false) {
    return L.marker(latlon,{icon:L.divIcon({className:'map-pin '+classe,html:'<span aria-hidden="true"></span>',iconSize:[36,44],iconAnchor:[18,42]}),title:titulo,alt:titulo,keyboard:true,draggable:arrastavel,autoPan:arrastavel});
  }
  if(aoEscolher)mapa.on('click',e=>aoEscolher(e.latlng.lat,e.latlng.lng));
  return {
    resize(){requestAnimationFrame(()=>mapa.invalidateSize({pan:true,animate:false}));},
    ponto(g,centrar=true) {
      if(ponto){ponto.remove();ponto=null;}
      if(!g)return;
      ponto=marcador([g.latitude,g.longitude],'escolhido','Local do problema. Arraste para ajustar.',Boolean(aoEscolher)).addTo(mapa);
      if(aoEscolher)ponto.on('dragend',()=>{const g=ponto.getLatLng();aoEscolher(g.lat,g.lng);});
      if(centrar)mapa.setView([g.latitude,g.longitude],17);
    },
    casos(casos,selecionado,abrir) {
      camada.clearLayers();
      casos.filter(pontoValido).forEach(c=>marcador([c.localizacao.latitude,c.localizacao.longitude],fase(c)+(c.id===selecionado?' selected':''),c.descricao)
        .on('click',()=>abrir(c.id)).addTo(camada));
    },
    enquadrar(casos) {
      const pontos=casos.filter(pontoValido).map(c=>[c.localizacao.latitude,c.localizacao.longitude]);
      if(pontos.length)mapa.fitBounds(pontos,{padding:[45,45],maxZoom:17});
    },
    focar(caso) {if(pontoValido(caso))mapa.setView([caso.localizacao.latitude,caso.localizacao.longitude],17);}
  };
}
