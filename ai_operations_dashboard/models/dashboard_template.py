import json
from odoo import models, fields, api, _

FONTS = [
    "Arial, sans-serif",
    "Helvetica, sans-serif",
    "Georgia, serif",
    "Times New Roman, serif",
    "Courier New, monospace",
    "Verdana, sans-serif",
    "Tahoma, sans-serif",
    "Trebuchet MS, sans-serif",
    "Impact, sans-serif",
    "Comic Sans MS, cursive",
    "Roboto, sans-serif",
    "Open Sans, sans-serif",
    "Lato, sans-serif",
    "Montserrat, sans-serif",
    "Poppins, sans-serif",
    "Nunito, sans-serif",
    "Raleway, sans-serif",
    "Oswald, sans-serif",
    "Merriweather, serif",
    "PT Sans, sans-serif",
    "Ubuntu, sans-serif",
    "Playfair Display, serif",
    "Noto Sans, sans-serif",
    "Fira Sans, sans-serif",
    "Work Sans, sans-serif",
    "Source Sans Pro, sans-serif",
    "Quicksand, sans-serif",
    "Karla, sans-serif",
    "Rubik, sans-serif",
    "Libre Baskerville, serif",
    "Inconsolata, monospace",
    "Cabin, sans-serif",
    "Barlow, sans-serif",
    "Heebo, sans-serif",
    "Muli, sans-serif",
    "Exo 2, sans-serif",
    "Dosis, sans-serif",
    "Josefin Sans, sans-serif",
    "Varela Round, sans-serif",
    "Catamaran, sans-serif",
    "Titillium Web, sans-serif",
    "Hind, sans-serif",
    "Maven Pro, sans-serif",
    "Comfortaa, cursive",
    "Teko, sans-serif",
    "Rajdhani, sans-serif",
    "Saira, sans-serif",
    "Kanit, sans-serif",
    "Prompt, sans-serif",
    "Anton, sans-serif",
    "Bebas Neue, sans-serif",
    "Abril Fatface, cursive",
    "Righteous, cursive",
    "Cinzel, serif",
    "Old Standard TT, serif",
    "Zilla Slab, serif",
    "Spectral, serif",
    "Manuale, serif",
    "Domine, serif",
    "Cormorant, serif",
    "Bitter, serif",
    "Eczar, serif",
    "Nunito Sans, sans-serif",
    "Public Sans, sans-serif",
    "Inter, sans-serif",
    "Space Grotesk, sans-serif",
    "DM Sans, sans-serif",
    "Lexend, sans-serif",
    "Gantari, sans-serif",
    "Outfit, sans-serif",
    "Figtree, sans-serif",
    "Plus Jakarta Sans, sans-serif",
    "Sora, sans-serif",
    "Syne, sans-serif",
    "Epilogue, sans-serif",
    "Albert Sans, sans-serif",
    "Red Hat Display, sans-serif",
    "Urbanist, sans-serif",
    "Kumbh Sans, sans-serif",
    "Nabla, cursive",
    "Shizuru, cursive",
    "Rubik Mono One, sans-serif",
    "Bungee, cursive",
    "Bungee Shade, cursive",
    "Monoton, cursive",
    "Fredoka, cursive",
    "Pacifico, cursive",
    "Dancing Script, cursive",
    "Lobster, cursive",
    "Great Vibes, cursive",
    "Caveat, cursive",
    "Satisfy, cursive",
    "Courgette, cursive",
    "Kalam, cursive",
    "Sacramento, cursive",
    "Parisienne, cursive",
    "Satisfy, cursive",
    "Rokkitt, serif",
    "Archivo, sans-serif",
    "Vollkorn, serif",
    "Neuton, serif",
    "Arvo, serif",
    "Lora, serif",
    "Crimson Pro, serif",
    "BioRhyme, serif",
    "Sanchez, serif",
    "Radley, serif",
    "Proza Libre, sans-serif",
    "Concert One, cursive",
    "Patua One, cursive",
    "Raleway Dots, cursive",
]

COLORS = [
    'blue', 'cyan', 'yellow', 'green', 'orange', 'purple', 'indigo', 'red',
    'teal', 'pink', 'magenta', 'lime', 'sky', 'amber', 'gray', 'black',
]


class AIDashboardTemplate(models.Model):
    _name = 'ai.dashboard.template'
    _description = 'AI Dashboard UI Variation'
    _order = 'sequence, id'

    name = fields.Char(string='Variation Name', required=True)
    sequence = fields.Integer(default=10)
    workflow_template_id = fields.Many2one('ai.workflow.template', string='Workflow Template', required=True, ondelete='cascade')
    font_family = fields.Char(string='Font Family', required=True)
    color = fields.Char(string='Color', default='blue')
    layout = fields.Text(string='Layout JSON', default='{}')
    active = fields.Boolean(default=True)

    @api.model
    def _generate_variations(self):
        workflow_templates = self.env['ai.workflow.template'].search([], order='id')
        if not workflow_templates:
            return

        existing = self.search([('active', '=', True)])
        if existing:
            existing.write({'active': False})

        created = 0
        for i, font in enumerate(FONTS):
            wf = workflow_templates[i % len(workflow_templates)]
            color = COLORS[i % len(COLORS)]
            name = f"{wf.name} — {font.split(',')[0].strip()}"
            layout = json.dumps({
                'font_family': font,
                'color': color,
                'vertical_id': wf.vertical_id,
                'template_key': wf.template_key,
            })
            self.create({
                'name': name,
                'sequence': (i + 1) * 10,
                'workflow_template_id': wf.id,
                'font_family': font,
                'color': color,
                'layout': layout,
                'active': True,
            })
            created += 1
        return created
