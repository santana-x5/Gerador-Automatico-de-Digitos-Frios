from documentos import (
    PESOS_CNPJ_1,
    PESOS_CNPJ_2,
    digito_verificador,
    estragar_documento,
    formatar_cnpj,
    formatar_cpf,
    gerar_cnpj,
    gerar_cnpj_alfanumerico,
    gerar_cpf,
    valor_do_caractere,
)

PESOS_CPF_1 = list(range(10, 1, -1))
PESOS_CPF_2 = list(range(11, 1, -1))


def valores(texto):
    return [valor_do_caractere(c) for c in texto]


def soma(vals, pesos):
    return sum(v * p for v, p in zip(vals, pesos))


# ---------- valor_do_caractere ----------

def test_valor_do_caractere():
    assert valor_do_caractere("0") == 0
    assert valor_do_caractere("9") == 9
    assert valor_do_caractere("A") == 17
    assert valor_do_caractere("Z") == 42


# ---------- Caso 1: CPF, base 123456789 -> 12345678909 ----------

def test_cpf_caso_base_123456789():
    base = valores("123456789")
    assert soma(base, PESOS_CPF_1) == 210
    dv1 = digito_verificador(base, PESOS_CPF_1)
    assert dv1 == 0

    assert soma(base + [dv1], PESOS_CPF_2) == 255
    dv2 = digito_verificador(base + [dv1], PESOS_CPF_2)
    assert dv2 == 9


# ---------- Caso 2: CNPJ, base 123456780001 -> 12345678000195 ----------

def test_cnpj_caso_base_123456780001():
    base = valores("123456780001")
    assert soma(base, PESOS_CNPJ_1) == 222
    dv1 = digito_verificador(base, PESOS_CNPJ_1)
    assert dv1 == 9

    assert soma(base + [dv1], PESOS_CNPJ_2) == 237
    dv2 = digito_verificador(base + [dv1], PESOS_CNPJ_2)
    assert dv2 == 5


# ---------- Caso 3: CNPJ alfanumérico, base 12ABC34501DE -> 12ABC34501DE35 ----------

def test_cnpj_alfanumerico_caso_base_12ABC34501DE():
    base = valores("12ABC34501DE")
    assert soma(base, PESOS_CNPJ_1) == 459
    dv1 = digito_verificador(base, PESOS_CNPJ_1)
    assert dv1 == 3

    assert soma(base + [dv1], PESOS_CNPJ_2) == 424
    dv2 = digito_verificador(base + [dv1], PESOS_CNPJ_2)
    assert dv2 == 5


# ---------- digito_verificador: resto 0 ou 1 vira 0 ----------

def test_digito_verificador_resto_0_ou_1():
    assert digito_verificador([1], [11]) == 0  # soma 11, resto 0
    assert digito_verificador([1], [1]) == 0   # soma 1, resto 1
    assert digito_verificador([2], [1]) == 9   # soma 2, resto 2 -> 11 - 2


# ---------- formatação ----------

def test_formatar():
    assert formatar_cpf("12345678909") == "123.456.789-09"
    assert formatar_cnpj("12345678000195") == "12.345.678/0001-95"
    assert formatar_cnpj("12ABC34501DE35") == "12.ABC.345/01DE-35"


# ---------- geradores ----------

def test_gerar_cpf_valido():
    for _ in range(1000):
        c = gerar_cpf()
        assert len(c) == 11 and c.isdigit()
        assert len(set(c)) > 1  # item 7: nada de dígitos todos iguais
        d1 = digito_verificador(valores(c[:9]), PESOS_CPF_1)
        d2 = digito_verificador(valores(c[:10]), PESOS_CPF_2)
        assert c[9:] == f"{d1}{d2}"


def test_gerar_cnpj_valido():
    for _ in range(1000):
        c = gerar_cnpj()
        assert len(c) == 14 and c.isdigit()
        d1 = digito_verificador(valores(c[:12]), PESOS_CNPJ_1)
        d2 = digito_verificador(valores(c[:13]), PESOS_CNPJ_2)
        assert c[12:] == f"{d1}{d2}"


def test_gerar_cnpj_alfanumerico_valido():
    alfabeto = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    for _ in range(1000):
        c = gerar_cnpj_alfanumerico()
        assert len(c) == 14
        assert set(c[:12]) <= alfabeto
        assert c[12:].isdigit()
        d1 = digito_verificador(valores(c[:12]), PESOS_CNPJ_1)
        d2 = digito_verificador(valores(c[:13]), PESOS_CNPJ_2)
        assert c[12:] == f"{d1}{d2}"


# ---------- estragar_documento ----------

def test_estragar_dv_muda_o_ultimo_digito():
    for _ in range(1000):
        c = estragar_documento("cpf", "dv")
        assert len(c) == 11
        esperado = digito_verificador(valores(c[:10]), PESOS_CPF_2)
        assert c[10] != str(esperado)


def test_estragar_formato_quebra_tamanho_ou_mascara():
    for _ in range(1000):
        c = estragar_documento("cpf", "formato")
        assert not (len(c) == 11 and c.isdigit())