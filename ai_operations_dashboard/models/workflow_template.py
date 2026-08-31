import json
import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PANTHERHIVE_WORKFLOW_TEMPLATES_URL = 'https://pantherhive-api.hotwodi4.workers.dev/api/workflow-templates'


class AIWorkflowTemplate(models.Model):
    _name = 'ai.workflow.template'
    _description = 'PantherHive Workflow Template'
    _order = 'vertical_id, sequence, id'

    name = fields.Char(string='Template Name', required=True)
    sequence = fields.Integer(default=10)
    vertical_id = fields.Char(string='Vertical', required=True)
    template_key = fields.Char(string='Template Key', required=True)
    service_catalog_template = fields.Char(string='Service Catalog')
    tips = fields.Text(string='Tips')
    active = fields.Boolean(default=True)
    color = fields.Char(string='Color', default='blue')

    _sql_constraints = [
        ('vertical_template_uniq', 'unique(vertical_id, template_key)', 'Template must be unique per vertical.'),
    ]

    @api.model
    def _build_templates_from_cloud(self, payload):
        templates = payload.get('templates', [])
        values = []
        color_map = self._default_color_map()
        color_index = 0
        for item in templates:
            vertical = item.get('vertical_id') or item.get('id')
            tips = item.get('tips', '')
            catalog = item.get('service_catalog_template', '')
            color = color_map.get(vertical, 'blue')
            keys = item.get('workflow_templates') or []
            if not isinstance(keys, list):
                try:
                    keys = json.loads(keys) if keys else []
                except Exception:
                    keys = []
            for idx, key in enumerate(keys):
                name = self._template_name(vertical, key)
                values.append({
                    'name': name,
                    'sequence': (idx + 1) * 10,
                    'vertical_id': vertical,
                    'template_key': key,
                    'service_catalog_template': catalog,
                    'tips': tips,
                    'active': True,
                    'color': color,
                })
            color_index += 1
        return values

    def _template_name(self, vertical, key):
        name = key.replace('_', ' ').title()
        return f"{vertical.replace('_', ' ').title()} - {name}"

    def _default_color_map(self):
        return {
            'hvac': 'blue',
            'plumbing': 'cyan',
            'electrical': 'yellow',
            'cleaning': 'green',
            'landscaping': 'green',
            'roofing': 'orange',
            'general_contractor': 'purple',
            'trucking': 'indigo',
            'auto_repair': 'red',
            'property_management': 'teal',
            'retail': 'pink',
            'consulting': 'blue',
            'marketing': 'magenta',
            'it_services': 'lime',
            'medical': 'sky',
            'real_estate': 'amber',
        }

    @api.model
    def sync_from_pantherhive(self):
        try:
            resp = requests.get(PANTHERHIVE_WORKFLOW_TEMPLATES_URL, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            _logger.error('PantherHive workflow sync failed: %s', e)
            raise UserError(_('Failed to fetch workflow templates from PantherHive: %s') % str(e))

        values = self._build_templates_from_cloud(data)
        if not values:
            raise UserError(_('No workflow templates returned from PantherHive.'))

        created = 0
        for vals in values:
            existing = self.search([
                ('vertical_id', '=', vals['vertical_id']),
                ('template_key', '=', vals['template_key'])
            ], limit=1)
            if not existing:
                self.create(vals)
                created += 1
            else:
                existing.write(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Complete'),
                'message': _('%s workflow templates synced from PantherHive.') % created,
                'type': 'success',
            }
        }
