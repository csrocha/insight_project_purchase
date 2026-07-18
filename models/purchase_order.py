# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_approve(self, force=False):
        """button_confirm() no siempre deja state='purchase' (con doble
        validación de compras lo deja en 'to approve' hasta que se aprueba
        a mano) — button_approve() es el método que efectivamente escribe
        state='purchase'/'done' en todos los caminos (confirmación directa o
        aprobación manual posterior), así que es el hook correcto para
        reaccionar a "esta compra ya es real"."""
        res = super().button_approve(force=force)
        self.filtered(lambda o: o.state in ('purchase', 'done'))._notify_insight_cost_budgets()
        return res

    def button_cancel(self):
        """Hook simétrico a button_approve: si se cancela una compra que ya
        respaldaba un escenario (estaba en 'purchase'/'done'), coverage_state
        se recalcula solo (compute sobre purchase_id.state), pero sin esto
        nadie se entera en el chatter ni se reevalúa la estrategia de
        selección — mismo gap que documentaba BACKLOG.md ítem 1."""
        orders_to_notify = self.filtered(lambda o: o.state in ('purchase', 'done'))
        res = super().button_cancel()
        orders_to_notify._notify_insight_cost_budgets(cancelled=True)
        return res

    def _notify_insight_cost_budgets(self, cancelled=False):
        budgets = self.env['insight.cost.budget'].search([
            ('purchase_id', 'in', self.order_line.ids),
        ])
        if not budgets:
            return
        by_project = defaultdict(lambda: self.env['insight.cost.budget'])
        for budget in budgets:
            by_project[budget.project_id] |= budget
        for project, project_budgets in by_project.items():
            scenarios = project.scenario_ids.filtered(
                lambda s: s.cost_budget_ids & project_budgets
            )
            if not scenarios:
                continue
            if cancelled:
                project._post_purchase_cancelled_message(scenarios, project_budgets)
            else:
                project._post_purchase_confirmed_message(scenarios, project_budgets)
            if project.scenario_selection_strategy == 'automatic':
                project._apply_selection_strategy()
