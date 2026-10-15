# Fit-Battle

Bernardo Nardelli, Cauã Gomes, João Paulo Costa, João Pedro Braga, Miguel Assunção, Henrique Vale.

Plataforma gamificada de treinos. Este repositório contém a API (Flask) e o
frontend web.

## Casos de uso implementados

Levantamento conferido contra o código atual (rotas registradas e serviços
que as implementam), não só contra as tabelas do SQL — uma tabela existir no
schema não significa que a funcionalidade esteja implementada.

- RF01 — Cadastro (nome, data de nascimento, e-mail, senha)
- RF02 — Login e autenticação, com token assinado
- RF03 — Perfil (visualizar/editar, foto, nível, bio)
- RF04 — Registrar atividade (tipo, tempo, distância, carga/repetições)
- RF05 — Histórico completo de atividades
- RF06 — Criar grupos privados de competição
- RF07 — Convidar via link/código ou busca direta
- RF08 — Aceitar/recusar convites
- RF09 — Ranking interno do grupo
- RF10 — Ranking regional (cidade/região)
- RF11 — Ranking global
- RF12 — Cálculo automático de pontuação por atividade
- RF13 — Atribuição automática de nível/categoria por XP (cinco categorias)
- RF15 — Criar/gerenciar metas pessoais (curto/longo prazo)
- RF17 — Acompanhar status de metas ativas (só metas; a parte de desafios está em "Em breve")
- RF19 — Busca de perfis, restrita a campos públicos (busca de grupos está em "Em breve")
- RF20 — Compartilhar treino copiando um texto pronto para a área de transferência (postar de verdade em redes sociais está em "Em breve")

### Em breve

- RF14 — Dashboard de estatísticas com gráficos detalhados (`/api/estatisticas` só devolve total de usuários e média de XP)
- RF16 — Participar de desafios sazonais (`frontend/desafio.html` é só uma prévia visual, sem chamada à API)
- RF17 (desafios) — Acompanhar status de desafios ativos, depende do RF16
- RF18 — Notificações push ou e-mail (a tabela `notificacao` existe no SQL, sem rota nem serviço de envio)
- RF19 (grupos) — Busca de grupos (hoje só se entra por código/link de convite, RF07)
- RF20 (redes sociais) — Postar de verdade em redes sociais (a tabela `compartilhamento` do SQL não é usada)

## Arquitetura em camadas

Fluxo de uma requisição: **routers → controller → service → repository → model → MySQL**.
Cada seta só anda num sentido: `controllers/` importa só `services/` (e utilitários
como `auth.py`); `services/` nunca importa `database` nem `models` diretamente, só
`repositories/` e `utils.py`; só `repositories/` toca `database`/`models`. Essa regra
é verificada por `backend/tests/test_arquitetura.py`, que analisa os imports de cada
arquivo (não só roda os testes — lê o código-fonte) e falha se alguma camada importar
o que não devia.

| Caso de uso | Controller | Service | Repository |
|---|---|---|---|
| Cadastro | `UsuarioController.cadastrar` | `UsuarioService.cadastrar` | `UsuarioRepository.criar` |
| Login | `UsuarioController.login` | `UsuarioService.autenticar` | `UsuarioRepository.buscar_por_email` |
| Registrar treino | `AtividadeController.registrar` | `AtividadeService.registrar` | `AtividadeRepository.criar` |
| Ranking global | `RankingController.ranking_global` | `RankingService.global_` | `RankingRepository.global_` |
| Ranking regional | `RankingController.ranking_regional` | `RankingService.regional` | `RankingRepository.regional` |
| Ranking por exercício | `RankingController.ranking_por_exercicio` | `RankingService.por_exercicio` | `RankingRepository.por_exercicio` |
| Grupos | `GrupoController.criar` | `GrupoService.criar` | `GrupoRepository.criar` |
| Convites | `ConviteController.responder` | `ConviteService.responder` | `ConviteRepository.buscar_por_id` |
| Metas | `MetaController.criar` | `MetaService.criar` | `MetaRepository.criar` |
| Feed (listagem) | `FeedController.listar` | `FeedService.listar` | `AtividadeRepository.listar_publicas` + `PostagemRepository.listar_publicas` |
| Postagem | `PostagemController.criar` | `PostagemService.criar` | `PostagemRepository.criar` |
| Curtida | `CurtidaController.alternar` | `CurtidaService.alternar` | `CurtidaRepository.curtir` |
| Comentário | `ComentarioController.criar` | `ComentarioService.criar` | `ComentarioRepository.criar` |
| Consentimentos | `ConsentimentoController.atualizar` | `ConsentimentoService.atualizar` | `ConsentimentoRepository.buscar` |

