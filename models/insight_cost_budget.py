# -*- coding: utf-8 -*-
from odoo import api, fields, models


class InsightCostBudget(models.Model):
    _inherit = 'insight.cost.budget'

    purchase_id = fields.Many2one(
        'purchase.order.line', string='Línea de compra',
        domain="[('product_id', '=', product_id)]",
        help='Línea de compra real que respalda este costo. Vacío = estimación manual.',
    )
    amount = fields.Monetary(compute='_compute_amount_from_purchase', store=True, readonly=False)
    coverage_state = fields.Selection(
        [
            ('estimated', 'Estimado'),
            ('quoted', 'Cotizado'),
            ('purchased', 'Comprado'),
        ],
        compute='_compute_coverage_state', store=True,
        help='Estimado: sin línea de compra vinculada, monto a mano. Cotizado: hay '
             'línea de compra pero la orden todavía no está confirmada. Comprado: la '
             'orden que respalda esta línea ya fue aprobada.',
    )

    @api.depends('purchase_id.price_subtotal')
    def _compute_amount_from_purchase(self):
        for budget in self:
            if budget.purchase_id:
                budget.amount = budget.purchase_id.price_subtotal
            # sin purchase_id: no se toca, queda el valor manual (compute +
            # readonly=False preserva la edición a mano hasta que la
            # dependencia real cambie, mismo patrón que
            # project.task.resource_pool_ids en project_improve).

    @api.depends('purchase_id.state')
    def _compute_coverage_state(self):
        for budget in self:
            if not budget.purchase_id:
                budget.coverage_state = 'estimated'
            elif budget.purchase_id.state in ('purchase', 'done'):
                budget.coverage_state = 'purchased'
            else:
                budget.coverage_state = 'quoted'
