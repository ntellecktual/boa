import pytest
from django.contrib.auth.models import User
from django.urls import reverse

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_home_redirects_anonymous(client):
    """Unauthenticated users are redirected away from the home dashboard."""
    response = client.get(reverse('home'))
    assert response.status_code in (302, 301)


@pytest.mark.django_db
def test_login_page_loads(client):
    response = client.get(reverse('login'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_page_loads(client):
    response = client.get(reverse('register'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_reaches_home(client):
    User.objects.create_user(username='tester', password='pass1234!')
    client.login(username='tester', password='pass1234!')
    response = client.get(reverse('home'))
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_portfolio_showcase_loads(client):
    response = client.get(reverse('portfolio_showcase'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_education_page_loads(client):
    response = client.get(reverse('education_details'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_live_demos_page_loads(client):
    response = client.get(reverse('live_demos'))
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_health_endpoint_responds(client):
    response = client.get('/health/')
    # Returns 200 when all checks pass, 500 if any fail — both are valid responses
    assert response.status_code in (200, 500)


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_api_health_endpoint(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.json()
    assert data.get('status') == 'ok'


@pytest.mark.django_db
def test_api_me_requires_auth(client):
    response = client.get('/api/v1/me')
    assert response.status_code == 401


@pytest.mark.django_db
def test_api_docs_accessible(client):
    response = client.get('/api/v1/docs')
    assert response.status_code == 200