## Estrutura

```
.
├── README.md
├── .gitignore
├── backend/
│   ├── app.py                  # cria e sobe a aplicação Flask
│   ├── auth.py                 # token (itsdangerous), decorator protegido()
│   ├── database.py             # instância do SQLAlchemy (objeto db)
│   ├── utils.py                # agora(), iso_utc(), calcular_idade() — usados por models e services
│   ├── gunicorn.conf.py        # workers = 1 (ver seção "gunicorn" abaixo)
│   ├── requirements.txt
│   ├── database/
│   │   ├── create_database.sql           # schema completo, para instalação nova
│   │   ├── migracao_meta.sql             # atualiza um banco existente (ver "Atualizando o banco")
│   │   └── migracao_data_nascimento.sql  # idem, para a coluna data_nascimento
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
│   │   ├── postagem.py          # PostagemService
│   │   ├── feed.py              # FeedService
│   │   ├── curtida.py           # CurtidaService
│   │   ├── comentario.py        # ComentarioService
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
│       ├── test_arquitetura.py  # análise estática das regras de camada acima
│       ├── test_seguranca.py
│       ├── test_robustez.py
│       ├── test_grupos.py
│       ├── test_metas.py
│       └── test_ranking.py
└── frontend/
    ├── config.js                                         # window.FITBATTLE_API_URL (ver "Como rodar")
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

Se você já tem um banco `fitbattle` de antes da feature de Metas (RF15) ou
de antes da coluna `data_nascimento` e quer **manter os dados**, não rode
`create_database.sql` de novo — veja "Atualizando o banco" abaixo.

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

### 3. Rodar com dados de exemplo (sem MySQL)

```bash
cd backend
python tests/servidor_dev.py
```

Sobe a API num banco SQLite local (`backend/dev.db`), já populado com ~12
usuários e treinos de teste, sem precisar de MySQL. Útil para demonstração
rápida ou para olhar o frontend sem configurar banco nenhum.

### 4. Suíte de testes

```bash
cd backend
python -m unittest discover -s tests -t .
```

123 testes atualmente, cobrindo autenticação/LGPD (incluindo as fronteiras de
13 e 18 anos), robustez (uploads, limite de login, concorrência),
grupos/convites, metas, rankings e a análise estática das camadas.

## Como rodar em 2 servidores

API e frontend são dois servidores separados por padrão. Com a API já rodando
na porta 5000 (passo 2 de "Como rodar"), sirva a pasta `frontend/` com
qualquer servidor de arquivos estático:

```bash
cd frontend
python -m http.server 5500
```

(ou a extensão Live Server do VS Code, na mesma porta 5500 ou 5501). Abra
`http://localhost:5500/login.html` — o `frontend/api.js` detecta a porta de
desenvolvimento e aponta sozinho para `http://localhost:5000/api`.

### Hospedando os dois juntos em um único serviço (opcional)

Para hospedagem simplificada (ex.: um link único para demonstração), a própria
API pode servir os arquivos do frontend. Defina `SERVIR_FRONTEND=1` no
ambiente antes de subir a API: `http://localhost:5000/` passa a servir
`frontend/login.html` e o resto da pasta `frontend/` (que precisa continuar
como pasta irmã de `backend/`). **Sem essa variável (padrão), a API só
responde `/api`, `/uploads` e `/healthz`** — a separação cliente-servidor fica
explícita mesmo quando os dois rodam na mesma máquina. A alternativa a
`SERVIR_FRONTEND=1` é sempre publicar frontend e API como dois serviços de
verdade (por exemplo, frontend num host de arquivos estáticos e a API no
Render) — veja o próximo item.

