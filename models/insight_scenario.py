# -*- coding: utf-8 -*-
from odoo import api, fields, models


class InsightScenario(models.Model):
    _inherit = 'insight.scenario'

    secured_extra_cost = fields.Float(
        compute='_compute_secured_extra_cost', store=True, readonly=True,
        help='Parte de extra_cost ya respaldada por compras confirmadas '
             '(cost_budget_ids con coverage_state = Comprado).',
    )

    @api.depends(
        'cost_budget_ids.coverage_state', 'cost_budget_ids.amount', 'cost_budget_ids.currency_id',
        'cost_budget_ids.periodicity', 'cost_budget_ids.individual', 'cost_budget_ids.skill_ids',
        'schedule_ids.task_id.required_skill_ids', 'schedule_ids.resource_ids',
        'schedule_ids.resource_ids.employee_id.skill_ids',
        'schedule_ids.start_scheduled', 'schedule_ids.end_scheduled',
    )
    def _compute_secured_extra_cost(self):
        for scenario in self:
            scenario.secured_extra_cost = sum(
                amount for budget, amount in scenario._cost_budget_contributions()
                if budget.coverage_state == 'purchased'
            )
