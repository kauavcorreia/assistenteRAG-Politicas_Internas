# Chatbot RAG para WhatsApp

Chatbot desenvolvido em Python com arquitetura baseada em RAG (Retrieval-Augmented Generation), integrado ao WhatsApp através do WAHA.

O sistema permite que usuários enviem perguntas pelo WhatsApp e recebam respostas baseadas nos documentos internos previamente indexados, utilizando busca semântica com FAISS, embeddings com BGE-M3 e geração de respostas através do Qwen 2.5 0.5B, executado localmente pelo Ollama.

---

## Visão geral

O projeto foi desenvolvido com o objetivo de criar um assistente capaz de responder perguntas relacionadas às políticas internas de uma empresa utilizando uma base documental própria.

O funcionamento principal é:

```text
                    +-----------------+
                    |    WhatsApp     |
                    +--------+--------+
                             |
                             v
                    +-----------------+
                    |      WAHA       |
                    | WhatsApp HTTP   |
                    |      API        |
                    +--------+--------+
                             | Webhook
                             v
                    +-----------------+
                    |     FastAPI     |
                    |   /webhook      |
                    +--------+--------+
                             |
                             v
                    +-----------------+
                    |       RAG       |
                    |                 |
                    | FAISS + BGE-M3  |
                    +--------+--------+
                             | contexto
                             v
                    +-----------------+
                    |     Ollama      |
                    | Qwen 2.5 0.5B   |
                    +--------+--------+
                             | resposta
                             v
                    +-----------------+
                    |      WAHA       |
                    +--------+--------+
                             |
                             v
                    +-----------------+
                    |    WhatsApp     |
                    +-----------------+
```

---

# Arquitetura RAG

RAG significa Retrieval-Augmented Generation.

Em vez de enviar uma pergunta diretamente para o modelo de linguagem, o sistema primeiro procura informações relevantes na base de conhecimento.

O fluxo é:

```text
Documento
   |
   v
Divisão em chunks
   |
   v
Embeddings
   |
   v
FAISS
   |
   v
Busca semântica
   |
   v
Contexto relevante
   |
   v
LLM
   |
   v
Resposta
```

### Motivo da utilização de RAG

O RAG foi escolhido porque o objetivo do sistema é trabalhar com informações internas e específicas da empresa.

Entre as principais vantagens:

* Não é necessário treinar um modelo de linguagem.
* Os documentos podem ser atualizados.
* Informações relevantes são recuperadas antes da geração.
* Documentos inteiros não precisam ser enviados ao modelo a cada pergunta.
* O modelo pode ser relativamente pequeno.
* A aplicação pode utilizar modelos executados localmente.

---

# Estrutura do projeto

```text
chatbotRAG/
|
├── app/
│   |
│   ├── api/
│   │   ├── chat.py
│   │   ├── whatsapp.py
│   │   └── dto/
│   |
│   ├── data/
│   │   ├── politica_rh.pdf
│   │   └── vectorstore/
│   │       ├── index.faiss
│   │       └── index.pkl
│   |
│   ├── rag/
│   │   ├── chain.py
│   │   ├── loader.py
│   │   ├── splitter.py
│   │   ├── vector_store.py
│   │   └── build_vectorstore.py
│   │   
│   │   
│    ── main.py
│   
│   
│
├── .dockerignore
├── .env
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

# Tecnologias

## Python

Linguagem principal do projeto.

Foi escolhida pela disponibilidade de bibliotecas para:

* Desenvolvimento de APIs.
* Processamento de documentos.
* Embeddings.
* RAG.
* Integração com modelos de linguagem.
* Comunicação HTTP.

---

## FastAPI

Framework utilizado para disponibilizar a API responsável pelo chatbot e pelo recebimento dos webhooks.

Principais responsabilidades:

* Disponibilizar o endpoint `/api/webhook`.
* Receber eventos enviados pelo WAHA.
* Processar mensagens recebidas.
* Executar o pipeline RAG.
* Enviar respostas de volta ao WhatsApp.

---

## LangChain

Utilizado para estruturar o pipeline RAG e integrar:

* Retriever.
* Prompt.
* Modelo de linguagem.
* Parser da resposta.

O fluxo principal é:

```text
Pergunta
   |
   v
Retriever
   |
   v
Contexto
   |
   v
Prompt
   |
   v
LLM
   |
   v
