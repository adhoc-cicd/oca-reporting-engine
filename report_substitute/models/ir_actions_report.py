# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class IrActionReport(models.Model):

    _inherit = 'ir.actions.report'

    action_report_substitution_rule_ids = fields.One2many(
        comodel_name="ir.actions.report.substitution.rule",
        inverse_name="action_report_id",
        string="Substitution Rules",
    )

    @api.multi
    def _get_substitution_report(self, model, active_ids):
        self.ensure_one()
        model = self.env[model]
        for (
            substitution_report_rule
        ) in self.action_report_substitution_rule_ids:
            domain = safe_eval(substitution_report_rule.domain)
            domain.append(('id', 'in', active_ids))
            if set(model.search(domain).ids) == set(active_ids):
                return substitution_report_rule.substitution_action_report_id
        return False

    @api.model
    def get_substitution_report_dict(self, action_report_dict, active_ids):
        if action_report_dict.get('id'):
            action_report = self.browse(action_report_dict['id'])
            substitution_report = action_report
            while substitution_report:
                action_report = substitution_report
                substitution_report = action_report._get_substitution_report(
                    action_report.model, active_ids
                )
            action_report_dict.update(action_report.read()[0])
        return action_report_dict

    @api.multi
    def render(self, res_ids, data=None):
        substitution_report = self._get_substitution_report(
            self.model, res_ids
        )
        if substitution_report:
            return substitution_report.render(res_ids, data)
        return super().render(res_ids, data)
