from datetime import timedelta

from repositories.repository import AtividadeRepository
from services.usuario import UsuarioService
from utils import agora

SEMANAS_JANELA = 8


class DashboardService:

    @staticmethod
    def resumo(id_usuario, exercicio=None):
        usuario = UsuarioService.buscar(id_usuario)
        hoje = agora().date()

        semanas = DashboardService._semanas(hoje)
        inicio_janela = semanas[0]

        pontos_por_dia = dict(AtividadeRepository.pontuacao_por_dia(id_usuario, inicio_janela))
        treinos_por_dia = dict(AtividadeRepository.contagem_por_dia(id_usuario, inicio_janela))

        xp_por_semana = [
            {"inicio": semana.isoformat(), "xp": DashboardService._soma_semana(pontos_por_dia, semana)}
            for semana in semanas
        ]
        treinos_por_semana = [
            {"inicio": semana.isoformat(), "quantidade": DashboardService._soma_semana(treinos_por_dia, semana)}
            for semana in semanas
        ]

        distribuicao_por_tipo = AtividadeRepository.distribuicao_por_tipo(id_usuario)

        dias = AtividadeRepository.dias_com_treino(id_usuario)
        sequencia_atual, melhor_sequencia = DashboardService._sequencias(dias, hoje)

        total_treinos, total_tempo = AtividadeRepository.totais(id_usuario)

        exercicios = AtividadeRepository.titulos_distintos(id_usuario)
        exercicio_escolhido = None
        if exercicios:
            exercicio_escolhido = exercicio if exercicio in exercicios else exercicios[0]

        evolucao_carga = []
        if exercicio_escolhido:
            registros = AtividadeRepository.listar_do_usuario_por_titulo(
                id_usuario, exercicio_escolhido.strip().lower()
            )
            maior = None
            for registro in registros:
                if registro.carga_kg is None:
                    continue
                valor = float(registro.carga_kg)
                maior = valor if maior is None else max(maior, valor)
                evolucao_carga.append({
                    "data": registro.data_registro.date().isoformat(),
                    "carga_maxima": maior,
                })

        return {
            "xp_por_semana": xp_por_semana,
            "treinos_por_semana": treinos_por_semana,
            "distribuicao_por_tipo": distribuicao_por_tipo,
            "sequencia_atual": sequencia_atual,
            "melhor_sequencia": melhor_sequencia,
            "totais": {
                "treinos": total_treinos,
                "tempo_min": total_tempo,
                "xp": usuario.xp,
            },
            "exercicios_disponiveis": exercicios,
            "exercicio_selecionado": exercicio_escolhido,
            "evolucao_carga": evolucao_carga,
        }

    @staticmethod
    def _semanas(hoje):
        inicio_semana_atual = hoje - timedelta(days=hoje.weekday())
        return [
            inicio_semana_atual - timedelta(weeks=i)
            for i in range(SEMANAS_JANELA - 1, -1, -1)
        ]

    @staticmethod
    def _soma_semana(mapa_por_dia, inicio_semana):
        fim_semana = inicio_semana + timedelta(days=6)
        return sum(
            valor for dia, valor in mapa_por_dia.items()
            if inicio_semana <= dia <= fim_semana
        )

    @staticmethod
    def _sequencias(dias, hoje):
        if not dias:
            return 0, 0

        dias_ordenados = sorted(set(dias))
        comprimento_do_run_que_termina_em = {dias_ordenados[0]: 1}
        melhor = 1

        for indice in range(1, len(dias_ordenados)):
            anterior = dias_ordenados[indice - 1]
            atual = dias_ordenados[indice]
            if (atual - anterior).days == 1:
                comprimento_do_run_que_termina_em[atual] = comprimento_do_run_que_termina_em[anterior] + 1
            else:
                comprimento_do_run_que_termina_em[atual] = 1
            melhor = max(melhor, comprimento_do_run_que_termina_em[atual])

        ultimo_dia = dias_ordenados[-1]
        if ultimo_dia in (hoje, hoje - timedelta(days=1)):
            sequencia_atual = comprimento_do_run_que_termina_em[ultimo_dia]
        else:
            sequencia_atual = 0

        return sequencia_atual, melhor
