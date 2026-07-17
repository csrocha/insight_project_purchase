# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class InsightCostBudget(models.Model):
    _inherit = 'insight.cost.budget'

    purchase_id = fields.Many2one(
        'purchase.order.line', string='Línea de compra',
        domain="[('product_id', '=', product_id)]",
        help='Línea de compra real que respalda este costo. Vacío = estimación manual.',
    )
    # required=False: a diferencia de insight_project (100% manual), acá el
    # monto puede llegar solo del compute cuando hay purchase_id — la
    # obligatoriedad de "algún monto, de una forma u otra" la impone el
    # constrains de abajo, no el required del campo (si no, Odoo intenta
    # insertar NULL antes de correr el compute y explota la constraint).
    amount = fields.Monetary(
        compute='_compute_amount_from_purchase', store=True, readonly=False, required=False,
    )
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

    @api.constrains('amount', 'purchase_id')
    def _check_amount_or_purchase(self):
        for budget in self:
            if not budget.purchase_id and not budget.amount:
                raise ValidationError(_(
                    'Ingresá un monto manual o vinculá una línea de compra en "%s".'
                ) % budget.product_id.display_name)
