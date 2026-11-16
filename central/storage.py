import hashlib
import re
from urllib.parse import urlsplit

import httpx

from .imagens import preparar_foto


class StorageFotos:
    def __init__(self, url: str, chave: str):
        destino = urlsplit(url)
        if (destino.scheme != 'https' or not destino.hostname
                or not re.fullmatch(r'[a-z0-9-]+\.supabase\.co', destino.hostname)
                or destino.username or destino.password or destino.port
                or destino.path not in {'', '/'} or destino.query or destino.fragment):
            raise ValueError('Configure a URL HTTPS do projeto Supabase.')
        if not chave.startswith('sb_secret_') or len(chave) < 24:
            raise ValueError('Configure a chave secreta de servidor do Supabase.')
        self.base = url.rstrip('/') + '/storage/v1/object/zelabairro-fotos/'
        self.headers = {'apikey': chave}

    def guardar(self, conteudo: bytes) -> dict:
        foto, metadados = preparar_foto(conteudo)
        sha = metadados['sha256']
        try:
            resposta = httpx.request('POST', self.base + sha + '.jpg', content=foto,
                                     headers={**self.headers, 'Content-Type': 'image/jpeg', 'x-upsert': 'false'},
                                     timeout=30, follow_redirects=False)
            if resposta.is_success:
                return metadados
            duplicado = (resposta.status_code in {400, 409}
                         and resposta.json().get('error') == 'Duplicate')
            if duplicado and self.ler(sha) == foto:
                return metadados
        except (httpx.HTTPError, ValueError, TypeError, AttributeError):
            pass
        raise RuntimeError('Não foi possível guardar a foto. O pedido não foi registrado; tente novamente.')

    def ler(self, sha: str) -> bytes:
        if not re.fullmatch(r'[a-f0-9]{64}', sha):
            raise ValueError('Identificador de foto inválido.')
        try:
            resposta = httpx.request('GET', self.base + sha + '.jpg', headers=self.headers,
                                     timeout=30, follow_redirects=False)
            if (resposta.is_success and len(resposta.content) <= 8 * 1024 * 1024
                    and hashlib.sha256(resposta.content).hexdigest() == sha):
                return resposta.content
        except httpx.HTTPError:
            pass
        raise RuntimeError('Não foi possível recuperar a foto íntegra do armazenamento. Tente novamente.')