### Frontend publicado num domínio diferente da API

Edite `frontend/config.js` e defina `window.FITBATTLE_API_URL` com a URL
completa da API (ex.: `'https://minha-api.onrender.com/api'`). Deixado em
branco (padrão de fábrica), o `api.js` usa a detecção automática de porta
acima. Esse arquivo é carregado antes de `api.js` em toda página que faz
chamadas à API.

## Atualizando o banco

Duas situações bem diferentes — escolha a certa antes de rodar qualquer
coisa:

**Você tem um banco `fitbattle` de antes da feature de Metas e/ou da troca de
idade por data de nascimento, e quer manter os dados** (usuários, treinos,
etc.) → rode as migrações que se aplicarem:

```bash
mysql -u root -p fitbattle < backend/database/migracao_meta.sql
mysql -u root -p fitbattle < backend/database/migracao_data_nascimento.sql
```

Cada uma faz só um `ALTER TABLE` (a de metas adiciona as colunas novas e
remove a antiga `progresso`; a de data de nascimento só adiciona a coluna
`data_nascimento`) e preserva todas as linhas existentes. **Rode cada script
uma única vez** — MySQL não aceita `ADD COLUMN`/`DROP COLUMN IF [NOT]
EXISTS`, então rodar de novo falha (coluna já existe/já removida).

Qualquer meta criada antes da migração de metas fica com `tipo_metrica` e
`valor_objetivo` nulos — não dá para inventar esses valores a partir do
dado antigo (`progresso` era só um número de 0 a 100, sem o objetivo real
por trás). A API não quebra por isso: `GET /api/metas` e
`GET /api/metas/<id>` devolvem essas metas com `tipo_metrica`,
`valor_objetivo`, `valor_atual` e `percentual` como `null` em vez de erro
500, mas o progresso delas simplesmente não é calculável — é uma limitação
conhecida, não um bug pendente. Da mesma forma, uma conta criada antes da
migração de data de nascimento fica com `data_nascimento` nulo e continua
usando a antiga coluna `idade` como base para o cálculo de idade
(`utils.calcular_idade`).

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
| PUT | `/api/usuarios/<id>` | Atualiza o perfil; se incluir `data_nascimento`, reaplica as mesmas regras de idade do cadastro | Dono | RF03 |
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

O cadastro recebe `data_nascimento` (`AAAA-MM-DD`), não mais uma idade
digitada — a idade é sempre calculada na hora (`utils.calcular_idade`) a
partir dela, nunca gravada para contas novas. `UsuarioService._validar_faixa_etaria`
aplica, a partir dessa idade calculada:

- **< 13 anos:** cadastro (ou edição) recusado (400).
- **13 a 17 anos:** obrigatório `responsavel` (`nome`, `email`) e
  `autorizacao_responsavel = true`. Os dados ficam em
  `usuario.responsavel_nome` / `responsavel_email` / `responsavel_autorizado_em`.
- **>= 18 anos:** fluxo normal.

Essa mesma validação roda de novo em `PUT /api/usuarios/<id>` sempre que o
corpo inclui `data_nascimento` — editar a data de nascimento no perfil
passa pelas mesmas regras, incluindo exigir o responsável se a nova data
cair em 13-17 anos. Contas criadas antes dessa coluna existir (`data_nascimento`
nulo) continuam usando a antiga coluna `idade` como base do cálculo.

Por decisão do projeto, menores de 18 **participam** dos rankings e da busca
(a autorização do responsável, dada no cadastro, cobre isso).

### Foto de perfil e de postagem (upload de arquivo)

Imagens (PNG, JPG ou WEBP, até 3 MB) são enviadas em `multipart/form-data`.
`services/comum.py` valida a extensão e salva com um nome único
(`usuario_<id>_<timestamp>.<ext>` ou `postagem_<id>_<timestamp>.<ext>`); o
upload de foto de perfil apaga a foto anterior do usuário, o de postagem
não. Os arquivos são servidos pela rota `GET /uploads/<nome>` e ficam em
`backend/uploads/`, que está no `.gitignore` (não versionar fotos).
