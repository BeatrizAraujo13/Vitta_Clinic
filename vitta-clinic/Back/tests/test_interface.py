def test_aplicacao_serve_site_e_recursos_estaticos(cliente_teste):
    inicio = cliente_teste.get("/")
    estilo = cliente_teste.get("/css/normalizacao.css")
    script = cliente_teste.get("/js/armazenamento.js")

    assert inicio.status_code == 200
    assert b'<html lang="pt-BR">' in inicio.data
    assert estilo.status_code == 200
    assert script.status_code == 200
    assert b"/api/v1" in script.data


def test_rota_api_inexistente_nao_serve_arquivo_estatico(cliente_teste):
    resposta = cliente_teste.get("/api/v1/rota-inexistente")

    assert resposta.status_code == 404
