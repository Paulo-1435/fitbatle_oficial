const HOST_API = window.location.hostname || 'localhost';
const PORTAS_FRONTEND_DEV = new Set(['5500', '5501']);
const API_URL = window.FITBATTLE_API_URL
  ? window.FITBATTLE_API_URL
  : (PORTAS_FRONTEND_DEV.has(window.location.port)
    ? 'http://' + HOST_API + ':5000/api'
    : window.location.origin + '/api');
const ORIGEM_API = API_URL.replace(/\/api\/?$/, '');
const CHAVE_SESSAO = 'fitbattle_sessao';
const CHAVE_SESSAO_ANTIGA = 'fitbattle_usuario';
const PAGINA_LOGIN = 'login.html';
const PAGINA_INICIAL = 'feed.html';

function armazenamentosDisponiveis() {
  const lista = [];
  try { if (typeof sessionStorage !== 'undefined') lista.push(sessionStorage); } catch (e) {}
  try { if (typeof localStorage !== 'undefined') lista.push(localStorage); } catch (e) {}
  return lista;
}

function armazenamentoDaSessao() {
  const lista = armazenamentosDisponiveis();
  for (let i = 0; i < lista.length; i++) {
    try {
      if (lista[i].getItem(CHAVE_SESSAO)) return lista[i];
    } catch (e) {}
  }
  return null;
}

function lerSessao() {
  const armazenamento = armazenamentoDaSessao();
  if (!armazenamento) return null;
  try {
    const sessao = JSON.parse(armazenamento.getItem(CHAVE_SESSAO));
    return sessao && sessao.token && sessao.usuario ? sessao : null;
  } catch (e) {
    return null;
  }
}

function salvarSessao(token, usuario, lembrar) {
  const persistente = lembrar !== false;
  const destino = persistente ? localStorage : (typeof sessionStorage !== 'undefined' ? sessionStorage : localStorage);
  limparSessao();
  try {
    destino.setItem(CHAVE_SESSAO, JSON.stringify({ token: token, usuario: usuario }));
  } catch (e) {}
}

function atualizarUsuarioDaSessao(usuario) {
  const armazenamento = armazenamentoDaSessao();
  const sessao = lerSessao();
  if (!armazenamento || !sessao) return;
  try {
    armazenamento.setItem(CHAVE_SESSAO, JSON.stringify({ token: sessao.token, usuario: usuario }));
  } catch (e) {}
}

function limparSessao() {
  armazenamentosDisponiveis().forEach(function (armazenamento) {
    try {
      armazenamento.removeItem(CHAVE_SESSAO);
      armazenamento.removeItem(CHAVE_SESSAO_ANTIGA);
    } catch (e) {}
  });
}

function usuarioDaSessao() {
  const sessao = lerSessao();
  return sessao ? sessao.usuario : null;
}

function exigirLogin() {
  const usuario = usuarioDaSessao();
  if (!usuario) {
    window.location.href = PAGINA_LOGIN;
    return null;
  }
  return usuario;
}

function encerrarSessao() {
  limparSessao();
  window.location.href = PAGINA_LOGIN;
}

const MENSAGEM_SEM_CONEXAO = 'Não foi possível falar com o servidor. Tente novamente.';

class ErroDeConexao extends Error {
  constructor() {
    super(MENSAGEM_SEM_CONEXAO);
    this.name = 'ErroDeConexao';
  }
}

async function api(caminho, opcoes) {
  const config = Object.assign({}, opcoes);
  const cabecalhos = Object.assign({}, config.headers);
  const sessao = lerSessao();
  if (sessao) cabecalhos['Authorization'] = 'Bearer ' + sessao.token;
  config.headers = cabecalhos;

  let resposta;
  try {
    resposta = await fetch(API_URL + caminho, config);
  } catch (erro) {
    throw new ErroDeConexao();
  }
  if (resposta.status === 401) encerrarSessao();
  if (resposta.status >= 500) throw new ErroDeConexao();
  return resposta;
}

function mostrarFalhaDeCarregamento(aoTentarDeNovo) {
  document.querySelectorAll('body *').forEach(function (elemento) {
    if (elemento.childElementCount === 0 && /^carregando/i.test(elemento.textContent.trim())) {
      elemento.textContent = /^(H[1-6]|SPAN)$/.test(elemento.tagName) ? 'Indisponível no momento' : MENSAGEM_SEM_CONEXAO;
    }
  });
  let bloco = document.getElementById('falhaDeCarregamento');
  if (bloco) bloco.remove();
  bloco = document.createElement('div');
  bloco.id = 'falhaDeCarregamento';
  bloco.className = 'card card--interno estado-falha';
  bloco.setAttribute('role', 'alert');
  const texto = document.createElement('p');
  texto.textContent = MENSAGEM_SEM_CONEXAO;
  const botao = document.createElement('button');
  botao.type = 'button';
  botao.className = 'btn btn--secundario btn--pequeno';
  botao.textContent = 'Tentar de novo';
  botao.addEventListener('click', function () {
    bloco.remove();
    aoTentarDeNovo();
  });
  bloco.append(texto, botao);
  const principal = document.querySelector('main') || document.body;
  principal.insertBefore(bloco, principal.firstChild);
}

async function atualizarSessaoPelaApi() {
  const resposta = await api('/eu');
  if (!resposta.ok) return null;
  const dados = await resposta.json();
  atualizarUsuarioDaSessao(dados.usuario);
  return dados.usuario;
}

const ESCAPES_HTML = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, function (caractere) {
    return ESCAPES_HTML[caractere];
  });
}
