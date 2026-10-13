"""Núcleo de geração e validação de documentos brasileiros (CPF/CNPJ)."""

import random

"""Núcleo de geração e validação de documentos brasileiros (CPF/CNPJ)."""


def valor_do_caractere(c):
    """Converte um caractere no valor numérico usado no cálculo do dígito verificador.

    Dígitos '0'-'9' valem 0-9. Letras 'A'-'Z' valem 17-42
    (ord('A') = 65, e 65 - 48 = 17), como no CNPJ alfanumérico.
    """
    return ord(c) - 48

def digito_verificador(valores, pesos):
    """Calcula um dígito verificador (módulo 11).

    valores: lista de inteiros (use valor_do_caractere em cada caractere).
    pesos: lista de pesos, do mesmo tamanho de valores.

    Soma os produtos valor * peso. Se o resto da divisão por 11
    for 0 ou 1, o dígito é 0; senão, é 11 - resto.
    """
    soma = sum(v * p for v, p in zip(valores, pesos))
    resto = soma % 11
    if resto in (0, 1):
        return 0
    return 11 - resto

def gerar_cpf():
    """Gera um CPF válido, sem máscara (11 dígitos, como string).

    Rejeita CPFs com todos os dígitos iguais (111.111.111-11 etc.),
    que passam no cálculo mas são considerados inválidos.
    """
    while True:
        base = [random.randint(0, 9) for _ in range(9)]
        dv1 = digito_verificador(base, list(range(10, 1, -1)))        # pesos 10..2
        dv2 = digito_verificador(base + [dv1], list(range(11, 1, -1)))  # pesos 11..2
        digitos = base + [dv1, dv2]
        if len(set(digitos)) > 1:
            return "".join(str(n) for n in digitos)

PESOS_CNPJ_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
PESOS_CNPJ_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def gerar_cnpj():
    """Gera um CNPJ válido, sem máscara (14 dígitos, como string).

    Os 12 primeiros dígitos são a base: 8 da raiz + 4 da filial
    (aqui, a filial é sorteada também).
    """
    base = [random.randint(0, 9) for _ in range(12)]
    dv1 = digito_verificador(base, PESOS_CNPJ_1)
    dv2 = digito_verificador(base + [dv1], PESOS_CNPJ_2)
    return "".join(str(n) for n in base + [dv1, dv2])

ALFABETO_CNPJ = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gerar_cnpj_alfanumerico():
    """Gera um CNPJ alfanumérico válido, sem máscara (14 caracteres).

    Os 12 primeiros caracteres (a base) são sorteados entre 0-9 e A-Z.
    Os 2 dígitos verificadores continuam sendo numéricos.
    """
    base = "".join(random.choice(ALFABETO_CNPJ) for _ in range(12))
    valores = [valor_do_caractere(c) for c in base]
    dv1 = digito_verificador(valores, PESOS_CNPJ_1)
    dv2 = digito_verificador(valores + [dv1], PESOS_CNPJ_2)
    return base + str(dv1) + str(dv2)

def formatar_cpf(cpf):
    """Aplica a máscara no CPF: 12345678909 -> 123.456.789-09."""
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_cnpj(cnpj):
    """Aplica a máscara no CNPJ: 12345678000195 -> 12.345.678/0001-95.

    Funciona também para o alfanumérico: 12ABC34501DE35 -> 12.ABC.345/01DE-35.
    """
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def estragar_documento(tipo="cpf", modo="dv"):
    """Gera um documento válido e o estraga de propósito (útil para testar validações).

    tipo: "cpf", "cnpj" ou "cnpj_alfanumerico".
    modo:
      "dv"      -> mantém o formato, mas troca o último dígito (dígito verificador inválido).
      "formato" -> quebra o tamanho (falta ou sobra um caractere) ou a máscara.
    """
    geradores = {
        "cpf": (gerar_cpf, formatar_cpf),
        "cnpj": (gerar_cnpj, formatar_cnpj),
        "cnpj_alfanumerico": (gerar_cnpj_alfanumerico, formatar_cnpj),
    }
    if tipo not in geradores:
        raise ValueError(f"tipo inválido: {tipo}")
    if modo not in ("dv", "formato"):
        raise ValueError(f"modo inválido: {modo}")

    gerar, formatar = geradores[tipo]
    doc = gerar()

    if modo == "dv":
        # soma 1..9 ao último dígito (mod 10): garante que ele sempre muda
        novo = (int(doc[-1]) + random.randint(1, 9)) % 10
        return doc[:-1] + str(novo)

    defeito = random.choice(["falta", "sobra", "mascara"])
    if defeito == "falta":
        return doc[:-1]
    if defeito == "sobra":
        return doc + str(random.randint(0, 9))
    mascarado = formatar(doc)
    if random.random() < 0.5:
        return mascarado.replace(".", ",", 1)   # troca um ponto por vírgula
    return mascarado.replace("-", "", 1)        # remove o hífen

