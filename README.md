# Fit-Battle

Bernardo Nardelli, Cauã Gomes, João Paulo Costa, João Pedro Braga, Miguel Assunção, Henrique Vale.

Plataforma gamificada de treinos. Este repositório contém a API (Flask) e o
frontend web.

## Status do desenvolvimento (RF01 a RF20)

Levantamento conferido contra o código atual (rotas registradas e serviços
que as implementam), não só contra as tabelas do SQL — uma tabela existir no
schema não significa que a funcionalidade esteja implementada.

| RF | Descrição | Status |
|---|---|---|
| RF01 | Cadastro (nome, idade, e-mail, senha) | Implementado |
| RF02 | Login e autenticação | Implementado, com token assinado |
| RF03 | Perfil (visualizar/editar, foto, nível, bio) | Implementado |
| RF04 | Registrar atividade (tipo, tempo, distância, carga/repetições) | Implementado |
| RF05 | Histórico completo de atividades | Implementado |
| RF06 | Criar grupos privados de competição | Implementado |
| RF07 | Convidar via link/código ou busca direta | Implementado |
| RF08 | Aceitar/recusar convites | Implementado |
| RF09 | Ranking interno do grupo | Implementado |
| RF10 | Ranking regional (cidade/região) | Implementado |
| RF11 | Ranking global | Implementado |
| RF12 | Cálculo automático de pontuação por atividade | Implementado |
| RF13 | Atribuição automática de nível/categoria por XP | Implementado, cinco categorias |
| RF14 | Dashboard de estatísticas com gráficos detalhados | Não implementado — `/api/estatisticas` só devolve total de usuários e média de XP, sem gráfico e sem detalhe por usuário |
| RF15 | Criar/gerenciar metas pessoais (curto/longo prazo) | Implementado |
| RF16 | Participar de desafios sazonais | Não implementado — `frontend/desafio.html` é só uma prévia visual com dados de exemplo fixos, sem chamada nenhuma à API |
| RF17 | Acompanhar status de metas/desafios ativos | Parcial — metas sim (`GET /api/metas`, `GET /api/metas/<id>`); desafios não, porque o RF16 não existe |
| RF18 | Notificações push ou e-mail | Não implementado — a tabela `notificacao` existe no SQL, mas não há rota nem serviço de envio |
| RF19 | Busca de perfis ou grupos | Parcial — busca de perfis implementada e restrita a campos públicos; não existe busca de grupos (entra-se em um grupo só por código/link de convite, RF07) |
| RF20 | Compartilhar conquistas/recordes em redes sociais | Parcial — só copia um texto pronto para a área de transferência; a tabela `compartilhamento` do SQL não é usada, e não existe conceito de medalha no sistema |

## Estrutura

```
.
├── README.md
├── .gitignore
├── backend/
│   ├── app.py                  # cria e sobe a aplicação Flask
│   ├── auth.py                 # token (itsdangerous), decorator protegido()
│   ├── database.py             # instância do SQLAlchemy (objeto db)
│   ├── gunicorn.conf.py        # workers = 1 (ver seção "gunicorn" abaixo)
│   ├── requirements.txt
│   ├── database/
│   │   ├── create_database.sql    # schema completo, para instalação nova
│   │   └── migracao_meta.sql      # atualiza um banco existente (ver "Atualizando o banco")
│   ├── routers/
│   │   └── routers.py          # mapeia as URLs para os Controllers
│   ├── controllers/
│   │   └── controller.py       # Usuario/Atividade/Postagem/Feed/Curtida/Comentario/
│   │                            # Ranking/Consentimento/Grupo/Convite/MetaController
│   ├── services/                # regra de negócio, um módulo por domínio
│   │   ├── comum.py             # ErroValidacao, upload/validação de imagem
│   │   ├── usuario.py           # UsuarioService, limitador de tentativas de login
│   │   ├── privacidade.py       # ConsentimentoService (LGPD)
│   │   ├── atividade.py         # AtividadeService, cálculo de XP/nível
│   │   ├── feed.py              # PostagemService, FeedService, Curtida/Comentario
│   │   ├── ranking.py           # RankingService
│   │   ├── grupo.py             # GrupoService, ConviteService
│   │   └── meta.py              # MetaService
│   ├── repositories/
│   │   └── repository.py       # único ponto de acesso ao banco
│   ├── models/
│   │   └── model.py            # todas as tabelas (SQLAlchemy)
│   └── tests/
│       ├── apoio.py             # recria as views de ranking em SQLite para os testes
│       ├── servidor_dev.py      # API com SQLite populado de dados de exemplo
│       ├── test_seguranca.py
│       ├── test_robustez.py
│       ├── test_grupos.py
│       ├── test_metas.py
│       └── test_ranking.py
└── frontend/
    ├── login.html / login.js, index.html / script.js   # login e cadastro
    ├── perfil.html / perfil.js                          # perfil, treinos, foto
    ├── feed.html / feed.js                               # feed social
    ├── grupo*.html / grupo*.js, entrar-grupo.*           # grupos e convites
    ├── metas*.html / metas*.js                           # metas pessoais
    ├── ranking.html / ranking.js                         # rankings
    ├── privacidade.html / privacidade.js                 # consentimentos LGPD
    ├── desafio.html / desafio.js                         # prévia visual, sem API (RF16)
    ├── mockups/                                          # telas de outro integrante do grupo,
    │                                                      # não referenciadas pelo app (perfil-A/B/C.html)
    └── api.js, shell.js, auth-comum.js, tokens.css, ...  # compartilhados entre as páginas
```

