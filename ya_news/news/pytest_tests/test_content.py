from django.conf import settings
from django.utils import timezone
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


def test_news_sorted_by_date(client, test_news, home_page_news_url):
    """
    Тестирует, что новости на главной странице сортируются по дате
    от самой свежей к самой старой.

    В данном тесте создаются три новости с различными датами создания,
    после чего отправляется GET-запрос на главную страницу новостей.
    Проверяется, что список новостей, полученный из контекста ответа,
    соответствует порядку их создания.
    """
    news1 = test_news(title="News 1", created_at=timezone.now())
    news2 = test_news(
        title="News 2",
        created_at=timezone.now() - timezone.timedelta(days=1)
    )
    news3 = test_news(
        title="News 3",
        created_at=timezone.now() - timezone.timedelta(days=2)
    )

    response = client.get(home_page_news_url)

    news_list = response.context['object_list']

    assert list(news_list) == [news1, news2, news3]


def test_anonymous_client_has_no_form(client, news_detail_url):
    """
    Тестирует, что анонимный пользователь
    не видит форму комментариев на странице деталей новости.

    В данном тесте отправляется GET-запрос на страницу деталей новости.
    Проверяется, что в контексте ответа нет ключа 'form', что подтверждает
    отсутствие формы комментариев для анонимных пользователей.
    """
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(
    authenticated_author_client,
    news_detail_url
):
    """
    Тестирует, что авторизованный пользователь видит форму комментариев
    на странице деталей новости.

    В данном тесте отправляется GET-запрос на страницу деталей новости
    с авторизованным клиентом. Проверяется, что в контексте ответа присутствует
    ключ 'form' и что объект `form` является экземпляром `CommentForm`.
    """
    response = authenticated_author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
