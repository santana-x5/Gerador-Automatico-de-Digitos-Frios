"""Geração de lotes de registros fictícios e exportação (JSON/CSV)."""

import random

from documentos import (
    estragar_documento,
    formatar_cnpj,
    formatar_cpf,
    gerar_cnpj,
    gerar_cnpj_alfanumerico,
    gerar_cpf,
)
from pessoas import gerar_pessoa

QUANTIDADE_MIN = 1
QUANTIDADE_MAX = 100
MODOS = ("pessoas", "documentos")
TIPOS_DOC = ("cpf", "cnpj", "cnpj_alfanumerico")
MARCA = "TESTE"

# tipo -> (função que gera sem máscara, função que aplica a máscara)
_DOCUMENTOS = {
    "cpf": (gerar_cpf, formatar_cpf),
    "cnpj": (gerar_cnpj, formatar_cnpj),
    "cnpj_alfanumerico": (gerar_cnpj_alfanumerico, formatar_cnpj),
}


def _documento_valido(tipo_doc):
    gerar, formatar = _DOCUMENTOS[tipo_doc]
    return formatar(gerar())


def _documento_invalido(tipo_doc):
    """Dígito verificador errado (mantendo a máscara) ou formato quebrado."""
    formatar = _DOCUMENTOS[tipo_doc][1]
    if random.random() < 0.5:
        return formatar(estragar_documento(tipo_doc, "dv"))
    return estragar_documento(tipo_doc, "formato")


def _adicionar_documento(pessoa, cenario, tipo_doc, modo_ausente):
    """Acrescenta 'documento' e 'marca' ao registro, respeitando o cenário."""
    if cenario == "invalidos":
        pessoa["documento"] = _documento_invalido(tipo_doc)
    elif cenario == "ausentes" and random.random() < 0.5:
        if modo_ausente == "vazio":
            pessoa["documento"] = ""
        elif modo_ausente == "nulo":
            pessoa["documento"] = None
        # "omitido": a chave simplesmente não entra no registro
    else:
        pessoa["documento"] = _documento_valido(tipo_doc)
    pessoa["marca"] = MARCA


def gerar_lote(quantidade, cenario="completo", modo="pessoas", tipo_doc="cpf",
               faixa="adulto", modo_ausente="vazio"):
    """Gera um lote de registros fictícios (lista de dicionários).

    quantidade: inteiro de 1 a 100.
    cenario: "completo" | "ausentes" | "invalidos" (validado em gerar_pessoa).
    modo: "pessoas" (só os dados da pessoa) |
          "documentos" (pessoa + campo 'documento' + marca 'TESTE').
    tipo_doc: "cpf" | "cnpj" | "cnpj_alfanumerico" (usado no modo "documentos").
    faixa e modo_ausente: repassados para gerar_pessoa.
    Os IDs são sequenciais dentro do lote: teste-0001, teste-0002...
    """
    if (isinstance(quantidade, bool) or not isinstance(quantidade, int)
            or not QUANTIDADE_MIN <= quantidade <= QUANTIDADE_MAX):
        raise ValueError(
            f"quantidade deve ser um inteiro de {QUANTIDADE_MIN} a {QUANTIDADE_MAX}"
        )
    if modo not in MODOS:
        raise ValueError(f"modo inválido: {modo}")
    if tipo_doc not in TIPOS_DOC:
        raise ValueError(f"tipo_doc inválido: {tipo_doc}")

    lote = [
        gerar_pessoa(i, cenario, faixa, modo_ausente)
        for i in range(1, quantidade + 1)
    ]
    if modo == "documentos":
        for pessoa in lote:
            _adicionar_documento(pessoa, cenario, tipo_doc, modo_ausente)
    return lote