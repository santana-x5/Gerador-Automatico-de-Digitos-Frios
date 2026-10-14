import re
from datetime import date

import pytest

from documentos import digito_verificador
from pessoas import (
    CAMPOS_OPCIONAIS,
    NOMES_FEMININOS,
    NOMES_MASCULINOS,
    SOBRENOMES,
    _sem_acentos,
    calcular_idade,
    gerar_data_nascimento,
    gerar_email,
    gerar_id,
    gerar_nome,
    gerar_pessoa,
)

PESOS_CPF_1 = list(range(10, 1, -1))
PESOS_CPF_2 = list(range(11, 1, -1))
REGEX_CPF = r"\d{3}\.\d{3}\.\d{3}-\d{2}"
REGEX_EMAIL = r"[a-z0-9]+@example\.com"


# ---------- verificadores usados nos testes ----------

def cpf_ok(texto):
    """CPF com máscara, dígitos corretos e não todos iguais."""
    if not re.fullmatch(REGEX_CPF, texto):
        return False
    digitos = [int(c) for c in texto if c.isdigit()]
    if len(set(digitos)) == 1:
        return False
    dv1 = digito_verificador(digitos[:9], PESOS_CPF_1)
    dv2 = digito_verificador(digitos[:10], PESOS_CPF_2)
    return digitos[9:] == [dv1, dv2]


def data_ok(texto):
    try:
        date.fromisoformat(texto)
    except ValueError:
        return False
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto))


def email_ok(texto):
    return bool(re.fullmatch(REGEX_EMAIL, texto))


def idade_da_pessoa(p):
    return calcular_idade(date.fromisoformat(p["data_nascimento"]))


# ---------- gerar_nome ----------

def test_gerar_nome():
    for _ in range(1000):
        partes = gerar_nome().split()
        assert len(partes) == 3
        assert partes[0] in NOMES_MASCULINOS + NOMES_FEMININOS
        assert partes[1] in SOBRENOMES and partes[2] in SOBRENOMES
        assert partes[1] != partes[2]


# ---------- datas de nascimento ----------

def test_gerar_data_nascimento_faixas():
    for _ in range(5000):
        assert 18 <= calcular_idade(gerar_data_nascimento("adulto")) <= 80
        assert 0 <= calcular_idade(gerar_data_nascimento("menor")) <= 17


def test_calcular_idade_limites():
    assert calcular_idade(date(2008, 10, 13), date(2026, 10, 13)) == 18
    assert calcular_idade(date(2008, 10, 14), date(2026, 10, 13)) == 17


def test_data_29_de_fevereiro():
    hoje = date(2028, 2, 29)
    for _ in range(3000):
        assert calcular_idade(gerar_data_nascimento("adulto", hoje), hoje) >= 18
        assert calcular_idade(gerar_data_nascimento("menor", hoje), hoje) <= 17


def test_data_cenario_invalido():
    with pytest.raises(ValueError):
        gerar_data_nascimento("idoso")


# ---------- e-mail ----------

def test_gerar_email_valido():
    for _ in range(1000):
        assert email_ok(gerar_email(True))


def test_gerar_email_invalido():
    for _ in range(1000):
        e = gerar_email(False)
        assert not email_ok(e)
        # tem que ser um dos 3 defeitos: sem @, sem domínio ou com espaço
        assert ("@" not in e) or e.endswith("@") or (" " in e)


def test_gerar_email_derivado_do_nome():
    e = gerar_email(True, "Letícia Araújo Nunes")
    assert e.startswith("leticianunes")
    assert email_ok(e)


# ---------- id ----------

def test_gerar_id():
    assert gerar_id(1) == "teste-0001"
    assert gerar_id(42) == "teste-0042"
    assert gerar_id(9999) == "teste-9999"
    assert gerar_id(10000) == "teste-10000"
    ids = [gerar_id(i) for i in range(1, 1001)]
    assert len(set(ids)) == 1000


def test_gerar_id_invalido():
    with pytest.raises(ValueError):
        gerar_id(0)


# ---------- gerar_pessoa: cenário completo ----------

def test_pessoa_completa():
    for i in range(1, 1001):
        p = gerar_pessoa(i)
        assert list(p) == ["id", "ambiente", "nome", "cpf", "data_nascimento", "email"]
        assert p["id"] == gerar_id(i)
        assert p["ambiente"] == "teste"
        assert len(p["nome"].split()) == 3
        assert cpf_ok(p["cpf"])
        assert data_ok(p["data_nascimento"])
        assert email_ok(p["email"])
        assert idade_da_pessoa(p) >= 18
        primeiro, *_, ultimo = _sem_acentos(p["nome"]).lower().split()
        assert p["email"].startswith(primeiro + ultimo)


def test_pessoa_menor():
    for _ in range(1000):
        assert idade_da_pessoa(gerar_pessoa(1, "completo", "menor")) < 18


# ---------- gerar_pessoa: campos ausentes ----------

def test_ausentes_vazio():
    for i in range(1, 1001):
        p = gerar_pessoa(i, "ausentes")
        assert p["id"] == gerar_id(i) and p["ambiente"] == "teste"
        assert len(p) == 6
        assert 1 <= sum(p[c] == "" for c in CAMPOS_OPCIONAIS) <= 3


def test_ausentes_nulo():
    for i in range(1, 1001):
        p = gerar_pessoa(i, "ausentes", modo_ausente="nulo")
        assert p["id"] == gerar_id(i) and p["ambiente"] == "teste"
        assert len(p) == 6
        assert 1 <= sum(p[c] is None for c in CAMPOS_OPCIONAIS) <= 3


def test_ausentes_omitido():
    for i in range(1, 1001):
        p = gerar_pessoa(i, "ausentes", modo_ausente="omitido")
        assert p["id"] == gerar_id(i) and p["ambiente"] == "teste"
        assert 3 <= len(p) <= 5
        assert 1 <= sum(c not in p for c in CAMPOS_OPCIONAIS) <= 3


# ---------- gerar_pessoa: formatos inválidos ----------

def test_invalidos():
    for i in range(1, 1001):
        p = gerar_pessoa(i, "invalidos")
        assert p["id"] == gerar_id(i) and p["ambiente"] == "teste"
        assert len(p) == 6
        assert len(p["nome"].split()) == 3  # nome nunca é estragado
        invalidos = [
            not cpf_ok(p["cpf"]),
            not data_ok(p["data_nascimento"]),
            not email_ok(p["email"]),
        ]
        assert 1 <= sum(invalidos) <= 3


# ---------- erros de uso ----------

def test_cenario_invalido():
    with pytest.raises(ValueError):
        gerar_pessoa(1, "xyz")


def test_modo_ausente_invalido():
    with pytest.raises(ValueError):
        gerar_pessoa(1, "ausentes", modo_ausente="sumido")