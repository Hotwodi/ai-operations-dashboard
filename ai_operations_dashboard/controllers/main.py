import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AIOperationsController(http.Controller):

    @http.route('/ai_operations_dashboard/data', auth='user', type='json')
    def get_dashboard_data(self, **kw):
        metrics = request.env['ai.dashboard.metric'].search([])
        metrics.refresh_all()
        result = []
        for m in metrics:
            result.append({
                'id': m.id,
                'name': m.name,
                'value': round(m.value, 2),
                'color': m.color,
                'last_computed': m.last_computed,
            })
        return {'metrics': result}

    @http.route('/ai_operations_dashboard/ask', auth='user', type='json', methods=['POST'])
    def ask_ai(self, **kw):
        try:
            prompt = kw.get('prompt')
            if not prompt:
                return {'error': 'No prompt provided'}
            answer = request.env['res.config.settings'].ai_ask(prompt)
            return {'answer': answer}
        except Exception as e:
            _logger.error('AI ask failed: %s', e)
            return {'error': str(e)}
