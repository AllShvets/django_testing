from http import HTTPStatus

from .test_case_base import TestCaseBase


class TestRoutes(TestCaseBase):
    def test_pages_availability(self):
        """
        Проверяет доступность страниц для
        авторизованных и неавторизованных пользователей.
        """
        # Определение ожидаемых статусов для различных клиентов и URL
        test_cases = [
            (self.client, self.HOME_URL, HTTPStatus.OK),
            (self.client, self.LOGIN_URL, HTTPStatus.OK),
            (self.client, self.LOGOUT_URL, HTTPStatus.OK),
            (self.client, self.SIGNUP_URL, HTTPStatus.OK),
            (self.not_author_client, self.ADD_URL, HTTPStatus.OK),
            (self.not_author_client, self.LIST_URL, HTTPStatus.OK),
            (self.not_author_client, self.SUCCESS_URL, HTTPStatus.OK),
            (self.not_author_client, self.DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.not_author_client, self.UPDATE_URL, HTTPStatus.NOT_FOUND),
            (self.not_author_client, self.DELETE_URL, HTTPStatus.NOT_FOUND),
            (self.author_client, self.DETAIL_URL, HTTPStatus.OK),
            (self.author_client, self.UPDATE_URL, HTTPStatus.OK),
            (self.author_client, self.DELETE_URL, HTTPStatus.OK),
        ]

        # Итерация по каждому тестовому случаю
        for client, url, expected_status in test_cases:
            with self.subTest(
                client=client,
                url=url,
                expected_status=expected_status
            ):
                self._check_page_availability(client, url, expected_status)

    def _check_page_availability(self, client, url, expected_status):
        """Проверяет код статуса ответа для заданного клиента и URL."""
        response = client.get(url)

        self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """Проверяет перенаправления для анонимных пользователей."""
        # URL для перенаправления
        redirectable_urls = [
            self.ADD_URL,
            self.DELETE_URL,
            self.DETAIL_URL,
            self.LIST_URL,
            self.SUCCESS_URL,
            self.UPDATE_URL,
        ]

        # Проверка перенаправления на страницу входа
        for url in redirectable_urls:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