Resposta
```

---

## FAISS

O FAISS é utilizado como banco vetorial do projeto.

Os documentos são transformados em vetores através dos embeddings e armazenados para permitir buscas semânticas.

Os arquivos gerados são:

```text
app/data/vectorstore/
├── index.faiss
└── index.pkl
```

Durante uma pergunta:

```text
"Qual é a política de férias?"
              |
              v
          Embedding
              |
              v
       Busca no FAISS
              |
              v
    Chunks mais relevantes
```

---

## BGE-M3

O BGE-M3 é utilizado para geração dos embeddings.

O modelo transforma os textos em representações vetoriais que podem ser comparadas pelo FAISS.

A responsabilidade do modelo é exclusivamente relacionada à representação semântica dos textos utilizados na busca.

---

## Ollama

O Ollama é utilizado para executar os modelos de inteligência artificial localmente.

Isso permite que o projeto não dependa diretamente de uma API externa para inferência.

A arquitetura é:

```text
Docker
   |
   | HTTP
   v
Host
   |
   v
Ollama :11434
```

O Ollama é executado no host, enquanto a aplicação FastAPI é executada em Docker.

Essa decisão foi tomada principalmente devido às limitações de memória do ambiente utilizado durante o desenvolvimento.

---

## Qwen 2.5 0.5B

Modelo utilizado para geração das respostas:

```text
qwen2.5:0.5b
```

A escolha de um modelo pequeno foi motivada pelas limitações de hardware disponíveis.

O objetivo é executar todo o pipeline localmente utilizando uma quantidade de recursos compatível com o ambiente.

---

## WAHA

O WAHA é utilizado como camada de integração com o WhatsApp.

Ele permite:

* Conectar uma sessão do WhatsApp.
* Receber eventos.
* Enviar mensagens.
* Utilizar webhooks.
* Trabalhar através de uma API HTTP.

O WAHA é executado através do Docker Compose.

---

## Docker

Docker é utilizado para isolar os serviços da aplicação.

Atualmente existem dois serviços principais:

```text
chatbot
   |
   v
FastAPI

waha
   |
   v
WhatsApp HTTP API
```

O Ollama permanece no host devido às características do ambiente de desenvolvimento.

---

# Funcionamento completo

## 1. Usuário envia uma mensagem

Um usuário envia uma pergunta pelo WhatsApp.

Exemplo:

```text
Qual é a política de férias da empresa?
```

---

## 2. WAHA recebe a mensagem

O WAHA recebe o evento do WhatsApp e envia um webhook para:

```text
POST /api/webhook
```

O evento utilizado é:

```text
message.any
```

---

## 3. FastAPI recebe o evento

O endpoint recebe o payload enviado pelo WAHA.

O sistema verifica inicialmente se o evento corresponde a:

```text
message.any
```

Eventos diferentes são ignorados.

---

## 4. Mensagens enviadas pelo próprio bot são ignoradas

O sistema verifica a propriedade:

```text
fromMe
```

Quando o evento foi originado pelo próprio número conectado ao WAHA, ele é ignorado.

Isso evita um loop:

```text
Bot envia mensagem
      |
      v
WAHA gera evento
      |
      v
Webhook recebe
      |
      v
Bot processa novamente
      |
      v
Bot envia outra mensagem
      |
      v
Loop infinito
```

---

## 5. A mensagem é enviada para o RAG

Após as validações, o texto recebido é enviado para a cadeia RAG.

```text
chain.invoke(message)
```

O retriever utiliza o FAISS para encontrar os trechos mais relevantes da documentação.

---

## 6. O contexto é enviado ao modelo

O sistema utiliza um prompt orientando o modelo a responder utilizando as informações recuperadas.

Conceitualmente:

```text
Contexto:
[informações recuperadas]

Pergunta:
[pergunta do usuário]

Resposta:
```

Essa estratégia reduz respostas baseadas em conhecimento externo ao documento utilizado como fonte.

---

## 7. Qwen gera a resposta

O contexto recuperado é enviado para:

```text
qwen2.5:0.5b
```

através do Ollama.

O modelo gera a resposta em português brasileiro.

---

## 8. Resposta retorna para o WhatsApp

Depois da geração:

```text
Resposta do RAG
      |
      v
WAHA /api/sendText
      |
      v
