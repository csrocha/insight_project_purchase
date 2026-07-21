# BACKLOG

Ideas y mejoras propuestas para `insight_project_purchase` que todavía no
se implementaron. Primer archivo de este tipo para este módulo (mismo
formato que `insight_project/BACKLOG.md`).

---

## Del backlog de ecosistema (2026-07-13)

Propuesta de "nivel profesional superior" para todo el ecosistema. Visión
completa en la memoria `project_ecosystem_roadmap`.

### ~~1. Hook de cancelación simétrico a `button_approve`~~ — RESUELTO

Resuelto (2026-07-18): `button_cancel()` ahora captura las órdenes en
`('purchase', 'done')` antes de cancelar, y tras `super().button_cancel()`
notifica `_notify_insight_cost_budgets(cancelled=True)` — mismo patrón que
`button_approve`, reusando el hook existente con un flag en vez de
duplicar la lógica de agrupar por proyecto. Nuevo
`_post_purchase_cancelled_message` en `project_project.py` (mensaje
simétrico a `_post_purchase_confirmed_message`) y recálculo de
`_apply_selection_strategy()` cuando la estrategia es automática. No se
tocó `coverage_state` (ya se recalculaba solo vía compute). Verificado
que el módulo sigue instalando limpio (`make test-local
MODULE=insight_project_purchase`, 0 tests/0 fallos — este módulo no tiene
tests automatizados propios); falta probar el flujo en vivo cancelando
una PO real.

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