Fluxo de uma requisição: **routers → controller → service → repository → model → MySQL**.

## Como rodar

### 1. Banco de dados (MySQL 8+) — instalação nova

Rode o script `backend/database/create_database.sql` inteiro:

```bash
mysql -u root -p < backend/database/create_database.sql
```

Ou pelo MySQL Workbench: *File > Open SQL Script* > selecione o arquivo >
botão do raio (Execute All).

O script cria o banco `fitbattle`, todas as tabelas e views, e o usuário de
aplicação `fitbattle` / senha `Fitbattle@123` (usado pela API, não pelo
root). Essa senha é só um exemplo para desenvolvimento local; troque-a (e
configure `DB_PASSWORD` com o novo valor) em qualquer ambiente compartilhado
ou de produção.

Se você já tem um banco `fitbattle` de antes da feature de Metas (RF15) e
quer **manter os dados**, não rode `create_database.sql` de novo — veja
"Atualizando o banco" abaixo.

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

A API sobe em `http://localhost:5000`. Deixe esse terminal aberto enquanto
usa o sistema — se fechar (ou o PC reiniciar), rode `python app.py` de novo.

> O pacote `cryptography` está no `requirements.txt` porque o MySQL 8 usa o
> método de autenticação `caching_sha2_password`, e o PyMySQL precisa dele
> para conectar.

Variáveis de ambiente aceitas (todas opcionais, já vêm com padrão):
`DB_USER` (fitbattle), `DB_PASSWORD` (Fitbattle@123), `DB_HOST` (localhost),
`DB_PORT` (3306), `DB_NAME` (fitbattle), `DB_URI` (sobrescreve as cinco
anteriores, usado pelos testes com SQLite), `SECRET_KEY`, `FLASK_DEBUG`
(desligado por padrão; defina como `1` só em desenvolvimento),
`CORS_EXTRA_ORIGENS` (origens extras separadas por vírgula, além de
localhost/127.0.0.1/IPs de rede local, já liberados por padrão).

### 3. Frontend

A própria API já serve o frontend: com o backend rodando, abra
`http://localhost:5000/` no navegador (ela serve os arquivos da pasta
`frontend/`, que precisa continuar como pasta irmã de `backend/`). Também é
possível abrir `frontend/login.html` direto no navegador ou com Live Server;
nesse caso o `frontend/api.js` detecta a porta de desenvolvimento e aponta
para `http://localhost:5000/api` sozinho.

### 4. Rodar com dados de exemplo (sem MySQL)

```bash
cd backend
python tests/servidor_dev.py
```

Sobe a API num banco SQLite local (`backend/dev.db`), já populado com ~12
usuários e treinos de teste, sem precisar de MySQL. Útil para demonstração
rápida ou para olhar o frontend sem configurar banco nenhum.

### 5. Suíte de testes

```bash
cd backend
python -m unittest discover -s tests -t .
```

111 testes atualmente, cobrindo autenticação/LGPD, robustez (uploads, limite
de login, concorrência), grupos/convites, metas e rankings.

## Atualizando o banco

Duas situações bem diferentes — escolha a certa antes de rodar qualquer
coisa:

**Você tem um banco `fitbattle` de antes da feature de Metas e quer manter
os dados** (usuários, treinos, etc.) → rode a migração:

```bash
mysql -u root -p fitbattle < backend/database/migracao_meta.sql
```

Ela faz só um `ALTER TABLE meta` (adiciona as colunas novas, remove a antiga
`progresso`) e preserva todas as linhas existentes. **Rode esse script uma
única vez** — MySQL não aceita `ADD COLUMN`/`DROP COLUMN IF [NOT] EXISTS`,
então rodar de novo falha na linha do `DROP COLUMN` (coluna já removida).

