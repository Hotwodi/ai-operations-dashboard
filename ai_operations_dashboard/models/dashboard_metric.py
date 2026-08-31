from odoo import models, fields, api


class AIDashboardMetric(models.Model):
    _name = 'ai.dashboard.metric'
    _description = 'AI Dashboard Metric'
    _order = 'sequence, id'

    name = fields.Char(string='Metric Name', required=True)
    sequence = fields.Integer(default=10)
    model_id = fields.Many2one('ir.model', string='Model', required=True)
    measure_field = fields.Char(string='Measure Field', required=True, help='Numeric field to aggregate')
    group_field = fields.Char(string='Group By Field')
    aggregate = fields.Selection([
        ('count', 'Count'),
        ('sum', 'Sum'),
        ('avg', 'Average'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
    ], string='Aggregate', required=True, default='count')
    color = fields.Char(string='Color', default='blue', help='Status color for the metric')
    value = fields.Float(string='Last Computed Value', readonly=True)
    last_computed = fields.Datetime(string='Last Computed', readonly=True)
    active = fields.Boolean(default=True)
    note = fields.Text(string='Notes')

    def _compute(self):
        for metric in self:
            try:
                records = metric.env[metric.model_id.model].search([])
                if metric.aggregate == 'count':
                    value = len(records)
                else:
                    vals = records.mapped(metric.measure_field) if metric.measure_field else []
                    vals = [v for v in vals if isinstance(v, (int, float))]
                    if not vals:
                        value = 0.0
                    elif metric.aggregate == 'sum':
                        value = sum(vals)
                    elif metric.aggregate == 'avg':
                        value = sum(vals) / len(vals) if vals else 0.0
                    elif metric.aggregate == 'min':
                        value = min(vals) if vals else 0.0
                    elif metric.aggregate == 'max':
                        value = max(vals) if vals else 0.0
                    else:
                        value = 0.0
                metric.write({'value': value, 'last_computed': fields.Datetime.now()})
            except Exception:
                metric.write({'value': 0.0, 'last_computed': fields.Datetime.now()})

    @api.model
    def refresh_all(self):
        self.search([])._compute()
