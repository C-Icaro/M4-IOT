#!/usr/bin/env python3
"""
CLI do contador de check-ins — Inteli.
Informe check-ins já perdidos e faltas planejadas (dias e/ou check-ins);
exibe quantos ainda pode faltar e o percentual final.
"""

import argparse
import sys

from constants import MAX_CHECKINS_FALTA, LIMITE_PCT
from calculator import percentual_atual, restante_permitido, simular_planejamento


def _parse_int_nao_negativo(valor: str, nome: str) -> int:
    """Converte string para int não negativo; em caso de erro, sai com mensagem."""
    try:
        n = int(valor)
        if n < 0:
            print(f"Erro: {nome} deve ser um número não negativo.", file=sys.stderr)
            sys.exit(1)
        return n
    except ValueError:
        print(f"Erro: {nome} deve ser um número inteiro válido.", file=sys.stderr)
        sys.exit(1)


def _parse_float_nao_negativo(valor: str, nome: str) -> float:
    """Converte string para float não negativo; em caso de erro, sai com mensagem."""
    try:
        n = float(valor.replace(",", "."))
        if n < 0:
            print(f"Erro: {nome} deve ser um número não negativo.", file=sys.stderr)
            sys.exit(1)
        return n
    except ValueError:
        print(f"Erro: {nome} deve ser um número válido.", file=sys.stderr)
        sys.exit(1)


def _exibir_resultado(
    checkins_ja_perdidos: float,
    dias_planejados: int,
    checkins_planejados: int,
) -> None:
    pct_atual = percentual_atual(checkins_ja_perdidos)
    restante = restante_permitido(checkins_ja_perdidos)
    resultado = simular_planejamento(
        checkins_ja_perdidos,
        dias_planejados=dias_planejados,
        checkins_planejados=checkins_planejados,
    )

    print()
    print("--- Situação atual ---")
    print(f"Check-ins já perdidos: {checkins_ja_perdidos}")
    print(f"Percentual atual de falta: {pct_atual:.2f}%")
    print(f"Check-ins que ainda pode faltar (sem ultrapassar 20%): {int(restante)}")
    print()
    print("--- Após suas faltas planejadas ---")
    print(f"Dias planejados: {dias_planejados} (={dias_planejados * 3} check-ins)")
    print(f"Check-ins planejados (extra): {checkins_planejados}")
    print(f"Total de check-ins em falta após planejamento: {resultado['checkins_total_falta']:.1f}")
    print(f"Percentual final de falta: {resultado['pct_final']:.2f}%")
    if resultado["ultrapassa_limite"]:
        print()
        print("*** ATENÇÃO: você ultrapassará o limite de 20%. Risco de corte da bolsa. ***")
    else:
        print()
        print("Você permanece dentro do limite de 20%.")


def _modo_interativo() -> None:
    """Pergunta os valores via prompts e exibe o resultado."""
    print("Contador de check-ins — Inteli")
    print("(Limite: 20% de falta. Cada check-in = 0,75%.)")
    print()

    while True:
        r = input("Check-ins já perdidos no módulo (ou Enter para 0): ").strip() or "0"
        try:
            checkins_ja_perdidos = float(r.replace(",", "."))
            if checkins_ja_perdidos < 0:
                print("Digite um número não negativo.")
                continue
            break
        except ValueError:
            print("Digite um número válido.")

    while True:
        r = input("Quantos dias você planeja faltar? (ou Enter para 0): ").strip() or "0"
        try:
            dias_planejados = int(r)
            if dias_planejados < 0:
                print("Digite um número não negativo.")
                continue
            break
        except ValueError:
            print("Digite um número inteiro válido.")

    while True:
        r = input("Quantos check-ins extras planeja faltar (além dos dias)? (ou Enter para 0): ").strip() or "0"
        try:
            checkins_planejados = int(r)
            if checkins_planejados < 0:
                print("Digite um número não negativo.")
                continue
            break
        except ValueError:
            print("Digite um número inteiro válido.")

    _exibir_resultado(checkins_ja_perdidos, dias_planejados, checkins_planejados)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Contador de check-ins Inteli: calcula faltas e percentual no módulo."
    )
    parser.add_argument(
        "--ja-perdidos",
        type=str,
        default=None,
        metavar="N",
        help="Check-ins já perdidos no módulo (padrão: 0)",
    )
    parser.add_argument(
        "--dias",
        type=str,
        default=None,
        metavar="N",
        help="Dias que planeja faltar (padrão: 0)",
    )
    parser.add_argument(
        "--checkins",
        type=str,
        default=None,
        metavar="N",
        help="Check-ins extras que planeja faltar (padrão: 0)",
    )
    parser.add_argument(
        "-i", "--interativo",
        action="store_true",
        help="Modo interativo: pergunta os valores",
    )
    args = parser.parse_args()

    if args.interativo:
        _modo_interativo()
        return

    checkins_ja_perdidos = _parse_float_nao_negativo(
        args.ja_perdidos or "0", "Check-ins já perdidos"
    )
    dias_planejados = _parse_int_nao_negativo(args.dias or "0", "Dias")
    checkins_planejados = _parse_int_nao_negativo(
        args.checkins or "0", "Check-ins planejados"
    )

    _exibir_resultado(checkins_ja_perdidos, dias_planejados, checkins_planejados)


if __name__ == "__main__":
    main()