Qualquer meta criada antes da migração fica com `tipo_metrica` e
`valor_objetivo` nulos — não dá para inventar esses valores a partir do
dado antigo (`progresso` era só um número de 0 a 100, sem o objetivo real
por trás). A API não quebra por isso: `GET /api/metas` e
`GET /api/metas/<id>` devolvem essas metas com `tipo_metrica`,
`valor_objetivo`, `valor_atual` e `percentual` como `null` em vez de erro
500, mas o progresso delas simplesmente não é calculável — é uma limitação
conhecida, não um bug pendente.

**Você está num ambiente de desenvolvimento e topa perder todos os dados**
→ `DROP DATABASE fitbattle;` e rode `create_database.sql` de novo do zero.

> ⚠️ **Isso apaga todos os usuários, treinos, grupos, metas e tudo o mais,
> sem volta.** Nunca rode isso contra um banco com dados reais.

## Notas importantes

**Desafio 1x1 (`frontend/desafio.html`) é só uma prévia visual.** O próprio
HTML avisa isso ("dados de exemplo fixos do design"); o `desafio.js` não faz
nenhuma chamada à API. Corresponde ao RF16/RF17, que ainda não existem de
verdade no backend.

**A API precisa rodar com exatamente 1 worker do gunicorn em produção.** O
limitador de tentativas de login (`_LimitadorLogin`, em
`backend/services/usuario.py`) guarda o contador em memória, por processo —
com mais de um worker, cada processo teria seu próprio contador e o limite
deixaria de funcionar de verdade. `backend/gunicorn.conf.py` já fixa
`workers = 1` (usando `threads = 4` / `worker_class = "gthread"` para
concorrência sem múltiplos processos) e é carregado automaticamente pelo
gunicorn quando o comando de start roda a partir da pasta `backend/`. Nunca
suba a API com `-w`/`--workers` maior que 1.

As senhas são armazenadas com hash (`werkzeug.security`), nunca em texto
puro.

## Endpoints da API

| Método | Rota | Descrição | Acesso | RF |
|---|---|---|---|---|
| POST | `/api/usuarios` | Cadastra usuário (`aceite_termos`, `consentimentos`) | Público | RF01 |
| POST | `/api/login` | Autentica (email, senha); bloqueia após tentativas demais | Público | RF02 |
| GET | `/api/estatisticas` | Total de usuários e média de XP | Público | RF14 (parcial) |
| GET | `/api/eu` | Dados completos do próprio usuário logado | Logado | RF03 |
| GET | `/api/usuarios/busca?nome=` | Busca restrita por nome (só campos públicos) | Logado | RF19 |
| GET | `/api/usuarios/<id>` | Perfil (próprio: completo; de outro: público) | Logado | RF03, RF19 |
| PUT | `/api/usuarios/<id>` | Atualiza o perfil | Dono | RF03 |
| DELETE | `/api/usuarios/<id>` | Exclui a conta (e as fotos associadas) | Dono | — |
| POST | `/api/usuarios/<id>/foto` | Envia a foto de perfil (multipart, campo `foto`) | Dono | RF03 |
| POST | `/api/usuarios/<id>/atividades` | Registra um treino; calcula pontuação e XP/nível | Dono | RF04, RF12, RF13 |
| GET | `/api/usuarios/<id>/atividades` | Histórico de treinos | Dono | RF05 |
| GET | `/api/atividades/<id>` | Detalhe de um treino | Logado | RF05 |
| DELETE | `/api/atividades/<id>` | Exclui o treino (desconta a pontuação) | Logado | — |
| POST / DELETE | `/api/postagens[/<id>]` | Criar/excluir postagem no feed | Logado | — |
| GET | `/api/feed` | Feed combinado (treinos + postagens) | Logado | — |
| POST | `/api/feed/<tipo>/<id>/curtir` | Curtir/descurtir treino ou postagem | Logado | — |
| GET / POST | `/api/feed/<tipo>/<id>/comentarios` | Listar/criar comentário | Logado | — |
| DELETE | `/api/comentarios/<id>` | Excluir comentário | Logado | — |
| GET | `/api/ranking/global` | Ranking de todos por XP | Logado | RF11 |
| GET | `/api/ranking/regional?cidade=` | Ranking por cidade | Logado | RF10 |
| GET | `/api/ranking/exercicio?titulo=` | Ranking por carga num exercício específico | Logado | — |
| GET | `/api/usuarios/<id>/ranking` | Posição do usuário nos rankings global/regional | Dono | RF10, RF11 |
| GET | `/api/usuarios/<id>/consentimentos` | Lista os consentimentos LGPD | Dono | — |
| PUT | `/api/usuarios/<id>/consentimentos/<chave>` | Revoga/reativa um consentimento opcional | Dono | — |
| POST / GET | `/api/grupos` | Criar grupo / listar meus grupos | Logado | RF06 |
| POST | `/api/grupos/entrar` | Entrar num grupo via código de convite | Logado | RF07 |
| GET | `/api/grupos/<id>` | Detalhe do grupo | Logado | RF06 |
| GET | `/api/grupos/<id>/membros` | Lista de membros | Logado | RF06 |
| GET | `/api/grupos/<id>/ranking` | Ranking interno do grupo | Logado | RF09 |
| GET | `/api/grupos/<id>/convite` | Info do link/código de convite | Logado | RF07 |
| POST | `/api/grupos/<id>/convite/regenerar` | Gera um novo código de convite | Logado | RF07 |
| GET | `/api/grupos/<id>/busca-convidar?nome=` | Busca usuários para convidar | Logado | RF07 |
| POST | `/api/grupos/<id>/convites` | Envia convite direto a um usuário | Logado | RF07 |
| GET | `/api/convites` | Convites pendentes recebidos | Logado | RF08 |
| PUT | `/api/convites/<id>` | Aceita ou recusa um convite | Logado | RF08 |
| POST / GET | `/api/metas` | Criar meta / listar minhas metas | Logado | RF15, RF17 |
| GET | `/api/metas/<id>` | Detalhe da meta, com histórico de progresso | Logado | RF15, RF17 |
| PUT | `/api/metas/<id>` | Edita título, valor objetivo ou data final | Logado | RF15 |
| DELETE | `/api/metas/<id>` | Exclui a meta | Logado | RF15 |
| GET | `/uploads/<nome>` | Serve a foto de perfil/postagem salva | Público | RF03 (apoio) |
| GET | `/healthz` | Health check (status do serviço) | Público | — |