WhatsApp
```

O usuário recebe a resposta diretamente na conversa.

---

# Configuração

O projeto utiliza variáveis de ambiente para informações sensíveis.

Crie um arquivo:

```text
.env
```

com:

```env
WAHA_API_KEY=sua_chave_aqui
```

O arquivo `.env` não deve ser versionado no Git.

---

# Pré-requisitos

Antes de executar o projeto, é necessário possuir:

* Git
* Docker
* Docker Compose
* Python 3.12+
* Ollama
* WhatsApp para realizar a autenticação do WAHA

Também é necessário possuir os modelos utilizados pelo projeto no Ollama:

```text
qwen2.5:0.5b
bge-m3
```

---

# Baixando o projeto

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
```

Entre no diretório:

```bash
cd chatbotRAG
```

---

# Ambiente Python

Caso seja necessário executar ferramentas auxiliares do projeto localmente, crie um ambiente virtual:

```bash
python3 -m venv venv
```

Ative:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

# Configurando o Ollama

Instale o Ollama e baixe os modelos necessários:

```bash
ollama pull qwen2.5:0.5b
```

```bash
ollama pull bge-m3
```

Verifique:

```bash
ollama list
```

Os dois modelos devem aparecer na lista.

---

# Executando com Docker

Construa e inicialize os containers:

```bash
docker compose up --build
```

Para executar em segundo plano:

```bash
docker compose up -d --build
```

Verifique os containers:

```bash
docker ps
```

Os serviços principais estarão disponíveis em:

```text
FastAPI → http://localhost:8001
WAHA    → http://localhost:3000
```

---

# Conectando o WhatsApp

Depois de iniciar o WAHA, acesse:

```text
http://localhost:3000
```

A sessão do WhatsApp deve ser iniciada e autenticada através do QR Code.

Depois da autenticação, a sessão deverá estar em um estado semelhante a:

```text
WORKING
```

---

# Configuração do Webhook

O WAHA deve enviar os eventos para:

```text
http://chatbot:8000/api/webhook
```

Como os serviços estão na mesma rede Docker Compose, o nome:

```text
chatbot
```

é utilizado como hostname interno do container.

Isso evita depender do endereço `localhost` entre containers.

---

# Testando a API

A documentação automática do FastAPI pode ser acessada através de:

```text
http://localhost:8001/docs
```

O endpoint principal do WhatsApp é:

```text
POST /api/webhook
```

---

# Base de conhecimento

Os documentos utilizados pelo RAG ficam em:

```text
app/data/
```

Exemplo:

```text
app/data/politica_rh.pdf
```

O índice vetorial fica em:

```text
app/data/vectorstore/
```

com:

```text
index.faiss
index.pkl
```

---

# Construindo o Vector Store

Quando os documentos da base forem alterados, é necessário reconstruir o índice vetorial.

O processo é:

```text
PDF
 |
 v
Loader
 |
 v
Documentos
 |
 v
Text Splitter
 |
 v
Chunks
 |
 v
BGE-M3
 |
 v
Embeddings
 |
 v
FAISS
```

O processo é executado pelo módulo:

```text
app/rag/build_vectorstore.py
```

---

# Comunicação entre os serviços

A arquitetura utiliza duas formas principais de comunicação.

### Docker para Docker

O WAHA acessa o FastAPI através do nome do serviço:

```text
http://chatbot:8000
```

### Docker para Host

O FastAPI acessa o Ollama executando no host através de:

```text
http://host.docker.internal:11434
```

No Docker Compose foi configurado:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

Isso permite que o container encontre o host.

---

# Firewall

Como o Ollama está executando no host e recebe conexões do Docker, a porta:

```text
11434
```

precisa permitir conexões provenientes da rede Docker utilizada pela aplicação.

No ambiente atual, a rede utilizada pelo projeto é:

```text
172.24.0.0/16
```

Exemplo de regra utilizada no ambiente Linux:

```bash
sudo ufw allow from 172.24.0.0/16 to any port 11434 proto tcp
```

Essa configuração é específica do ambiente e pode variar dependendo da rede criada pelo Docker.

---

# Decisões técnicas

## Execução local da IA

Foi decidido executar a inferência localmente através do Ollama.

Motivos:

* Evitar dependência de APIs externas.
* Reduzir custos de inferência.
* Manter os documentos internos fora de serviços externos.
* Permitir desenvolvimento local após a configuração dos modelos.

---

## Utilização de um modelo pequeno

O projeto utiliza:

```text
qwen2.5:0.5b
```

em vez de modelos maiores.

A decisão foi motivada principalmente pelas limitações de memória do ambiente de desenvolvimento.

