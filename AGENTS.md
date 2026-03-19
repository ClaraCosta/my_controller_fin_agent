# Guia de Referência do Projeto — Plataforma Web de Operações com IA

## Objetivo deste arquivo

Este documento serve como **guia-base de arquitetura, escopo e validação** do projeto.  
A IA, ao auxiliar no desenvolvimento, deve sempre usar este material como referência para:

- validar se novas implementações estão dentro do escopo
- evitar desvio de stack
- manter consistência arquitetural
- preservar o objetivo do produto
- garantir aderência ao MVP definido
- sugerir evoluções sem quebrar a proposta principal

---

# 1. Resumo do projeto

Este projeto consiste em uma **plataforma web de operações com IA**, com foco em automação, integrações, OCR e apoio operacional.

A aplicação deve permitir que usuários autenticados:

- façam login
- visualizem dashboard
- consultem clientes
- consultem fornecedores
- consultem contatos
- criem solicitações operacionais
- anexem documentos
- processem documentos via OCR
- utilizem um agente com IA para interpretar a demanda
- consultem dados de clientes
- chamem APIs externas
- classifiquem prioridade
- gerem resposta padronizada
- registrem toda a execução em logs e histórico
- utilizem um chat com IA em linguagem natural para consultas, dúvidas operacionais e geração de relatórios simplificados


## Diferencial principal: Chat central com IA em linguagem natural

Um dos principais diferenciais desta plataforma é a existência de um **chat central com IA**, disponível logo após o login do usuário.

Esse chat deve funcionar como a interface principal de interação com o sistema, permitindo que o usuário se comunique em **linguagem natural** para executar ações, obter informações e acelerar rotinas operacionais.

Importante: **não devem existir chats separados por assunto**.  
O mesmo chat deve contemplar consultas operacionais, clientes, contatos, solicitações, documentos e relatórios simplificados.

O chatbot deve ser capaz de:

- identificar registros de clientes, contatos e solicitações
- responder dúvidas sobre dados disponíveis no sistema
- interpretar perguntas em linguagem natural
- consultar informações relevantes no banco de dados
- resumir dados encontrados de forma clara
- gerar relatórios simplificados com base em filtros ou contexto informado pelo usuário
- apoiar a navegação operacional da plataforma
- utilizar contexto de documentos processados via OCR quando necessário

Exemplos de uso esperados:

- "Quais clientes estão com solicitações críticas?"
- "Busque o contato principal da empresa X"
- "Me mostre os últimos atendimentos relacionados ao cliente Y"
- "Resuma o que foi processado neste documento"
- "Gere um relatório simplificado das solicitações de alta prioridade desta semana"

Este chat não deve ser tratado apenas como um assistente conversacional genérico.  
Ele deve atuar como uma **interface inteligente de consulta, apoio operacional e exploração de dados do sistema**, sempre com rastreabilidade, uso controlado de contexto e possibilidade de evolução futura.

---

# 2. Objetivo funcional do sistema

O sistema deve simular uma solução corporativa real, onde um operador ou analista pode registrar uma solicitação operacional e receber apoio de um agente de IA capaz de:

- entender o contexto da solicitação
- interpretar texto livre
- utilizar texto extraído de documentos
- consultar dados internos
- integrar com APIs externas
- classificar urgência/prioridade
- retornar uma resposta estruturada
- manter rastreabilidade de todo o processo

---

# 3. Stack oficial do projeto

A IA deve respeitar esta stack como padrão principal do projeto.

## Backend
- Python
- FastAPI
- SQLAlchemy
- Alembic
- pytest

## Inteligência Artificial
- Ollama

## Banco de dados
- PostgreSQL

## OCR
- Tesseract

## Frontend
- HTML
- JavaScript
- Tailwind CSS

## Infraestrutura
- Docker
- Docker Compose

## Extras recomendados
- JWT para autenticação
- logs estruturados em JSON
- organização por camadas
- integração via REST APIs

---

# 4. Importante sobre a stack

## 4.1 FastAPI
O framework web/API oficial do projeto é **FastAPI**.

**Não confundir com `fastai`**, que é uma biblioteca de deep learning e não deve ser usada como base da aplicação web.

## 4.2 Ollama
O Ollama será o provider principal de IA local, rodando como serviço acessado via API HTTP.

## 4.3 Tesseract
O Tesseract será o OCR padrão inicial do projeto para leitura de documentos e imagens.

