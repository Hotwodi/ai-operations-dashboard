from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AIAutomationRule(models.Model):
    _name = 'ai.automation.rule'
    _description = 'AI Automation Rule'
    _order = 'sequence, id'

    name = fields.Char(string='Rule Name', required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', string='Model Name', store=True)
    trigger = fields.Selection([
        ('on_create', 'On Create'),
        ('on_write', 'On Write'),
        ('on_cron', 'Scheduled (Cron)'),
        ('manual', 'Manual'),
    ], string='Trigger', required=True, default='on_write')
    domain = fields.Char(string='Filter Domain', default="[]", help="Domain to filter records for this rule")
    condition_field = fields.Char(string='Condition Field', help="Optional field to monitor for on_write trigger")
    action_type = fields.Selection([
        ('update_field', 'Update Field'),
        ('create_record', 'Create Record'),
        ('send_email', 'Send Email'),
        ('webhook', 'Call Webhook'),
        ('ai_insight', 'Generate AI Insight'),
    ], string='Action', required=True, default='update_field')
    action_field = fields.Char(string='Action Field', help="Field to update for update_field action")
    action_value = fields.Text(string='Action Value / Expression')
    action_model_id = fields.Many2one('ir.model', string='Target Model', help="For create_record action")
    action_values = fields.Text(string='Values to Create')
    webhook_url = fields.Char(string='Webhook URL')
    ai_prompt = fields.Text(string='AI Prompt')
    last_run = fields.Datetime(string='Last Run')
    run_count = fields.Integer(string='Run Count', default=0)
    note = fields.Text(string='Notes')

    def _eval_domain(self, record):
        if not self.domain or self.domain == '[]':
            return True
        try:
            domain = eval(self.domain) if isinstance(self.domain, str) else self.domain
            return record.filtered_domain(domain) == record
        except Exception as e:
            _logger.error('Domain eval error in rule %s: %s', self.name, e)
            return False

    def run_on_record(self, record):
        if not self._eval_domain(record):
            return False
        if self.action_type == 'update_field':
            if self.action_field and self.action_value:
                try:
                    value = eval(self.action_value, {'record': record, 'env': self.env})
                    record.write({self.action_field: value})
                except Exception as e:
                    _logger.error('Update field error: %s', e)
        elif self.action_type == 'create_record':
            if self.action_model_id and self.action_values:
                try:
                    vals = eval(self.action_values, {'record': record, 'env': self.env})
                    self.env[self.action_model_id.model].create(vals)
                except Exception as e:
                    _logger.error('Create record error: %s', e)
        elif self.action_type == 'send_email':
            _logger.info('Send email action not yet implemented for rule %s', self.name)
        elif self.action_type == 'webhook':
            _logger.info('Webhook action not yet implemented for rule %s', self.name)
        elif self.action_type == 'ai_insight':
            self._run_ai_insight(record)

        self.write({'last_run': fields.Datetime.now(), 'run_count': self.run_count + 1})
        return True

    def _run_ai_insight(self, record):
        if not self.ai_prompt:
            return
        try:
            prompt = self.ai_prompt.format(record=record, name=record.display_name)
            result = self.env['res.config.settings'].ai_ask(prompt, {'model': record._name, 'id': record.id})
            record.message_post(body=result, subject=_('AI Insight: %s') % self.name)
        except Exception as e:
            _logger.error('AI insight failed for rule %s: %s', self.name, e)

    @api.model
    def _run_scheduled_rules(self):
        rules = self.search([('active', '=', True), ('trigger', '=', 'on_cron')])
        for rule in rules:
            try:
                records = self.env[rule.model_id.model].search([])
                for record in records:
                    rule.run_on_record(record)
            except Exception as e:
                _logger.error('Scheduled rule %s failed: %s', rule.name, e)
