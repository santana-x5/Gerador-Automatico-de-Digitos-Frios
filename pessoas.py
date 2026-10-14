"""Geração de pessoas fictícias brasileiras para testes."""

import random
import string
import unicodedata
from datetime import date, timedelta
from documentos import estragar_documento, formatar_cpf, gerar_cpf

NOMES_MASCULINOS = [
    "Miguel", "Arthur", "Heitor", "Davi", "Gabriel", "Bernardo", "Samuel",
    "João", "Pedro", "Lucas", "Matheus", "Rafael", "Gustavo", "Felipe",
    "Henrique", "Carlos", "Eduardo", "Rodrigo", "Thiago", "Leonardo",
]

NOMES_FEMININOS = [
    "Helena", "Alice", "Laura", "Manuela", "Sophia", "Isabella", "Luiza",
    "Júlia", "Beatriz", "Mariana", "Fernanda", "Camila", "Larissa", "Amanda",
    "Letícia", "Gabriela", "Patrícia", "Aline", "Renata", "Carolina",
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
    "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
    "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa",
    "Rocha", "Dias", "Nascimento", "Andrade", "Moreira", "Nunes", "Marques",
    "Machado", "Mendes", "Freitas", "Cardoso", "Ramos", "Teixeira", "Araújo",
]


def gerar_nome():
    """Gera um nome completo fictício: nome + dois sobrenomes diferentes."""
    nome = random.choice(NOMES_MASCULINOS + NOMES_FEMININOS)
    sobrenome1, sobrenome2 = random.sample(SOBRENOMES, 2)
    return f"{nome} {sobrenome1} {sobrenome2}"

def _subtrair_anos(data, anos):
    """Volta 'anos' anos. Se cair em 29/02 de ano não bissexto, usa 28/02."""
    try:
        return data.replace(year=data.year - anos)
    except ValueError:
        return data.replace(year=data.year - anos, day=28)


def calcular_idade(nascimento, hoje=None):
    """Idade em anos completos na data 'hoje' (padrão: data atual)."""
    hoje = hoje or date.today()
    aniversario_ja_passou = (hoje.month, hoje.day) >= (nascimento.month, nascimento.day)
    return hoje.year - nascimento.year - (0 if aniversario_ja_passou else 1)


def gerar_data_nascimento(cenario, hoje=None):
    """Gera uma data de nascimento (objeto date) sempre relativa à data atual.

    cenario:
      "adulto" -> 18 anos ou mais (até 80 anos).
      "menor"  -> menos de 18 anos (de 0 a 17).
    hoje: só para testes; por padrão usa a data atual.
    """
    hoje = hoje or date.today()
    limite_18 = _subtrair_anos(hoje, 18)  # quem nasceu nesse dia faz 18 anos hoje

    if cenario == "adulto":
        inicio = _subtrair_anos(hoje, 80)
        fim = limite_18
    elif cenario == "menor":
        inicio = limite_18 + timedelta(days=1)  # faz 18 anos amanhã
        fim = hoje
    else:
        raise ValueError(f"cenário inválido: {cenario}")

    return date.fromordinal(random.randint(inicio.toordinal(), fim.toordinal()))

DOMINIO_EMAIL = "example.com"


def _sem_acentos(texto):
    """'Letícia Araújo' -> 'Leticia Araujo'."""
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def _parte_local(nome=None):
    """Parte antes do @: só letras minúsculas e números.

    Com nome: primeiro + último nome + número (ex.: camilabarbosa42).
    Sem nome: letras aleatórias + número.
    """
    if nome:
        partes = _sem_acentos(nome).lower().split()
        base = partes[0] + partes[-1]
    else:
        base = "".join(random.choice(string.ascii_lowercase) for _ in range(random.randint(5, 10)))
    return base + str(random.randint(1, 99))


