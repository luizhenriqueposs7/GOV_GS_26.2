import base64
import hashlib
import hmac
import json
import unittest

from central import relato_foto


class OcorrenciaTest(unittest.TestCase):
    def test_buraco_vira_pedido_sem_inventar_medida_ou_causa(self):
        texto = relato_foto.redigir('buraco', 'Abertura no asfalto com bordas irregulares e material solto.')
        self.assertIn('Solicito vistoria', texto)
        self.assertIn('quedas', texto)
        self.assertIn('sinalização', texto)
        self.assertIn('não aferidas', texto)
        self.assertNotRegex(texto, r'\d|solapamento|profundo|urgente')
        self.assertLessEqual(len(relato_foto.redigir('buraco', 'x' * 1000)), 1500)

    def test_previa_antiga_continua_valida_sem_adicionar_campos_a_assinatura(self):
        origem = dict(status='identificado', descricao='Fissura na superfície.', tipo='fissura',
                      limites='Não permite medir profundidade.', modelo='qwen/qwen3.8-27b',
                      gerado_em='2026-11-15T12:00:00+00:00', foto_sha256='a' * 64)
        payload = base64.urlsafe_b64encode(json.dumps(origem).encode()).decode()
        token = payload + '.' + hmac.new(b'chave', ('relato-foto-v1:' + payload).encode(), hashlib.sha256).hexdigest()
        self.assertEqual(relato_foto.validar(token, {'sha256': 'a' * 64}, 'chave'), origem)
