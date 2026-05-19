# 💸 DimDimApp — API REST Conteinerizada

> **Checkpoint 3 — DevOps Tools & Cloud Computing**
> Curso: Análise e Desenvolvimento de Sistemas (ADS) | Turma: 2TDSR | FIAP

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Azure](https://img.shields.io/badge/Microsoft_Azure-Cloud-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)

</div>

---

## 👩‍💻 Integrantes

| Nome | RM |
|---|---|
| Maria Gabriela Landim Severo | RM 565146 |
| Samara Porto de Oliveira | RM 559072 |

---

## 📋 Sobre o Projeto

A **DimDimApp** é uma **API REST** para gerenciamento de contas bancárias, desenvolvida em **Python (Flask)** e integrada a um banco de dados **PostgreSQL 15**. Todo o ambiente é orquestrado via **Docker**, implantado em uma Máquina Virtual **AlmaLinux** hospedada na **Microsoft Azure**.

O projeto demonstra na prática os pilares fundamentais de DevOps e Cloud Computing:

- ☁️ **Deploy em Nuvem (Azure)** — infraestrutura 100% fora do localhost
- 🌐 **Rede Isolada (Docker Network)** — comunicação interna segura via bridge dedicada
- 💾 **Persistência de Dados (Docker Volume)** — dados sobrevivem a reinicializações e destruição de containers
- 🔒 **Segurança (Dockerfile Non-Root)** — API executa sob usuário restrito, sem privilégios de root

---

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────┐
│              Microsoft Azure (AlmaLinux VM)              │
│                                                         │
│   ┌──────────────────────────────────────────────────┐  │
│   │              rede_dimdim (bridge)                │  │
│   │                                                  │  │
│   │   ┌─────────────────┐    ┌──────────────────┐   │  │
│   │   │   app_565146    │    │   banco_565146   │   │  │
│   │   │  (Flask / API)  │───▶│  (PostgreSQL 15) │   │  │
│   │   │   porta: 5000   │    │   porta: 5432    │   │  │
│   │   │   user: dimdim  │    │ vol: volume_db_  │   │  │
│   │   │   dir: /app_    │    │      dimdim      │   │  │
│   │   │     dimdim      │    └──────────────────┘   │  │
│   │   └─────────────────┘                            │  │
│   └──────────────────────────────────────────────────┘  │
│                         │                               │
│              porta 5000 exposta                         │
└─────────────────────────────────────────────────────────┘
         ▲
         │  HTTP Requests (curl / cliente REST)
         │
      Usuário
```

---

## 📂 Estrutura do Repositório

```
cp3-devops-dimdim/
│
├── app.py              # API Flask — rotas CRUD completas (/init, /contas)
├── Dockerfile          # Imagem customizada com segurança non-root
├── requirements.txt    # Dependências: Flask + psycopg2-binary
└── README.md           # Documentação completa do projeto
```

---

## 🔗 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/init` | Cria a tabela `contas` no banco de dados |
| `POST` | `/contas` | Cria uma nova conta bancária |
| `GET` | `/contas` | Lista todas as contas cadastradas |
| `PUT` | `/contas/<id>` | Atualiza o saldo de uma conta pelo ID |
| `DELETE` | `/contas/<id>` | Remove uma conta pelo ID |

### Exemplo de payload para criação de conta (POST):
```json
{
  "titular": "Maria Gabriela",
  "saldo": 2500.00
}
```

---

## 🔒 Segurança — Dockerfile Non-Root

O `Dockerfile` foi construído seguindo boas práticas de segurança de containers. A API **nunca executa como root**, mitigando riscos de escalada de privilégio:

```dockerfile
FROM python:3.10-slim

WORKDIR /app_dimdim

COPY requirements.txt .
COPY app.py .

RUN pip install --no-cache-dir -r requirements.txt

ENV AMBIENTE=producao
ENV PORTA=5000

# Criação do usuário restrito e transferência de ownership do diretório
RUN useradd -m dimdimuser && chown -R dimdimuser /app_dimdim

# Troca para o usuário sem privilégios — nunca executa como root
USER dimdimuser

EXPOSE 5000

CMD ["python", "app.py"]
```

**Verificações de segurança:**
- ✅ Usuário de execução: `dimdimuser` (não-root)
- ✅ Diretório isolado: `/app_dimdim`
- ✅ Imagem base minimalista: `python:3.10-slim`
- ✅ Instalação sem cache: `--no-cache-dir`

---

## 🛠️ Guia de Implantação Completo

> Execute todos os comandos a partir do terminal da sua instância na nuvem (VM Azure com AlmaLinux).

### Pré-requisito: Clonar o Repositório

```bash
git clone https://github.com/gabrielalandim/cp3-devops-dimdim.git
cd cp3-devops-dimdim
```

---

### Passo 1 — Criar a Rede Docker Isolada

Cria a rede bridge dedicada `rede_dimdim`, que permite que os containers se comuniquem pelo nome do host, sem expor os serviços diretamente à internet.

```bash
docker network create rede_dimdim
```

**✅ Verificação:**
```bash
docker network ls
# rede_dimdim deve aparecer na listagem com driver "bridge"
```

---

### Passo 2 — Subir o Container do Banco de Dados (PostgreSQL 15)

Cria o container do PostgreSQL com:
- Nome identificado com o RM (`banco_565146`)
- Conectado à rede isolada `rede_dimdim`
- Volume nomeado para persistência dos dados
- Credenciais injetadas via variáveis de ambiente

```bash
docker container run -d \
  --name banco_565146 \
  --network rede_dimdim \
  -v volume_db_dimdim:/var/lib/postgresql/data \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=senhaforte \
  -e POSTGRES_DB=dimdimdb \
  postgres:15-alpine
```

---

### Passo 3 — Build da Imagem Personalizada da Aplicação

Compila o `Dockerfile` e gera a imagem local `app_python_dimdim` com todas as configurações de segurança e dependências instaladas.

```bash
docker image build -t app_python_dimdim .
```

**✅ Verificação:**
```bash
docker image ls
# app_python_dimdim deve aparecer na listagem
```

---

### Passo 4 — Subir o Container da API Flask

Executa o container da API com:
- Nome identificado com o RM (`app_565146`)
- Porta `5000` da VM mapeada para a porta `5000` do container
- Conectado à mesma rede do banco (`rede_dimdim`)
- Variáveis de ambiente apontando para o host do banco pelo nome DNS interno

```bash
docker container run -d \
  --name app_565146 \
  --network rede_dimdim \
  -p 5000:5000 \
  -e DB_HOST=banco_565146 \
  -e DB_NAME=dimdimdb \
  -e DB_USER=admin \
  -e DB_PASS=senhaforte \
  app_python_dimdim
```

---

## 🔍 Auditoria e Validação dos Requisitos

### 1. Verificar Status e Nomes dos Containers

```bash
docker container ls
```

**Retorno esperado:** os dois containers com status `Up` e os nomes corretos.

```
CONTAINER ID   IMAGE              STATUS        NAMES
xxxxxxxxxxxx   app_python_dimdim  Up X minutes  app_565146
xxxxxxxxxxxx   postgres:15-alpine Up X minutes  banco_565146
```

---

### 2. Validar Segurança — Usuário Non-Root e Diretório Isolado

Acesse o shell interativo do container da aplicação:

```bash
docker container exec -it app_565146 bash
```

Dentro do container, execute:

```bash
# Verifica o diretório de trabalho
pwd
# Retorno esperado: /app_dimdim

# Verifica o usuário em execução
whoami
# Retorno esperado: dimdimuser

# Sai do container
exit
```

---

### 3. Testar os Endpoints da API via cURL

**Inicializar o banco de dados (criar a tabela):**
```bash
curl http://localhost:5000/init
# Retorno esperado: {"message":"Tabela criada com sucesso!"}
```

**CREATE — Inserir uma nova conta:**
```bash
curl -X POST http://localhost:5000/contas \
  -H "Content-Type: application/json" \
  -d '{"titular": "Maria Gabriela", "saldo": 2500.00}'
# Retorno esperado: {"id": 1, "message": "Conta criada!"}
```

**READ — Listar todas as contas:**
```bash
curl http://localhost:5000/contas
# Retorno esperado: lista JSON com os registros inseridos
```

**UPDATE — Atualizar o saldo de uma conta:**
```bash
curl -X PUT http://localhost:5000/contas/1 \
  -H "Content-Type: application/json" \
  -d '{"saldo": 3500.00}'
# Retorno esperado: {"message": "Conta atualizada!"}
```

**DELETE — Remover uma conta:**
```bash
curl -X DELETE http://localhost:5000/contas/1
# Retorno esperado: {"message": "Conta deletada!"}
```

---

### 4. Verificar Persistência de Dados via psql

Conecte-se diretamente ao container do PostgreSQL para confirmar que os dados foram gravados no volume:

```bash
docker container exec -it banco_565146 psql -U admin -d dimdimdb
```

No prompt do banco (`dimdimdb=#`), execute:

```sql
SELECT * FROM contas;
```

**Retorno esperado:** todos os registros inseridos via API Flask listados na tabela.

Para sair do console psql:
```
\q
```

---

### 5. Verificar o Volume de Persistência

```bash
docker volume inspect volume_db_dimdim
```

Confirma que o volume foi criado e está mapeado corretamente.

---

### 6. Inspecionar a Rede Isolada

```bash
docker network inspect rede_dimdim
```

Confirma que ambos os containers (`app_565146` e `banco_565146`) estão conectados à mesma rede bridge.

---

## 🧹 Limpeza do Ambiente (Teardown)

Para remover todos os recursos criados:

```bash
# Parar e remover os containers
docker container stop app_565146 banco_565146
docker container rm app_565146 banco_565146

# Remover a imagem customizada
docker image rm app_python_dimdim

# Remover a rede isolada
docker network rm rede_dimdim

# Remover o volume (ATENÇÃO: apaga os dados persistidos)
docker volume rm volume_db_dimdim
```

---

## 🧰 Tecnologias e Ferramentas Utilizadas

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.10 | Linguagem da aplicação backend |
| Flask | 2.x | Framework web para a API REST |
| psycopg2-binary | latest | Adaptador Python para PostgreSQL |
| PostgreSQL | 15-alpine | Banco de dados relacional |
| Docker | latest | Conteinerização da aplicação |
| Docker Network | bridge | Rede isolada entre containers |
| Docker Volume | named | Persistência de dados do banco |
| Microsoft Azure | — | Provedor de nuvem (VM AlmaLinux) |

---

## 🎥 Demonstração em Vídeo

A implantação e validação completa do projeto foram gravadas e estão disponíveis no link abaixo:

📺 **[Assista à demonstração no YouTube](https://youtu.be/rnluPW2Bnoc?feature=shared)**

---

## 📌 Referências

- [Documentação oficial do Docker](https://docs.docker.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL 15 Docker Hub](https://hub.docker.com/_/postgres)
- [Microsoft Azure — Virtual Machines](https://azure.microsoft.com/pt-br/products/virtual-machines)
- [Docker Security — Non-root users](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user)

---

<div align="center">

Feito com 💜 por **Maria Gabriela Landim Severo** e **Samara Porto** — FIAP 2025

</div>
