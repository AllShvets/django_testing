from django.conf import settings
from news.forms import CommentForm


def test_home_page_news_count(
    client,
    multiple_news_on_home_page,
    home_page_news_url
):
    """
    Тестирует, что количество новостей на главной странице
    не превышает установленное значение.

    В данном тесте отправляется GET-запрос на главную страницу новостей и
    проверяется, что количество отображаемых новостей в контексте ответа
    не превышает значения, заданного в настройках (NEWS_COUNT_ON_HOME_PAGE).
    """
    response = client.get(home_page_news_url)
    assert len(
        response.context['object_list']
    ) <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_date(client, home_page_news_url):
    """
    Тестирует, что новости на главной странице сортируются по дате
    от самой свежей к самой старой.
    """
    response = client.get(home_page_news_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_anonymous_client_has_no_form(client, detail_page_news_url):
    """
    Тестирует, что анонимный пользователь
    не видит форму комментариев на странице деталей новости.

    В данном тесте отправляется GET-запрос на страницу деталей новости.
    Проверяется, что в контексте ответа нет ключа 'form', что подтверждает
    отсутствие формы комментариев для анонимных пользователей.
    """
    response = client.get(detail_page_news_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(
    authenticated_author_client,
    detail_page_news_url
):
    """
    Тестирует, что авторизованный пользователь видит форму комментариев
    на странице деталей новости.

    В данном тесте отправляется GET-запрос на страницу деталей новости
    с авторизованным клиентом. Проверяется, что в контексте ответа присутствует
    ключ 'form' и что объект `form` является экземпляром `CommentForm`.
    """
    response = authenticated_author_client.get(detail_page_news_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