## 4.4 Frontend
O frontend será server-rendered ou baseado em páginas HTML com JavaScript e Tailwind, sem necessidade inicial de React.

---

# 5. Escopo principal do MVP

O MVP deve conter obrigatoriamente:

- login
- chat operacional com IA após login
- dashboard
- listagem de clientes
- base de fornecedores
- listagem de contatos
- tela de nova solicitação
- upload de documento
- processamento OCR
- agente com IA
- consulta de dados do cliente
- chamada a API externa
- classificação de prioridade
- geração de resposta padronizada
- logs e histórico de execução


---

# 6. Funcionalidades principais esperadas

## 6.1 Autenticação
- login com email e senha
- proteção de rotas
- controle básico de sessão/token

## 6.2 Dashboard
- total de clientes
- total de contatos
- total de solicitações
- solicitações recentes
- visão por prioridade
- status das execuções

## 6.3 Clientes
- listagem de clientes
- busca simples
- detalhe do cliente
- dados básicos de cadastro

## 6.4 Fornecedores
- listagem de fornecedores
- busca simples
- detalhe do fornecedor
- dados básicos de cadastro
- possibilidade futura de vínculo com documentos, solicitações e fluxo fiscal

## 6.5 Contatos
- listagem de contatos
- relacionamento com cliente
- exibição de email, telefone e cargo

## 6.6 Solicitações operacionais
- criação de solicitação em texto livre
- vínculo com cliente
- upload opcional de documento
- disparo do processamento do agente

## 6.7 OCR
- recebimento de arquivo
- extração de texto com Tesseract
- persistência do texto extraído
- associação do texto à solicitação

## 6.8 Agente de IA
- interpretação da solicitação
- análise do texto OCR
- decisão de tools
- geração de resposta final

## 6.9 Integrações
- consulta de dados do cliente
- chamada a API externa
- consolidação dos resultados

## 6.10 Priorização
- classificação em baixa, média, alta ou crítica
- justificativa da prioridade

## 6.11 Resposta padronizada
- resumo do caso
- prioridade
- resultado da análise
- próximos passos sugeridos

## 6.12 Logs e histórico
- registrar o fluxo completo
- permitir rastreabilidade
- salvar eventos importantes no banco
- salvar logs estruturados

## 6.13 Chat central com IA
- interface conversacional em linguagem natural
- identificação de registros no sistema
- resposta a dúvidas operacionais
- resposta a dúvidas sobre clientes, fornecedores, contatos e solicitações
- geração de relatórios simplificados
- uso de contexto de cliente, fornecedor, solicitação e documento
- rastreabilidade das interações
---

# 7. Fluxos principais

## 7.1 Fluxo sem documento
1. usuário faz login
2. acessa a tela de nova solicitação
3. informa cliente e descrição da demanda
4. backend monta o contexto
5. agente interpreta a solicitação
6. tools são executadas conforme necessário
7. sistema classifica prioridade
8. resposta padronizada é gerada
9. logs e histórico são registrados
10. resultado é exibido ao usuário

## 7.2 Fluxo com documento
1. usuário faz login
2. cria solicitação
3. anexa documento
4. sistema processa OCR
5. texto extraído é adicionado ao contexto
6. agente interpreta solicitação + OCR
7. tools são executadas
8. prioridade é definida
9. resposta final é gerada
10. logs e histórico são persistidos

## 7.3 Fluxo do chat central
1. usuário faz login
2. acessa o chat da plataforma
3. envia uma pergunta em linguagem natural
4. sistema interpreta a intenção
5. agente consulta dados internos e/ou ferramentas disponíveis
6. sistema retorna resposta estruturada ou resumo
7. interação é registrada em histórico e logs
---

# 8. Arquitetura recomendada

O projeto deve seguir uma arquitetura em camadas, separando responsabilidades.

## 8.1 Camadas principais

### Frontend
Responsável por:
- login
- dashboard
- páginas de clientes
- páginas de fornecedores
- páginas de contatos
- tela de solicitação
- visualização de resultados

### API Backend
Responsável por:
- autenticação
- CRUDs principais
- recebimento de requisições
- orquestração dos serviços
- exposição de endpoints

### Camada de domínio / serviços
Responsável por:
- regras de negócio
- classificação de prioridade
- geração de resposta padronizada
- coordenação operacional

### Camada de agentes
Responsável por:
- construção de contexto
- decisão sobre tools
- comunicação com LLM
- orquestração do fluxo do agente

