'use strict';
importScripts('/ouviai/audio_bundle.js');
let modelo;
self.onmessage = async ({data}) => {
  try {
    if (data.tipo === 'iniciar') {
      const arquivos = await Audio.FilesetResolver.forAudioTasks('/ouviai/wasm');
      modelo = await Audio.AudioClassifier.createFromOptions(arquivos, {
        baseOptions: {modelAssetPath:'/ouviai/yamnet.tflite'}, maxResults:-1,
      });
      self.postMessage({tipo:'pronto'});
    } else if (data.tipo === 'audio') {
      const resultados = modelo.classify(data.amostras, data.frequencia);
      self.postMessage({tipo:'resultado', janelas:resultados.map(r=>r.classifications[0]?.categories || [])});
    }
  } catch {
    self.postMessage({tipo:'erro', mensagem:'Não foi possível executar o modelo de áudio. Pare e tente novamente com conexão disponível.'});
  }
};
