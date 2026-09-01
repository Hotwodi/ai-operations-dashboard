def post_init_hook(env):
    env['ai.dashboard.template']._generate_variations()