### Camada de tools
Responsável por:
- consultar dados do cliente
- consultar dados de fornecedores
- chamar API externa
- classificar prioridade
- gerar resposta padronizada
- extrair texto OCR

### Camada de integrações
Responsável por:
- comunicação com Ollama
- comunicação com APIs externas
- comunicação com OCR

### Camada de persistência
Responsável por:
- acesso ao banco
- repositórios
- models
- migrations

---

# 9. Estrutura de diretórios sugerida

```text
my_controller_fin_agent/
  .env.example
  alembic.ini
  docker-compose.yml
  Dockerfile
  requirements.txt
  scripts/
    start.sh
  alembic/
    env.py
    script.py.mako
    versions/
      0001_initial_schema.py
  backend/
    __init__.py
    app/
      api/
        v1/
          routes/
            auth.py
            chat.py
            clients.py
            suppliers.py
            contacts.py
            dashboard.py
            pages.py
            requests.py
      core/
        config.py
        logging.py
        security.py
      db/
        base.py
        seed.py
        session.py
      models/
        audit_log.py
        chat.py
        client.py
        supplier.py
        contact.py
        document.py
        mixins.py
        request.py
        user.py
      repositories/
        base.py
        chat_repository.py
        client_repository.py
        supplier_repository.py
        contact_repository.py
        document_repository.py
        request_repository.py
      schemas/
        auth.py
        chat.py
        client.py
        supplier.py
        contact.py
        dashboard.py
        document.py
        request.py
      services/
        auth_service.py
        chat_service.py
        client_service.py
        supplier_service.py
        contact_service.py
        dashboard_service.py
        document_service.py
        ocr_service.py
        ollama_service.py
        request_service.py
      agents/
        prompts.py
      tools/
        record_search.py
        simplified_report.py
      integrations/
      static/
        css/
          app.css
        js/
          app.js
          chat.js
          dashboard.js
          login.js
      templates/
        base.html
        chat.html
        dashboard.html
        login.html
      main.py
    tests/
      conftest.py
      test_health_and_pages.py
  PROJECT_GUIDELINES.md
```

## 9.1 Artefatos mínimos de infraestrutura

O projeto deve prever desde o início:

- `docker-compose.yml` para orquestrar aplicação, PostgreSQL e Ollama
- `Dockerfile` da aplicação com Python, dependências do backend e Tesseract
- `alembic.ini` e pasta `alembic/` para versionamento do banco
- `.env.example` com variáveis de ambiente mínimas
- `scripts/start.sh` para aplicar migrations e subir o FastAPI

## 9.2 Estrutura inicial já alinhada ao MVP

Essa estrutura inicial deve refletir:

- backend em camadas
- rotas REST para autenticação, dashboard, registros e chat
- frontend server-rendered com HTML, JavaScript e Tailwind CSS
- base para JWT, logs estruturados em JSON, OCR e integração com Ollama
- suporte inicial a chat operacional, busca de registros e relatório simplificado

---

# 10. Telas esperadas

## 10.1 Login
- email
- senha
- botão entrar

## 10.2 Dashboard
- cards de métricas
- solicitações recentes
- prioridades
- status das execuções

## 10.3 Clientes
- tabela de clientes
- busca
- status
- botão visualizar

## 10.4 Fornecedores
- tabela de fornecedores
- busca
- status
- botão visualizar

## 10.5 Contatos
- tabela de contatos
- filtro por cliente
- ações básicas

## 10.6 Nova solicitação
- seleção de cliente
- descrição livre
- upload de documento
- botão processar

## 10.7 Documentos
- cadastro de nota fiscal ou recibo
- opção de entrada manual ou via OCR
- formulário com os mesmos campos persistidos em `documents`
- upload de arquivo em qualquer formato suportado quando o modo for OCR
- exibição do texto extraído e dos JSONs estruturados

## 10.8 Detalhe da solicitação
- dados do cliente
- texto enviado
- texto OCR
- tools executadas
- prioridade
- resposta final
- logs resumidos

## 10.9 Chat central
- campo de conversa
- histórico de mensagens
- respostas estruturadas
- sugestões de perguntas
- acesso rápido a clientes, fornecedores, solicitações e relatórios simplificados
- uso do mesmo fluxo conversacional para clientes, fornecedores, contatos, solicitações, documentos e relatórios

---

# 11. Entidades principais do banco de dados

## users
- id
- name
- email
- password_hash
- role
- created_at

