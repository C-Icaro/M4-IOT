"""Cálculos de faltas e percentuais para o contador de check-ins Inteli."""

from constants import MAX_CHECKINS_FALTA, PCT_POR_CHECKIN, LIMITE_PCT


def percentual_atual(checkins_ja_perdidos: float) -> float:
    """Retorna o percentual de falta atual (0.75% por check-in perdido)."""
    return checkins_ja_perdidos * PCT_POR_CHECKIN


def restante_permitido(checkins_ja_perdidos: float) -> float:
    """
    Retorna quantos check-ins ainda podem ser perdidos sem ultrapassar 20%.
    Conservador: valor pode ser truncado para inteiro na exibição.
    """
    return max(0.0, MAX_CHECKINS_FALTA - checkins_ja_perdidos)


def simular_planejamento(
    checkins_ja_perdidos: float,
    dias_planejados: int = 0,
    checkins_planejados: int = 0,
) -> dict:
    """
    Simula o impacto de faltas planejadas (dias e/ou check-ins).
    Dias são convertidos em check-ins (1 dia = 3 check-ins).

    Retorna:
        - checkins_total_falta: total de check-ins em falta após planejamento
        - pct_final: percentual final de falta
        - checkins_restantes: quantos check-ins ainda pode faltar (antes do planejamento)
        - ultrapassa_limite: True se pct_final > 20%
    """
    checkins_planejados_total = checkins_planejados + (dias_planejados * 3)
    checkins_total_falta = checkins_ja_perdidos + checkins_planejados_total
    pct_final = checkins_total_falta * PCT_POR_CHECKIN
    checkins_restantes = restante_permitido(checkins_ja_perdidos)
    ultrapassa_limite = pct_final > LIMITE_PCT

    return {
        "checkins_total_falta": checkins_total_falta,
        "pct_final": pct_final,
        "checkins_restantes": checkins_restantes,
        "ultrapassa_limite": ultrapassa_limite,
        "checkins_planejados": checkins_planejados_total,
    }
