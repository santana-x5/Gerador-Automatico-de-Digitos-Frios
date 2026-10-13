# Dígito Frio

Gerador de dados fictícios brasileiros para testes de cadastros e fluxos de software.

Permite gerar rapidamente um pequeno conjunto de pessoas fictícias (e documentos de teste) e usá-lo em um formulário ou em um teste automatizado, exportando em **CSV** ou **JSON**.

> ⚠️ **Uso exclusivo para testes.** Os dados são fictícios. Não use em cadastros, compras ou serviços reais.
> A ferramenta **não consulta a Receita Federal** e não confirma a existência ou a titularidade de nenhum documento.

---

## Funcionalidades

### Pessoas fictícias
- Campos: `id`, `nome`, `data_nascimento`, `email`, `ambiente`
- Quantidade de registros: de 1 a 100
- Cenários: adulto ou menor de idade; campos preenchidos ou ausentes; dados válidos ou inválidos
- Identificador sequencial no formato `teste-0001`, `teste-0002`, ...
- Exportação em CSV ou JSON

### Documentos para teste (modo separado)
- CPF, CNPJ numérico e CNPJ alfanumérico
- Dígitos verificadores calculados por **módulo 11**
- Cenários: formato correto, dígitos verificadores inválidos, formato incorreto
- Campo extra `ambiente: teste` e marca `TESTE` na tela e no arquivo exportado
- Lotes pequenos

---

## Tecnologias

- Python 3.12
- FastAPI + Uvicorn (API)
- Pydantic (validação)
- pytest (testes)

---

## Estrutura do projeto

```
digito-frio/
├── back/
│   ├── app/
│   │   ├── main.py              # FastAPI, CORS e rotas
│   │   ├── config.py            # limites, domínio de e-mail, aviso de teste
│   │   ├── geradores/
│   │   │   ├── modulo11.py      # digito_verificador, valor_do_caractere
│   │   │   ├── documentos.py    # CPF, CNPJ, CNPJ alfanumérico
│   │   │   ├── pessoas.py       # nome, data, e-mail, id
│   │   │   └── dados_nomes.py   # listas de nomes e sobrenomes
│   │   ├── servicos/
│   │   │   ├── lote.py          # geração de lotes
│   │   │   └── exportar.py      # CSV e JSON
│   │   ├── schemas/
│   │   │   └── modelos.py       # modelos Pydantic
│   │   └── rotas/
│   │       ├── pessoas.py
│   │       ├── documentos.py
│   │       └── download.py
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── front/
├── docs/
│   └── Digito_Frio_Especificacao.pdf
└── .gitignore
```

---

## Como rodar

### 1. Criar e ativar o ambiente virtual

Windows (PowerShell):

```powershell
cd back
python -m venv venv
venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
cd back
python -m venv venv
source venv/bin/activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Subir a API

```bash
uvicorn app.main:app --reload
```

A documentação interativa fica em `http://127.0.0.1:8000/docs`.

### 4. Rodar os testes

```bash
pytest
```

---

## Endpoints (planejados)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/gerar` | Gera um lote de pessoas fictícias (1 a 100) |
| POST | `/gerar-documentos` | Gera documentos de teste (CPF/CNPJ), em lote pequeno |
| POST | `/download` | Devolve o lote completo em CSV ou JSON |

Exemplo de corpo para `/gerar`:

```json
{
  "quantidade": 10,
  "cenario": "completo",
  "formato": "json"
}
```

---

## Formato dos arquivos exportados

JSON:

```json
[
  {
    "id": "teste-0001",
    "nome": "Fulano de Tal",
    "data_nascimento": "1990-05-14",
    "email": "usuario@example.com",
    "ambiente": "teste"
  }
]
```

CSV:

```csv
id,nome,data_nascimento,email,ambiente
teste-0001,Fulano de Tal,1990-05-14,usuario@example.com,teste
```

No modo "Documentos para teste", o registro inclui também o campo do documento e a marca `TESTE`.

---

## Cálculo dos dígitos verificadores (módulo 11)

```
funcao digito_verificador(valores, pesos):
    soma  = soma de (valores[i] * pesos[i])
    resto = soma mod 11
    se resto == 0 ou resto == 1: retorne 0
    senao: retorne 11 - resto
```

- **CPF:** 9 dígitos de base. Pesos `10..2` para o 1º dígito e `11..2` para o 2º (sobre base + 1º dígito).
- **CNPJ:** 12 caracteres de base. Pesos `5,4,3,2,9,8,7,6,5,4,3,2` e `6,5,4,3,2,9,8,7,6,5,4,3,2`.
- **CNPJ alfanumérico:** mesmo cálculo; cada caractere vale `código ASCII − 48` (A = 17, ..., Z = 42).
- CPF com todos os dígitos iguais (ex.: `111.111.111-11`) é tratado como inválido.

Casos de conferência:

| Tipo | Base | Resultado esperado |
|---|---|---|
| CPF | `123456789` | `123.456.789-09` |
| CNPJ numérico | `123456780001` | `12.345.678/0001-95` |
| CNPJ alfanumérico | `12ABC34501DE` | `12.ABC.345/01DE-35` |

---

## Status

- [x] Fase 1: núcleo de documentos (`modulo11`, `documentos`) com testes
- [ ] Fase 2: pessoas fictícias
- [ ] Fase 3: lote e exportação (CSV/JSON)
- [ ] Fase 4: API
- [ ] Fase 5: testes de API e documentação final

---

## Pontos em aberto

- Campos ausentes: `""`, `null` ou fora do registro
- Limite de menor de idade (menos de 18 anos, a partir da data atual)
- Domínio do e-mail: usar `example.com` (reservado para testes) em vez de `gmail.com`/`yahoo.com`

---

## Equipe

Preencha com os nomes do grupo.

## Licença

Defina a licença do projeto.