## clients
- id
- name
- document_number
- email
- phone
- status
- created_at

## contacts
- id
- client_id
- name
- email
- phone
- position
- created_at

## suppliers
- id
- name
- document_number
- email
- phone
- status
- created_at

## documents
- id
- client_id
- document_type
- entry_mode
- file_name
- file_path
- mime_type
- extracted_text
- json_nfe
- json_rec
- created_at
- updated_at

## requests
- id
- client_id
- user_id
- title
- description
- status
- priority
- standardized_response
- created_at

## agent_runs
- id
- request_id
- input_text
- ocr_text
- selected_tools
- llm_output
- final_output
- execution_time_ms
- status
- created_at

## audit_logs
- id
- request_id
- event_type
- level
- message
- payload_json
- created_at

---

# 12. Responsabilidades do agente

O agente deve ser capaz de:

- entender a solicitação em linguagem natural
- usar contexto de cliente
- usar texto vindo de OCR
- decidir quais tools utilizar
- consolidar os resultados
- classificar prioridade
- gerar saída estruturada
- produzir resposta padronizada

O agente **não deve ser tratado como simples chatbot genérico**.  
Ele deve ter papel de **orquestrador operacional**.

---

# 13. Tools esperadas

A IA deve considerar estas tools como parte central do sistema.

## Tool: consultar dados do cliente
Objetivo:
- buscar informações do cliente no banco
- enriquecer o contexto da solicitação

## Tool: chamar API externa
Objetivo:
- consultar um serviço externo
- complementar dados operacionais

## Tool: classificar prioridade
Objetivo:
- definir prioridade com base em regras e contexto

## Tool: gerar resposta padronizada
Objetivo:
- criar uma resposta consistente para o usuário final

## Tool: extrair texto de documento
Objetivo:
- obter texto a partir de arquivo enviado

## Regra de negócio do módulo de documentos

O módulo de documentos deve permitir o cadastro de **notas fiscais** e **recibos** de duas formas:

- manualmente
- via OCR

### Entrada manual

Quando o usuário escolher cadastro manual, a interface deve exibir os mesmos campos persistidos na tabela `documents`, permitindo preenchimento direto e gravação estruturada.

### Entrada via OCR

Quando o usuário escolher OCR:

- o sistema deve aceitar o upload do documento em formato compatível
- o arquivo deve ser processado com OCR
- o texto extraído deve ser organizado por uma camada de IA
- o resultado estruturado deve ser salvo na tabela `documents`

### Estrutura esperada para `json_nfe`

O campo `json_nfe` deve seguir um padrão estruturado para notas fiscais, por exemplo:

```json
{
  "numero_nota": "",
  "serie": "",
  "chave_acesso": "",
  "data_emissao": "",
  "emitente": {
    "nome": "",
    "cnpj": ""
  },
  "destinatario": {
    "nome": "",
    "cnpj": ""
  },
  "itens": [
    {
      "descricao": "",
      "quantidade": 0,
      "valor_unitario": 0,
      "valor_total": 0
    }
  ],
  "totais": {
    "valor_produtos": 0,
    "valor_total": 0
  }
}
```

### Estrutura esperada para `json_rec`

O campo `json_rec` deve seguir um padrão estruturado para recibos, por exemplo:

```json
{
  "numero_recibo": "",
  "data_emissao": "",
  "recebedor": {
    "nome": "",
    "documento": ""
  },
  "pagador": {
    "nome": "",
    "documento": ""
  },
  "referencia": "",
  "valor": 0,
  "forma_pagamento": "",
  "observacoes": ""
}
```

Esses dois campos devem ser tratados como estrutura padrão de saída normalizada, tanto para entrada manual quanto para documentos processados por OCR.

## Tool: buscar registros
Objetivo:
- localizar clientes, contatos, solicitações e execuções com base em linguagem natural

## Tool: gerar relatório simplificado
Objetivo:
- consolidar dados do sistema em formato resumido e compreensível

---

# 14. Lógica esperada do fluxo do agente

## Entrada
- texto da solicitação
- cliente selecionado
- documento opcional
- mensagem de chat do usuário

## Enriquecimento
- OCR do documento
- dados do cliente
- dados vindos de API externa

## Decisão
- agente identifica quais tools usar
- fallback por regras simples quando necessário

## Execução
- tools são chamadas
- resultados são consolidados

## Saída
- prioridade
- resposta final padronizada
- histórico
- logs
- resposta conversacional estruturad

