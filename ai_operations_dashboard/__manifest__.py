{
    'name': 'AI Operations Dashboard + Automation Hub',
    'version': '18.0.1.0.0',
    'images': ['static/description/cover.png'],
    'category': 'Productivity/AI',
    'summary': 'AI-powered operations dashboard and workflow automation suite',
    'description': """
        AI Operations Dashboard + Automation Hub
        ==========================================
        - AI-powered dashboard with KPIs and alerts
        - Workflow automation rules with triggers and actions
        - OpenAI / LLM integration for insights and recommendations
        - Centralized configuration for AI providers and automation
    """,
    'author': 'SoftaiDev',
    'website': 'https://softaidev.pages.dev',
    'license': 'LGPL-3',
    'price': 149.00,
    'currency': 'USD',
    'depends': ['base', 'web', 'mail'],
    'post_init_hook': 'post_init_hook',
    'data': [
        'security/ir.model.access.csv',
        'data/workflow_templates.xml',
        'views/ai_config_views.xml',
        'views/automation_rule_views.xml',
        'views/dashboard_views.xml',
        'views/workflow_template_views.xml',
        'views/dashboard_template_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