---

## Separação entre embeddings e LLM

O modelo utilizado para embeddings é:

```text
bge-m3
```

Enquanto o modelo generativo é:

```text
qwen2.5:0.5b
```

Cada modelo possui uma responsabilidade diferente:

```text
BGE-M3
    |
    +-- Representação semântica
    |
    +-- Busca

Qwen
    |
    +-- Interpretação do contexto
    |
    +-- Geração da resposta
```

---

## FAISS em vez de banco vetorial externo

O FAISS foi escolhido para a primeira versão porque:

* É simples de configurar.
* Funciona localmente.
* Possui bom desempenho para busca vetorial.
* Não exige um serviço adicional.
* É suficiente para a base documental inicial.

Em uma futura versão de produção, pode ser avaliada a utilização de um banco vetorial persistente ou PostgreSQL com extensão vetorial.

---

## WAHA como camada de integração

A aplicação não implementa diretamente o protocolo de comunicação com o WhatsApp.

O WAHA funciona como uma camada intermediária:

```text
WhatsApp
   |
   v
WAHA
   |
   v
API Python
```

Isso mantém a aplicação desacoplada da implementação específica da comunicação com o WhatsApp.

---

# Segurança

Algumas medidas adotadas:

* API Key do WAHA armazenada em variável de ambiente.
* `.env` não versionado.
* Validação do tipo de evento recebido.
* Filtro de mensagens `fromMe`.
* Comunicação interna entre containers através da rede Docker.
* Acesso ao Ollama restrito à rede necessária no firewall.

Nunca publique:

```text
.env
```

ou qualquer API Key no GitHub.

Caso uma credencial seja exposta, ela deve ser revogada e substituída.

---

# Limitações atuais

A versão atual é funcional, mas ainda possui pontos que podem ser melhorados antes de uma utilização em produção.

## Processamento síncrono

Atualmente o webhook aguarda o processamento completo do RAG:

```text
Webhook
   |
   v
RAG
   |
   v
LLM
   |
   v
WAHA
   |
   v
Resposta HTTP
```

Isso pode aumentar o tempo de resposta do webhook.

---

## Tratamento de erros

Pode ser aprimorado o tratamento de:

* Indisponibilidade do Ollama.
* Timeout do modelo.
* Falhas do FAISS.
* Falhas do WAHA.
* Mensagens inválidas.
* Mensagens sem texto.
* Indisponibilidade temporária dos serviços.

---

## Mensagens multimídia

A primeira versão está focada principalmente em mensagens de texto.

Futuras versões podem incluir:

* Áudio.
* Imagem.
* Documentos.
* Localização.
* Outros eventos do WhatsApp.

---

# Próximas evoluções

Possíveis melhorias para versões futuras:

* Processamento assíncrono.
* Filas com Redis/Celery.
* Sistema de logs estruturados.
* Tratamento centralizado de exceções.
* Monitoramento.
* Health checks.
* Autenticação adicional da API.
* Gerenciamento de múltiplos documentos.
* Atualização automática da base RAG.
* Suporte a múltiplos usuários.
* Histórico de conversas.
* Memória conversacional.
* Suporte a mensagens de áudio.
* Testes automatizados.
* CI/CD.
* Deploy em servidor.
* Banco de dados para persistência de informações.

---

# Fluxo de desenvolvimento

O projeto foi desenvolvido de forma incremental:

```text
1. Construção do RAG
        |
        v
2. Teste local da API
        |
        v
3. Containerização
        |
        v
4. Configuração do Ollama
        |
        v
5. Integração com WAHA
        |
        v
6. Configuração do webhook
        |
        v
7. Teste com WhatsApp real
        |
        v
8. Diagnóstico da comunicação Docker → Ollama
        |
        v
9. Validação ponta a ponta
```

A versão atual possui o fluxo completo funcionando com uma mensagem real enviada através de outro número de WhatsApp.

---

# Comandos úteis

### Iniciar

```bash
docker compose up
```

### Iniciar em segundo plano

```bash
docker compose up -d
```

### Rebuild

```bash
docker compose up --build
```

### Parar

```bash
docker compose down
```

### Ver containers

```bash
docker ps
```

### Ver logs do chatbot

```bash
docker logs -f chatbot-rag
```

### Ver logs do WAHA

```bash
docker logs -f waha
```

### Ver modelos do Ollama

```bash
ollama list
```

### Testar Ollama

```bash
curl http://l
```
