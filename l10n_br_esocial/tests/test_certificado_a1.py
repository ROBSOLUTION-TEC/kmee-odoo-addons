# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Certificado A1 da empresa no lote eSocial (Odoo 20).

No Odoo 20 o certificado é um ``certificate.certificate`` (módulo
``certificate`` do core, estendido pelo ``l10n_br_fiscal_certificate``) e o
binário ``content`` é um ``BinaryValue``: o lote precisa entregar à esociallib
os bytes crus do PFX e a senha. A transmissão é sempre simulada (mock): nada
é enviado ao ambiente do governo.
"""

import base64
import unittest
from unittest import mock

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools import BinaryBytes


@tagged("post_install", "-at_install")
class TestCertificadoA1(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if "certificate_id" not in cls.env["res.company"]._fields:
            raise unittest.SkipTest("l10n_br_fiscal_certificate não instalado")
        from erpbrasil.assinatura import misc

        cls.senha = "123456"
        cls.pfx_b64 = misc.create_fake_certificate_file(
            valid=True,
            passwd=cls.senha,
            issuer="EMISSOR TESTE",
            country="BR",
            subject="EMPRESA ESOCIAL TESTE",
        )
        cls.company = cls.env.company
        cls.certificate = cls.env["certificate.certificate"].create(
            {
                "scope": "l10n_br",
                "pkcs12_password": cls.senha,
                # Odoo 20: Binary fields take a BinaryValue (raw bytes)
                "content": BinaryBytes(base64.b64decode(cls.pfx_b64)),
                "company_id": cls.company.id,
            }
        )
        cls.lote = cls.env["l10n_br.esocial.lote"].create(
            {"company_id": cls.company.id}
        )

    def test_sem_certificado_erro_amigavel(self):
        self.company.certificate_id = False
        with self.assertRaises((UserError, Exception)):
            self.lote._get_certificate()

    def test_certificado_retorna_pfx_bruto_e_senha(self):
        self.company.certificate_id = self.certificate
        pfx_data, senha = self.lote._get_certificate()
        self.assertIsInstance(pfx_data, bytes)
        self.assertEqual(pfx_data, base64.b64decode(self.pfx_b64))
        self.assertEqual(senha, self.senha)

    def test_transmissao_simulada_usa_certificado(self):
        """action_transmitir assina e envia com o PFX da empresa (mock)."""
        self.company.certificate_id = self.certificate
        evento = self.env["l10n_br.esocial.evento"].create(
            {
                "tipo": "S-1000",
                "operacao": "I",
                "state": "validated",
                "xml_envio": "<eSocial><evtInfoEmpregador/></eSocial>",
                "company_id": self.company.id,
            }
        )
        evento.lote_id = self.lote.id
        modulo = "odoo.addons.l10n_br_esocial.models.esocial_lote"
        with mock.patch(
            f"{modulo}.assinar", side_effect=lambda xml, pfx, senha: xml
        ) as assinar, mock.patch(
            f"{modulo}.enviar_lote", return_value="PROT-SIMULADO"
        ) as enviar:
            self.lote.action_transmitir()
        pfx_esperado = base64.b64decode(self.pfx_b64)
        self.assertEqual(assinar.call_args.args[1], pfx_esperado)
        self.assertEqual(assinar.call_args.args[2], self.senha)
        self.assertEqual(enviar.call_args.args[1], pfx_esperado)
        self.assertEqual(self.lote.protocolo, "PROT-SIMULADO")
        self.assertEqual(self.lote.state, "sent")
        self.assertEqual(evento.state, "sent")