"Dono" exige o token do próprio `<id>` da URL; "Logado" aceita qualquer
usuário autenticado.

### Cálculo de pontuação (RF12) e nível (RF13)

A cada treino registrado, a pontuação é calculada automaticamente a partir
de tempo, distância, carga e repetições, mais um bônus por tipo de
exercício. Essa pontuação é somada ao `xp` do usuário e o `nivel` é
reatribuído pelas faixas em `FAIXAS_NIVEL`
(`backend/services/atividade.py`): iniciante → intermediario → avancado →
profissional → elite.

### Consentimento LGPD

No cadastro, o frontend mostra uma caixa com as finalidades de tratamento já
marcadas. As **obrigatórias** (conta, registro de treinos, histórico, dados
que podem revelar saúde — art. 11 da LGPD, segurança/auditoria) ficam
travadas; as **opcionais** (ranking público, localização, chats, busca,
notificações, compartilhamento) podem ser desmarcadas. O
`ConsentimentoService` grava uma linha por finalidade na tabela
`consentimento`. Recusar `ranking_publico` já define
`usuario.perfil_publico = 0`. O usuário pode revogar/reativar qualquer
opção depois via `PUT /api/usuarios/<id>/consentimentos/<chave>`. O texto
completo dos dois termos está em `frontend/termos.html`.

### Faixa etária (art. 14 da LGPD)

`UsuarioService._validar_faixa_etaria` aplica no cadastro:

- **< 13 anos:** cadastro recusado (400).
- **13 a 17 anos:** obrigatório `responsavel` (`nome`, `email`) e
  `autorizacao_responsavel = true`. Os dados ficam em
  `usuario.responsavel_nome` / `responsavel_email` / `responsavel_autorizado_em`.
- **>= 18 anos:** fluxo normal.

Por decisão do projeto, menores de 18 **participam** dos rankings e da busca
(a autorização do responsável, dada no cadastro, cobre isso).

### Foto de perfil e de postagem (upload de arquivo)

Imagens (PNG, JPG ou WEBP, até 3 MB) são enviadas em `multipart/form-data`.
`services/comum.py` valida a extensão e salva com um nome único
(`usuario_<id>_<timestamp>.<ext>` ou `postagem_<id>_<timestamp>.<ext>`); o
upload de foto de perfil apaga a foto anterior do usuário, o de postagem
não. Os arquivos são servidos pela rota `GET /uploads/<nome>` e ficam em
`backend/uploads/`, que está no `.gitignore` (não versionar fotos).