---

# 15. Regras de prioridade

A classificação pode seguir:
- baixa
- média
- alta
- crítica

A classificação deve considerar:
- urgência implícita no texto
- contexto do cliente
- conteúdo do documento
- retorno de API externa
- regras de negócio simples
- apoio do LLM

Sempre que possível, registrar também:
- justificativa da prioridade
- fatores considerados

---

# 16. Resposta padronizada esperada

A resposta final do sistema deve buscar um formato consistente, contendo:

- resumo do caso
- cliente relacionado
- prioridade
- achados principais
- retorno das consultas realizadas
- próximos passos sugeridos

Exemplo de estrutura:

```json
{
  "summary": "Resumo objetivo da solicitação",
  "priority": "alta",
  "client_context": "Dados relevantes do cliente",
  "external_findings": "Resultado da API externa",
  "document_findings": "Resumo do OCR/documento",
  "recommended_next_steps": [
    "Ação 1",
    "Ação 2"
  ]
}
```

---

# 17. Regras de logs e auditoria

O sistema deve registrar:

- login
- criação de solicitação
- upload de documento
- OCR executado
- tools acionadas
- chamada ao Ollama
- chamada à API externa
- classificação de prioridade
- resposta final gerada
- falhas
- tempo de execução
- status final
- perguntas feitas no chat
- tools acionadas durante a conversa
- relatórios gerados pelo chat

Os logs devem ser:
- claros
- estruturados
- úteis para depuração
- persistidos quando necessário

---

# 18. Diretrizes de desenvolvimento

A IA que auxiliar no projeto deve seguir estas diretrizes:

## 18.1 Preservar a arquitetura
Não misturar responsabilidades sem necessidade.

## 18.2 Evitar acoplamento excessivo
A lógica de IA não deve ficar espalhada por rotas.

## 18.3 Separar domínio de integração
Regras de negócio devem ficar em services ou agents, não dentro de clients HTTP.

## 18.4 Respeitar a stack
Evitar sugerir frameworks muito diferentes sem necessidade.

## 18.5 Priorizar clareza
O projeto deve parecer profissional, mas viável de desenvolver em poucas semanas.

## 18.6 Priorizar backend funcional
A interface pode ser simples, desde que o fluxo principal esteja sólido.

## 18.7 Garantir rastreabilidade
Toda execução relevante deve poder ser entendida depois.

---

# 19. O que deve ser evitado

A IA não deve empurrar o projeto para fora da proposta inicial.

Evitar:
- transformar o sistema em chatbot genérico
- trocar FastAPI por stack muito diferente sem motivo
- adicionar complexidade excessiva antes do MVP
- depender de ferramentas pagas como requisito
- criar frontend complexo demais sem necessidade
- colocar regra de negócio diretamente em controllers/rotas
- acoplar toda a solução a um único provider difícil de trocar
- abandonar logs e observabilidade

---

# 20. Critérios de validação para novas implementações

Sempre que uma nova funcionalidade for proposta, validar:

1. está alinhada com o objetivo da plataforma?
2. respeita a stack definida?
3. melhora o fluxo principal do MVP?
4. preserva a arquitetura em camadas?
5. mantém rastreabilidade e logs?
6. pode ser implementada sem comprometer o prazo?
7. agrega valor para demonstração em portfólio/entrevista?

Se a resposta for majoritariamente "não", a funcionalidade deve ser revista.

---

# 21. Backlog macro do projeto

## 21.1 Planejamento
- definir escopo
- definir arquitetura
- definir fluxo principal
- definir entidades e telas

## 21.2 Setup do projeto
- criar repositório
- estruturar pastas
- configurar dependências
- configurar ambiente
- configurar Docker Compose

## 21.3 Backend base
- subir FastAPI
- configurar banco
- configurar SQLAlchemy
- configurar Alembic
- configurar tratamento de erro

## 21.4 Autenticação
- modelar usuários
- login
- proteção de rotas
- token

## 21.5 Modelagem de dados
- users
- clients
- suppliers
- contacts
- documents
- requests
- agent_runs
- audit_logs

## 21.6 Módulo de clientes
- CRUD/listagem
- busca
- detalhe

## 21.7 Módulo de fornecedores
- CRUD/listagem
- busca
- detalhe

## 21.8 Módulo de contatos
- CRUD/listagem
- filtro por cliente

