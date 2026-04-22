# Contador de Check-ins — Inteli

Ferramenta para controlar faltas no módulo da Inteli: você informa quantos check-ins já perdeu e quantos dias ou check-ins planeja faltar; o contador mostra **quantos check-ins ainda pode faltar** e o **percentual final de falta**, com aviso se ultrapassar o limite (risco de corte da bolsa).

## Regras da Inteli (resumo)

- São **3 check-ins por dia**.
- Cada check-in equivale a **0,75%** de falta.
- O limite é **20%** de falta: acima disso há **corte da bolsa**.
- Em termos de check-ins: 20 ÷ 0,75 ≈ **26,67** check-ins é o máximo que pode ser perdido (arredondando para baixo, 26 é uma margem segura).
- Anulação de faltas não é considerada nesta ferramenta.

## Fórmulas

| Conceito                   | Fórmula                                                |
| -------------------------- | ------------------------------------------------------ |
| Percentual atual           | `percentual = checkins_ja_perdidos × 0,75`             |
| Check-ins ainda permitidos | `restante = (20 / 0,75) - checkins_ja_perdidos`        |
| Após planejamento          | `total_falta = checkins_ja_perdidos + planejados`      |
| Percentual final           | `pct_final = total_falta × 0,75`                       |
| Dias → check-ins           | `checkins = dias × 3`                                  |

## Como usar

### CLI (Python)

Recomendado usar a partir da pasta do projeto:

```bash
cd Check-in_counter
python main.py -i
```

Ou com argumentos:

```bash
python main.py --ja-perdidos 5 --dias 2 --checkins 1
```

- **Modo interativo:** `python main.py -i` ou `python main.py --interativo` — o programa pergunta check-ins já perdidos, dias e check-ins planejados.
- **Argumentos:**
  - `--ja-perdidos N` — check-ins já perdidos no módulo (padrão: 0).
  - `--dias N` — dias que planeja faltar (padrão: 0).
  - `--checkins N` — check-ins extras que planeja faltar (padrão: 0).

### Versão web

Abra o arquivo `index.html` no navegador. Preencha os campos e use o botão para ver o resultado (check-ins restantes, percentual final e aviso de risco).

## Estrutura do projeto

```
Check-in_counter/
├── README.md          # Este arquivo (regras, fórmulas, uso)
├── constants.py       # Constantes: 3 check-ins/dia, 0,75%, limite 20%
├── calculator.py      # restante_permitido(), percentual_atual(), simular_planejamento()
├── main.py            # CLI: argumentos e modo interativo
├── requirements.txt   # Sem dependências externas
└── index.html         # Versão web (mesmas regras e cálculos)
```

## Exemplo de saída (CLI)

```
--- Situação atual ---
Check-ins já perdidos: 5
Percentual atual de falta: 3.75%
Check-ins que ainda pode faltar (sem ultrapassar 20%): 21

--- Após suas faltas planejadas ---
Dias planejados: 2 (= 6 check-ins)
Check-ins planejados (extra): 1
Total de check-ins em falta após planejamento: 12.0
Percentual final de falta: 9.00%

Você permanece dentro do limite de 20%.
```

Se o percentual final passar de 20%, é exibido:

**\*\*\* ATENÇÃO: você ultrapassará o limite de 20%. Risco de corte da bolsa. \*\*\***
