# BACKLOG

Ideas y mejoras propuestas para `insight_project_purchase` que todavía no
se implementaron. Primer archivo de este tipo para este módulo (mismo
formato que `insight_project/BACKLOG.md`).

---

## Del backlog de ecosistema (2026-07-13)

Propuesta de "nivel profesional superior" para todo el ecosistema. Visión
completa en la memoria `project_ecosystem_roadmap`.

### 1. Hook de cancelación simétrico a `button_approve`

`models/purchase_order.py` sobreescribe `button_approve(force=False)`
para notificar `insight.cost.budget` cuando una compra queda
aprobada/hecha — pero **`button_cancel` no está sobreescrito en
absoluto**, confirmado por auditoría de código (2026-07-13). Si se
cancela una compra que respaldaba un escenario, `coverage_state` se
termina recalculando solo (es un campo compute), pero sin ningún
`message_post` en el chatter y sin recálculo de
`_apply_selection_strategy()` — el usuario no se entera de que ese
recálculo pasó ni de que puede haber cambiado el escenario ganador.
Agregar el hook simétrico: al cancelar, recalcular la estrategia de
selección del proyecto afectado y postear el motivo en el chatter, mismo
patrón que ya usa `button_approve`.

Bajo esfuerzo, alta relación costo/beneficio — es deuda técnica ya
documentada (asimetría real en el código), no una feature nueva.

_Fuente: backlog de ecosistema propuesto por el usuario (2026-07-13,
"Épica 6" ítem 1)._
