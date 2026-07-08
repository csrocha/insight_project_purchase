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

    def _notify_insight_cost_budgets(self):
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
            project._post_purchase_confirmed_message(scenarios, project_budgets)
            if project.scenario_selection_strategy == 'automatic':
                project._apply_selection_strategy()
