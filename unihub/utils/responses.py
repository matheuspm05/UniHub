from flask import jsonify


def resposta_sucesso(mensagem="Operacao realizada com sucesso", dados=None, codigo_status=200):
    corpo = {
        "success": True,
        "message": mensagem,
        "data": dados if dados is not None else {},
    }
    return jsonify(corpo), codigo_status


def resposta_erro(mensagem="Erro interno", codigo_status=500, erros=None):
    corpo = {
        "success": False,
        "message": mensagem,
        "errors": erros if erros is not None else {},
    }
    return jsonify(corpo), codigo_status


def resposta_api(mensagem="Operacao realizada com sucesso", dados=None, codigo_status=200, sucesso=True):
    if sucesso:
        return resposta_sucesso(mensagem=mensagem, dados=dados, codigo_status=codigo_status)
    return resposta_erro(mensagem=mensagem, codigo_status=codigo_status, erros=dados)
