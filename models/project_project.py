# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import _, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _post_purchase_confirmed_message(self, scenarios, budgets):
        self.ensure_one()
        lines = [_('Compra confirmada: %s.') % ', '.join(budgets.mapped('product_id.display_name'))]
        lines.append(_('Escenarios respaldados: %s.') % ', '.join(scenarios.mapped('name')))
        if self.scenario_selection_strategy == 'manual':
            lines.append(_(
                'La selección de escenario está en modo manual — pasá a "Selección '
                'automática" para que esto se refleje en el escenario base.'
            ))
        self.message_post(body=Markup('<br/>').join(lines))
