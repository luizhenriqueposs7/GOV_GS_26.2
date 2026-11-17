async page => {
  if(new URL(page.url()).hostname!=='127.0.0.1')throw new Error('Execute somente na origem local de QA.');
  return await page.evaluate(async()=>{
    const {rascunho}=await import('/web/mobile.mjs');
    const conferir=(condicao,mensagem)=>{if(!condicao)throw new Error(mensagem);};
    const original=await rascunho('get');
    const foto=new Blob(['foto de teste: bytes preservados'],{type:'image/jpeg'});
    try {
      await rascunho('put',{id:'qa-foto',foto,campos:{descricao:'Rascunho de teste'},envioId:'mesma-tentativa'});
      const armazenado=await new Promise((resolve,reject)=>{
        const abrir=indexedDB.open('citizentech-rascunho',1);
        abrir.onerror=()=>reject(abrir.error);
        abrir.onsuccess=()=>{const db=abrir.result,tx=db.transaction('dados'),req=tx.objectStore('dados').get('pedido');
          tx.oncomplete=()=>{db.close();resolve(req.result);};tx.onabort=()=>{db.close();reject(tx.error);};};
      });
      conferir(armazenado.foto.dados instanceof ArrayBuffer,'Foto deve ser armazenada como bytes portáveis.');
      const salvo=await rascunho('get');
      conferir(salvo.foto instanceof Blob&&salvo.foto.type===foto.type&&await salvo.foto.text()===await foto.text(),'Foto recuperada deve preservar tipo e bytes.');
      conferir(salvo.envioId==='mesma-tentativa','Tentativa de envio deve ser preservada.');
      conferir(await rascunho('atualizar',{id:'outra-aba',foto})===false,'Outra aba não pode sobrescrever o rascunho.');
      conferir(await rascunho('delete','outra-aba')===false,'Outro envio não pode apagar o rascunho.');
      conferir(await rascunho('atualizar',{...salvo,campos:{descricao:'Atualizado conscientemente'}})===true,'O mesmo rascunho deve ser atualizável.');
      conferir((await rascunho('get')).campos.descricao==='Atualizado conscientemente','Atualização não persistiu.');
      conferir(await rascunho('delete','qa-foto')===true&&await rascunho('get')===undefined,'Exclusão não foi concluída.');
      await rascunho('put',{id:'qa-legado',campos:{descricao:'Sem foto'}});
      conferir((await rascunho('get')).campos.descricao==='Sem foto','Rascunho sem foto deve continuar compatível.');
      return {foto_bytes_e_tipo:true,envio_preservado:true,protecao_entre_abas:true,atualizacao:true,exclusao:true,sem_foto:true};
    } finally {if(original)await rascunho('put',original);else await rascunho('delete');}
  });
}
