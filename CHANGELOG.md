# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).
Versionado: `17.0.MAYOR.MENOR.PARCHE`.

Cada entrada de version incluye el **prompt** que motivo los cambios
y las **discusiones de diseno** relevantes que influyeron en las decisiones,
para trazabilidad completa del razonamiento de agentes de IA (mismo
formato que `insight_project`).

---

## [17.0.1.0.3] - 2026-08-26

### Prompt

> (Cambio derivado de insight_project 17.0.9.8.0: "En el project insight no
> le puedo asignar un escenario preexistente al proyecto...")

### Discusión de diseño

`insight_project` reemplazó el One2many `project.project.scenario_ids`
(a `insight.scenario`) por `scenario_link_ids` (a `insight.scenario.project`),
para poder compartir un escenario entre proyectos con `is_baseline` por
vínculo. `purchase_order.py._notify_insight_cost_budgets` filtraba
`project.scenario_ids` para decidir a qué escenarios avisar al confirmar/
cancelar una compra — pasa a leer `project.scenario_link_ids.scenario_id`.

### Modificado

- `models/purchase_order.py`: `project.scenario_ids` → `project.scenario_link_ids.scenario_id`.

## [17.0.1.0.2] - 2026-07-18

### Prompt

> Épica 6 (deuda técnica) del roadmap de ecosistema: hook de cancelación
> simétrico a `button_approve`.

### Agregado

- `PurchaseOrder.button_cancel()`: hook simétrico a `button_approve()`.
  Captura las órdenes en `('purchase', 'done')` antes de cancelar y, tras
  `super().button_cancel()`, reusa `_notify_insight_cost_budgets` (ahora
  con flag `cancelled=True`) en vez de duplicar la lógica de agrupar por
  proyecto.
- `ProjectProject._post_purchase_cancelled_message`: mensaje de chatter
  simétrico a `_post_purchase_confirmed_message`, más recálculo de
  `_apply_selection_strategy()` cuando la estrategia es automática.

### Discusión de diseño

- `coverage_state` no se tocó — ya se recalculaba solo vía compute sobre
  `purchase_id.state`. El gap real era solo de visibilidad (chatter) y de
  reevaluación de la estrategia de selección, no de dato.
- Módulo sin tests automatizados propios; verificado que sigue
  instalando limpio (`make test-local MODULE=insight_project_purchase`,
  0 tests/0 fallos). Falta probar el flujo en vivo cancelando una PO real.

## [17.0.1.0.1] - 2026-07-08

### Prompt

> Deployá addons/insight_project_purchase.

Al revisar el estado del repo antes del release apareció un cambio en
`models/insight_cost_budget.py` sin commitear del trabajo previo al scaffold
inicial (17.0.1.0.0): se decidió incluirlo en este release en vez de
dejarlo pendiente.

### Discusión de diseño

- **`amount` no puede ser `required=True` a nivel de campo**: al ser un
  campo `compute` con `store=True` y `readonly=False`, Odoo intenta
  insertar el registro con `amount=NULL` antes de correr el compute
  cuando no hay `purchase_id` (caso de estimación 100% manual); con
  `required=True` esa inserción intermedia viola la constraint antes de
  que el compute tenga chance de correr. Se cambió a `required=False`.
- **La obligatoriedad real se mueve a un `@api.constrains`**: en vez del
  `required` del campo, `_check_amount_or_purchase` valida que exista
  *algún* monto — manual o vía `purchase_id` — al guardar. Mantiene la
  regla de negocio ("todo costo necesita un monto de alguna forma") sin
  bloquear el flujo de estimación manual que sí soporta el módulo base
  `insight_project`.

### Corregido

- `models/insight_cost_budget.py`: campo `amount` cambiado a
  `required=False` (evita el error de inserción con NULL antes del
  compute); agregado `_check_amount_or_purchase` (`@api.constrains`) para
  exigir monto manual o línea de compra vinculada.

## [17.0.1.0.0] - 2026-07-08

### Prompt

> "A ver, un par de escenarios pueden usar dentro un mismo producto. Ahí es
> donde funciona el algoritmo de costo/duración/recursos. Si ya tenemos
> contratado el producto (eso significa que el purchase seleccionado ya fue
> comprado) eso fija el escenario, lo que no tenemos y existe un escenario
> siempre va a perder porque no tiene los recursos para que sea real, por lo
> que para avanzar en ese escenario o para tenerlo en cuenta hay que comprar
> esos recursos que le falta para avanzar. El tema de la periosidad tiene
> que seguir activo para poder calcular el costo del proyecto completo.
> Creo que esto requiere un nuevo módulo que dependa de insight_project y
> purchase."

Aclaraciones de seguimiento que definieron el diseño final:

> "El escenario se ejecuta igual, porque el administrador del proyecto
> tiene que conocer 'que se está perdiendo'. La idea es competir
> escenarios, cambiarlos y mejorarlos continuamente. [...] Debería apuntar
> a un purchase.order.line (un purchase.order puede incluir cosas que no
> nos interesa)."

### Discusión de diseño

- Se descartó vincular `insight.cost.budget` a `purchase.order` completo:
  una orden puede tener líneas de productos no relacionados, así que el
  vínculo va a `purchase.order.line` (`purchase_id`), con
  `domain="[('product_id','=',product_id)]"` para que no pueda apuntar a
  una línea de un producto distinto al de la línea de costo.
- Se mantiene `product_id` independiente de `purchase_id` (no se deriva
  uno del otro): permite crear la línea de costo "especulativa" (producto +
  skills + periodicidad + monto estimado) antes de que exista ninguna orden
  de compra, para no frenar la comparación de escenarios mientras se evalúan
  proveedores.
- La descalificación de un escenario sin recursos comprados **no es
  binaria**: el escenario sigue corriendo el schedule y compitiendo por
  costo/duración/recursos igual que cualquier otro (`_apply_selection_strategy`
  de `insight_project` no se toca). Lo que se agrega es visibilidad: cada
  línea de costo expone `coverage_state` (estimado/cotizado/comprado)
  derivado de `purchase_id.state`, y el escenario expone `secured_extra_cost`
  (cuánto de `extra_cost` ya es firme) para que el admin del proyecto decida
  si vale la pena comprar lo que le falta a un escenario que hoy pierde.
- `amount` pasa a ser `compute(store=True, readonly=False)` en vez de un
  campo manual plano: si hay `purchase_id`, se autocompleta con
  `price_subtotal` (sin impuestos, consistente con que `total_cost`/
  `extra_cost` de `insight_project` tampoco los incluyen); si no hay
  `purchase_id`, el compute no toca el valor y queda editable a mano (mismo
  patrón que `project.task.resource_pool_ids` en `project_improve`).
- **Hook de confirmación**: se evaluó `purchase.order.button_confirm()`
  primero, pero se descartó — con doble validación de compras activada,
  `button_confirm()` deja la orden en `state='to approve'`, no en
  `'purchase'`. El método que realmente escribe `state='purchase'`/`'done'`
  en todos los caminos (confirmación directa o aprobación manual posterior)
  es `button_approve()` — mismo patrón que usa `purchase_stock` para crear
  los pickings al aprobar. Ahí se dispara el aviso en el chatter del
  proyecto y, si `scenario_selection_strategy='automatic'`, la re-selección
  del escenario baseline.
- La estrategia manual del proyecto se respeta siempre: el hook nunca
  fuerza `is_baseline` ni cambia `scenario_selection_strategy`; en modo
  manual solo posta el aviso sugiriendo pasar a automático.
- `insight.scenario._cost_budget_contributions()` (extraído en
  `insight_project` v17.0.9.5.0 específicamente para esto) se reutiliza tal
  cual para `secured_extra_cost`, filtrando por `coverage_state='purchased'`,
  sin duplicar la lógica de prorrateo por skill/individual/periodicidad.
- No se crean modelos nuevos (todo es `_inherit` de `insight.cost.budget`,
  `insight.scenario`, `project.project`, `purchase.order`), así que no hace
  falta `ir.model.access.csv` propio.

### Agregado

- `insight.cost.budget.purchase_id` (M2O a `purchase.order.line`) y
  `coverage_state` (estimado/cotizado/comprado).
- `insight.scenario.secured_extra_cost`.
- Hook en `purchase.order.button_approve()`: aviso en el chatter del
  proyecto + re-selección automática de escenario cuando corresponde.
- Vistas heredadas (`views/insight_cost_budget_views.xml`) que agregan las
  columnas nuevas al catálogo de costos, al tree embebido en la pestaña
  TaskJuggler del proyecto, y `secured_extra_cost` a la vista de escenario.