## 21.9 Frontend
- login
- layout com menu lateral
- dashboard
- clientes
- fornecedores
- contatos
- documentos
- solicitações
- tela de chat

## 21.10 OCR
- upload
- integração com Tesseract
- armazenamento do texto extraído
- organização do conteúdo por IA para notas fiscais e recibos

## 21.11 IA
- integração com Ollama
- prompt builder
- tool registry
- orquestrador
- endpoint de conversa

## 21.12 Tools
- cliente
- API externa
- prioridade
- resposta padronizada
- OCR
- histórico de conversa
- tool de busca de registros
- tool de relatório simplificado

## 21.13 Logs
- logger estruturado
- persistência de logs
- histórico de execução

## 21.14 Testes
- testes unitários
- testes de integração
- testes de rotas principais

## 21.15 Documentação
- README
- setup
- arquitetura
- endpoints
- screenshots

## 21.16 Deploy
- ajustar Docker Compose
- subir na VPS
- validar persistência
- validar logs

---

# 22. Ordem sugerida de implementação

1. estrutura do projeto  
2. Docker e banco  
3. FastAPI e config base  
4. autenticação  
5. models e migrations  
6. clientes  
7. contatos  
8. layout web  
9. dashboard  
10. upload de documento  
11. OCR  
12. integração com Ollama  
13. orquestrador do agente  
14. tools  
15. chat operacional  
16. busca de registros por linguagem natural  
17. relatório simplificado via chat  
18. prioridade  
19. resposta padronizada  
20. logs  
21. testes  
22. README  
23. deploy  

## 22.1 O que precisa existir no projeto para o chat funcionar de verdade

O chat central não deve existir apenas como ideia de interface ou item de backlog.  
Para funcionar de forma real dentro do projeto, a arquitetura precisa prever componentes específicos no backend, banco, frontend e camada de agente.

### Backend
- rota de chat, por exemplo `/chat/message`
- service de conversa
- memória curta de contexto por sessão ou por conversa
- tools de busca no banco
- tool de geração de relatório resumido

### Banco
- tabelas para sessões e histórico de conversa, idealmente como `chat_sessions` e `chat_messages`
- vínculo entre conversa, usuário autenticado e contexto operacional consultado
- persistência de mensagens do usuário, respostas do agente e metadados de execução das tools

### Frontend
- item `Chat` no menu lateral
- tela com histórico
- input de mensagem
- loading da resposta
- renderização de resposta estruturada

### Agente
- prompt específico para modo conversacional
- controle para evitar respostas inventadas
- uso de tools antes de responder
- resposta baseada em dados do sistema

Sem esses elementos, o chat tende a virar apenas uma caixa de texto conectada ao modelo, sem contexto confiável, sem rastreabilidade e sem valor operacional real. Além disso, o projeto deve preservar a ideia de **um único chat central**, e não múltiplos chats independentes para cada módulo.

---

# 23. Evoluções futuras possíveis

Depois do MVP, o projeto pode evoluir para:

- fila assíncrona
- Redis
- Celery ou RQ
- WebSocket para status em tempo real
- RBAC
- múltiplos modelos via Ollama
- dashboards mais completos
- observabilidade com Prometheus/Grafana
- exportação de relatórios
- embeddings e busca semântica
- revisão humana antes de resposta final

Essas evoluções são válidas, mas **não devem comprometer o MVP inicial**.

---

# 24. Como a IA deve usar este documento

Ao sugerir código, arquitetura, ajustes ou novas funcionalidades, a IA deve:

- consultar este documento primeiro
- manter aderência ao MVP
- respeitar a stack oficial
- preservar a arquitetura em camadas
- priorizar clareza, rastreabilidade e entrega realista
- evitar soluções que descaracterizem o projeto

---

# 25. Regra final de alinhamento

Se houver dúvida entre:
- uma solução mais complexa e sofisticada
- uma solução mais simples e aderente ao projeto

A preferência deve ser pela **solução mais simples, funcional, coerente com o MVP e apresentável em portfólio**.

---

# 26. Resumo executivo final

Este projeto deve demonstrar capacidade prática em:

- Python aplicado a backend
- FastAPI
- integrações REST
- OCR com Tesseract
- uso de LLM local com Ollama
- automação operacional
- arquitetura organizada
- persistência com PostgreSQL
- logs e observabilidade
- entrega de solução com cara de produto real

O foco não é apenas “usar IA”, mas sim **construir uma solução corporativa de automação com IA, integrável, rastreável e pronta para evolução**.