def gerar_email(valido=True, nome=None):
    """Gera um e-mail fictício, sempre no domínio example.com.

    valido=True  -> letras/números@example.com
    valido=False -> um destes defeitos, sorteado:
                    sem '@', sem domínio, ou com espaço.
    nome: opcional; se passado, o e-mail é derivado dele (usaremos no item 14).
    """
    local = _parte_local(nome)

    if valido:
        return f"{local}@{DOMINIO_EMAIL}"

    defeito = random.choice(["sem_arroba", "sem_dominio", "com_espaco"])
    if defeito == "sem_arroba":
        return f"{local}{DOMINIO_EMAIL}"
    if defeito == "sem_dominio":
        return f"{local}@"
    pos = random.randint(1, len(local) - 1)
    return f"{local[:pos]} {local[pos:]}@{DOMINIO_EMAIL}"

def gerar_id(n):
    """Gera o ID da n-ésima pessoa do lote: 1 -> 'teste-0001', 42 -> 'teste-0042'.

    n começa em 1. Acima de 9999 o número simplesmente ganha mais dígitos
    (teste-10000).
    """
    if n < 1:
        raise ValueError("n deve ser 1 ou maior")
    return f"teste-{n:04d}"

CAMPOS_OPCIONAIS = ["nome", "cpf", "data_nascimento", "email"]
CAMPOS_COM_FORMATO = ["cpf", "data_nascimento", "email"]
MODOS_AUSENTE = ("vazio", "nulo", "omitido")
CENARIOS = ("completo", "ausentes", "invalidos")
DATAS_INVALIDAS = ["2000-02-30", "2000-13-01", "31/12/2000", "0000-00-00", "ontem"]


def _cpf_invalido():
    """CPF inválido: ou com dígito verificador errado (mantendo a máscara),
    ou com formato quebrado (tamanho ou máscara)."""
    if random.random() < 0.5:
        return formatar_cpf(estragar_documento("cpf", "dv"))
    return estragar_documento("cpf", "formato")


def gerar_pessoa(i, cenario="completo", faixa="adulto", modo_ausente="vazio"):
    """Monta o registro de uma pessoa fictícia (um dicionário).

    i: posição da pessoa no lote (1, 2, 3...), usada no ID.
    cenario:
      "completo"  -> todos os campos válidos.
      "ausentes"  -> de 1 a 3 campos (entre nome, cpf, data_nascimento, email)
                     ficam ausentes, conforme modo_ausente.
      "invalidos" -> de 1 a 3 campos (entre cpf, data_nascimento, email)
                     ficam com formato inválido.
    faixa: "adulto" ou "menor", repassado para gerar_data_nascimento.
    modo_ausente: "vazio" ("")  |  "nulo" (None/null)  |  "omitido" (sem a chave).
    id e ambiente nunca ficam ausentes nem inválidos.
    """
    if cenario not in CENARIOS:
        raise ValueError(f"cenário inválido: {cenario}")
    if modo_ausente not in MODOS_AUSENTE:
        raise ValueError(f"modo_ausente inválido: {modo_ausente}")

    nome = gerar_nome()
    pessoa = {
        "id": gerar_id(i),
        "ambiente": "teste",
        "nome": nome,
        "cpf": formatar_cpf(gerar_cpf()),
        "data_nascimento": gerar_data_nascimento(faixa).isoformat(),
        "email": gerar_email(True, nome),
    }

    if cenario == "ausentes":
        for campo in random.sample(CAMPOS_OPCIONAIS, random.randint(1, 3)):
            if modo_ausente == "vazio":
                pessoa[campo] = ""
            elif modo_ausente == "nulo":
                pessoa[campo] = None
            else:
                del pessoa[campo]

    elif cenario == "invalidos":
        for campo in random.sample(CAMPOS_COM_FORMATO, random.randint(1, 3)):
            if campo == "cpf":
                pessoa[campo] = _cpf_invalido()
            elif campo == "data_nascimento":
                pessoa[campo] = random.choice(DATAS_INVALIDAS)
            else:
                pessoa[campo] = gerar_email(False, nome)

    return pessoa