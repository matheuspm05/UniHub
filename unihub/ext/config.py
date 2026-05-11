from unihub.config import get_config


def init_app(app, test_config=None):
    config_class = get_config()
    app.config.from_object(config_class)

    if test_config:
        app.config.update(test_config)
