import hashlib
import io
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError


def normalizar(conteudo: bytes) -> Image.Image:
    if not conteudo or len(conteudo) > 8 * 1024 * 1024:
        raise ValueError('Envie uma imagem JPEG ou PNG de até 8 MB.')
    try:
        with Image.open(io.BytesIO(conteudo)) as imagem:
            if imagem.format not in {'JPEG', 'PNG'} or imagem.width * imagem.height > 4096 * 4096:
                raise ValueError('Use JPEG ou PNG de até 16,8 megapixels.')
            limpa = ImageOps.exif_transpose(imagem).convert('RGB')
            limpa.info.clear()
            return limpa
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as erro:
        raise ValueError('A imagem está ilegível ou excede o limite de tamanho.') from erro


def guardar(conteudo: bytes, pasta: Path) -> dict:
    imagem = normalizar(conteudo)
    imagem.thumbnail((2048, 2048))
    saida = io.BytesIO()
    imagem.save(saida, format='JPEG', quality=85)
    foto = saida.getvalue()
    sha = hashlib.sha256(foto).hexdigest()
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / (sha + '.jpg')
    temporario = pasta / (str(uuid4()) + '.tmp')
    try:
        temporario.write_bytes(foto)
        temporario.replace(destino)
    except OSError as erro:
        raise RuntimeError('Não foi possível guardar a foto. O pedido não foi registrado; tente novamente.') from erro
    finally:
        temporario.unlink(missing_ok=True)
    return {'sha256': sha, 'tipo': 'image/jpeg', 'bytes': len(foto),
            'largura': imagem.width, 'altura': imagem.height}
