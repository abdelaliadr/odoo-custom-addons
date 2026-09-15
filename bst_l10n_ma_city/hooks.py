def post_init_hook(env):
    env.cr.execute("""
        UPDATE ir_model_data
           SET noupdate = TRUE
         WHERE module = 'bst_l10n_ma_city'
           AND model = 'res.city'
    """)