# Insight Project — Purchase Integration

Vincula los costos extra de infraestructura/SaaS de `insight_project`
(`insight.cost.budget`) a compras reales (`purchase.order.line`):

- Cada línea de costo puede apuntar a una línea de compra concreta. Si la
  tiene, el monto se autocompleta desde el precio de esa línea; si no, sigue
  siendo una estimación manual.
- El estado de cobertura (`estimado` / `cotizado` / `comprado`) se deriva del
  estado de la orden de compra vinculada.
- Al aprobarse una orden de compra que respalda algún costo, se avisa en el
  chatter del proyecto afectado y, si la estrategia de selección de
  escenario es "automática", se recalcula cuál escenario es el baseline.
- `insight.scenario.secured_extra_cost` expone cuánto del costo extra total
  ya está respaldado por compras confirmadas, separado de lo que sigue
  siendo estimación.

Depende de `insight_project` y `purchase`.
