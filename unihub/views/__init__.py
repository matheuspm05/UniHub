def init_app(app):
    from unihub.views.admin import bp as admin_bp
    from unihub.views.eventos import agenda_bp
    from unihub.views.eventos import bp as eventos_bp
    from unihub.views.forum import bp as forum_bp
    from unihub.views.main import bp as main_bp
    from unihub.views.mensagens import bp as mensagens_bp
    from unihub.views.moradias import bp as moradias_bp
    from unihub.views.notificacoes import bp as notificacoes_bp
    from unihub.views.usuarios import bp as usuarios_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(forum_bp)
    app.register_blueprint(eventos_bp)
    app.register_blueprint(agenda_bp)
    app.register_blueprint(moradias_bp)
    app.register_blueprint(notificacoes_bp)
    app.register_blueprint(mensagens_bp)
    app.register_blueprint(admin_bp)


__all__ = ["init_app"]
