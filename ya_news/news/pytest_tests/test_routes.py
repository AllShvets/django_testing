from http import HTTPStatus
from pytest_django.asserts import assertRedirects
import pytest
from .conftest import (
    AUTHORIZED_AUTHOR_CLIENT,
    NOT_AUTHORIZED_CLIENT,
    COMMENT_EDIT_URL,
    COMMENT_REMOVE_URL,
    HOME_PAGE_NEWS_URL,
    NEWS_DETAIL_PAGE_URL,
    USER_LOGIN_PAGE_URL,
    USER_LOGOUT_PAGE_URL,
    USER_SIGNUP_PAGE_URL,
    DEFAULT_CLIENT
)


@pytest.mark.parametrize(
    'client, url, expected_status',
    (
        (DEFAULT_CLIENT, HOME_PAGE_NEWS_URL, HTTPStatus.OK),
        (DEFAULT_CLIENT, NEWS_DETAIL_PAGE_URL, HTTPStatus.OK),
        (DEFAULT_CLIENT, USER_LOGIN_PAGE_URL, HTTPStatus.OK),
        (DEFAULT_CLIENT, USER_SIGNUP_PAGE_URL, HTTPStatus.OK),
        (DEFAULT_CLIENT, USER_LOGOUT_PAGE_URL, HTTPStatus.OK),
        (AUTHORIZED_AUTHOR_CLIENT, COMMENT_EDIT_URL, HTTPStatus.OK),
        (AUTHORIZED_AUTHOR_CLIENT, COMMENT_REMOVE_URL, HTTPStatus.OK),
        (NOT_AUTHORIZED_CLIENT, COMMENT_EDIT_URL, HTTPStatus.NOT_FOUND),
        (NOT_AUTHORIZED_CLIENT, COMMENT_REMOVE_URL, HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability(client, url, expected_status):
    """
    Проверяет доступность страниц для
    различных клиентов и ожидаемые статусы ответов.
    """
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url', (COMMENT_EDIT_URL, COMMENT_REMOVE_URL)
)
def test_redirect_pages_auth(client, url, user_login_page_url):
    """
    Проверяет перенаправление неавторизованного пользователя
    на страницу входа при попытке доступа к
    страницам редактирования или удаления комментариев.
    """
    expected_url = f'{user_login_page_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
