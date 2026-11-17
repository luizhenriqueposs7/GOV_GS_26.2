'use strict';
class CapturaOuviAi extends AudioWorkletProcessor {
  constructor() {
    super();
    this.janela = new Float32Array(Math.round(sampleRate * 2));
    this.posicao = 0;
  }
  process(entradas) {
    const dados = entradas[0]?.[0];
    if (!dados) return true;
    for (let i=0; i<dados.length; i++) {
      this.janela[this.posicao++] = dados[i];
      if (this.posicao === this.janela.length) {
        const copia = this.janela.slice();
        this.port.postMessage(copia, [copia.buffer]);
        this.posicao = this.janela.length / 2;
        this.janela.copyWithin(0, this.posicao);
      }
    }
    return true;
  }
}
registerProcessor('captura-ouviai', CapturaOuviAi);
