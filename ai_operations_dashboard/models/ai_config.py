import requests
import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AIConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('pantherhive', 'PantherHive'),
    ], string='AI Provider', config_parameter='ai_operations_dashboard.ai_provider', default='openai')
    ai_api_key = fields.Char(string='AI API Key', config_parameter='ai_operations_dashboard.ai_api_key')
    ai_model = fields.Char(string='AI Model', config_parameter='ai_operations_dashboard.ai_model', default='gpt-4o')

    @api.model
    @api.model
    def ai_ask(self, prompt, context=None):
        provider = self.env['ir.config_parameter'].sudo().get_param('ai_operations_dashboard.ai_provider', 'openai')
        api_key = self.env['ir.config_parameter'].sudo().get_param('ai_operations_dashboard.ai_api_key')
        model = self.env['ir.config_parameter'].sudo().get_param('ai_operations_dashboard.ai_model', 'gpt-4o')

        if not api_key:
            raise UserError(_('AI API key is not configured. Go to Settings → AI Operations.'))

        if provider == 'openai':
            return self._call_openai(prompt, api_key, model, context)
        elif provider == 'anthropic':
            return self._call_anthropic(prompt, api_key, model, context)
        return _('AI provider not implemented: %s') % provider

    def _call_openai(self, prompt, api_key, model, context):
        try:
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            messages = [{'role': 'system', 'content': 'You are an ERP operations assistant.'}]
            if context:
                messages.append({'role': 'user', 'content': json.dumps(context)})
            messages.append({'role': 'user', 'content': prompt})
            payload = {'model': model, 'messages': messages, 'temperature': 0.3, 'max_tokens': 500}
            resp = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            _logger.error('OpenAI call failed: %s', e)
            raise UserError(_('AI request failed: %s') % str(e))

    def _call_anthropic(self, prompt, api_key, model, context):
        try:
            headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}
            payload = {'model': model, 'max_tokens': 500, 'messages': [{'role': 'user', 'content': prompt}]}
            resp = requests.post('https://api.anthropic.com/v1/messages', headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data['content'][0]['text']
        except Exception as e:
            _logger.error('Anthropic call failed: %s', e)
            raise UserError(_('AI request failed: %s') % str(e))
