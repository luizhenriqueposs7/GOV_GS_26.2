export function criarEscuta(aoResultado, aoEstado) {
  let atual = null;
  function parar(mensagem='Microfone desligado.') {
    const sessao = atual; atual = null;
    if (sessao) {
      clearTimeout(sessao.prazo);
      clearTimeout(sessao.inferencia);
      sessao.cancelar?.(new Error('Escuta encerrada.'));
      sessao.worker?.terminate();
      sessao.fluxo?.getTracks().forEach(t=>t.stop());
      if (sessao.captura) {sessao.captura.port.onmessage=null; sessao.captura.disconnect();}
      sessao.origem?.disconnect(); sessao.silencio?.disconnect();
      sessao.contexto?.close().catch(()=>{});
    }
    aoEstado(false,mensagem);
  }
  async function iniciar() {
    if (atual) return;
    if (!globalThis.isSecureContext || !navigator.mediaDevices?.getUserMedia || !globalThis.AudioContext || !globalThis.AudioWorkletNode) {
      aoEstado(false,'Use o endereço HTTPS em um navegador atualizado para ativar o microfone.'); return;
    }
    const sessao = {}; atual = sessao;
    aoEstado(true,'Autorize o microfone. O modelo será carregado neste aparelho.');
    try {
      sessao.contexto = new AudioContext();
      await sessao.contexto.resume();
      if (atual !== sessao) return;
      const fluxo = await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:false,noiseSuppression:false,autoGainControl:false}});
      if (atual !== sessao) {fluxo.getTracks().forEach(t=>t.stop()); return;}
      sessao.fluxo = fluxo;
      fluxo.getAudioTracks().forEach(t=>t.addEventListener('ended',()=>{if(atual===sessao)parar('O microfone foi desconectado. Ative novamente para continuar.');}));
      aoEstado(true,'Carregando o modelo de áudio. Na primeira vez, o download pode levar alguns instantes.');
      sessao.worker = new Worker('/web/ouviai-worker.js');
      sessao.worker.onerror = ()=>{if(atual===sessao)parar('Falha ao carregar o modelo. Confira a conexão e tente novamente.');};
      await new Promise((resolve,reject)=>{
        sessao.cancelar=reject;
        sessao.prazo=setTimeout(()=>reject(new Error('O modelo demorou para carregar. Confira a conexão e tente novamente.')),90000);
        sessao.worker.onmessage=({data})=>{
          if (data.tipo==='pronto') {clearTimeout(sessao.prazo);resolve();}
          if (data.tipo==='erro') reject(new Error(data.mensagem));
        };
        sessao.worker.postMessage({tipo:'iniciar'});
      });
      sessao.cancelar=null;
      if (atual !== sessao) return;
      await sessao.contexto.audioWorklet.addModule('/web/ouviai-captura.js');
      if (atual !== sessao) return;
      sessao.origem = sessao.contexto.createMediaStreamSource(fluxo);
      sessao.captura = new AudioWorkletNode(sessao.contexto,'captura-ouviai');
      sessao.captura.onprocessorerror=()=>{if(atual===sessao)parar('A captura do áudio falhou. Ative novamente para continuar.');};
      sessao.silencio = sessao.contexto.createGain(); sessao.silencio.gain.value = 0;
      sessao.worker.onmessage=({data})=>{
        if (atual !== sessao) return;
        clearTimeout(sessao.inferencia);
        sessao.ocupado=false;
        if (data.tipo==='erro') parar(data.mensagem);
        else if (data.tipo==='resultado') for (const categorias of data.janelas) aoResultado(categorias);
      };
      sessao.captura.port.onmessage=({data})=>{
        if (atual !== sessao || sessao.ocupado) return;
        sessao.ocupado=true;
        sessao.inferencia=setTimeout(()=>{if(atual===sessao)parar('O processamento do áudio parou de responder. Ative novamente para continuar.');},15000);
        sessao.worker.postMessage({tipo:'audio',amostras:data,frequencia:sessao.contexto.sampleRate},[data.buffer]);
      };
      sessao.origem.connect(sessao.captura).connect(sessao.silencio).connect(sessao.contexto.destination);
      sessao.contexto.onstatechange=()=>{if(atual===sessao && ['suspended','interrupted'].includes(sessao.contexto.state))parar('O aparelho interrompeu o áudio. Ative novamente para continuar.');};
      aoEstado(true,'Escutando neste aparelho. Faça uma batida na porta ou toque uma campainha; aguarde alguns segundos.');
    } catch (erro) {
      if (atual !== sessao) return;
      parar(erro.name==='NotAllowedError' ? 'Microfone não autorizado. Permita o acesso nas opções do navegador e tente novamente.'
        : erro.name==='NotFoundError' ? 'Não encontramos um microfone neste aparelho.' : (erro.message || 'Não foi possível ativar o áudio.'));
    }
  }
  return {iniciar,parar};
}
