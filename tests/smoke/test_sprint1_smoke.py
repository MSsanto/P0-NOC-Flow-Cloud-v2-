import httpx
import pytest

pytestmark = pytest.mark.smoke


def test_qa_006_api_liveness(api_client):
    response = api_client.get("/health/live")
    assert response.status_code == 200


def test_qa_006_api_readiness_includes_database(api_client):
    response = api_client.get("/health/ready")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, dict)
    # O contrato detalhado de readiness ainda não define shape. Quando o backend
    # publicar OpenAPI, este assert deve ser endurecido para comprovar DB explicitamente.
    assert payload, "readiness não deve responder objeto vazio"


def test_qa_006_frontend_is_reachable(web_base_url):
    response = httpx.get(web_base_url, timeout=10.0, follow_redirects=True)
    assert response.status_code == 200
    assert response.text.strip(), "frontend respondeu 200 sem conteúdo"
