# Regras de check-in — Inteli
# 3 check-ins por dia; cada check-in = 0,75% de falta.
# Limite: 20% de falta → corte da bolsa.

CHECKINS_POR_DIA = 3
PCT_POR_CHECKIN = 0.75
LIMITE_PCT = 20
MAX_CHECKINS_FALTA = LIMITE_PCT / PCT_POR_CHECKIN  # ≈ 26.666...
