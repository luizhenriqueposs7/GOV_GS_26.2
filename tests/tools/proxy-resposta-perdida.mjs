// Sonda local: descarta apenas a primeira resposta de cadastro já concluído.
import http from 'node:http';
import {writeFileSync} from 'node:fs';
let descartar = true;
http.createServer((req,res)=>{
  const upstream=http.request({hostname:'127.0.0.1',port:8841,path:req.url,method:req.method,headers:{...req.headers,host:'127.0.0.1:8841'}}, resposta=>{
    if(descartar && req.method==='POST' && req.url==='/api/atendimentos/com-anexo' && resposta.statusCode===201) {
      descartar=false;
      const partes=[];
      resposta.on('data',c=>partes.push(c));
      resposta.on('end',()=>{
        const caso=JSON.parse(Buffer.concat(partes).toString());
        writeFileSync('data/runtime/resposta-perdida.json',JSON.stringify({atendimento_id:caso.id,descartada:true}));
        res.destroy();
      });
    } else {res.writeHead(resposta.statusCode,resposta.headers);resposta.pipe(res);}
  });
  upstream.on('error',()=>{res.writeHead(503,{'Content-Type':'application/json'});res.end(JSON.stringify({erro:'Prévia local indisponível.'}));});
  req.pipe(upstream);
}).listen(8842,'127.0.0.1');
