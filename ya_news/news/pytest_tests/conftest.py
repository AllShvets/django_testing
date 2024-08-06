import pytest
from news.models import Comment, News
from django.urls import reverse
from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from datetime import datetime, timedelta


@pytest.fixture(autouse=True)
def enable_database_access(db):
    ...


@pytest.fixture
def anon_client():
    return Client()


@pytest.fixture
def test_news(db):
    news_instance = News.objects.create(
        title='Тестовая новость',
        text='Просто текст.',
        date=datetime.today()
    )
    return news_instance


@pytest.fixture
def sample_comment(test_news, sample_author):
    comment_instance = Comment.objects.create(
        news=test_news,
        author=sample_author,
        text='Текст комментария'
    )
    return comment_instance


@pytest.fixture
def multiple_news_on_home_page(db):
    today = datetime.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def multiple_comments_for_news(sample_author, test_news):
    now = timezone.now()
    return Comment.objects.bulk_create(
        Comment(
            news=test_news,
            author=sample_author,
            text=f'Текст {index}',
            created=now + timedelta(days=index)
        )
        for index in range(10)
    )


@pytest.fixture
def update_comment_url(sample_comment):
    return reverse('news:edit', args=(sample_comment.id,))


@pytest.fixture
def delete_comment_url(sample_comment):
    return reverse('news:delete', args=(sample_comment.id,))


@pytest.fixture
def home_page_news_url():
    return reverse('news:home')


@pytest.fixture
def detail_page_news_url(test_news):
    return reverse('news:detail', args=(test_news.id,))


@pytest.fixture
def user_login_page_url():
    return reverse('users:login')


@pytest.fixture
def user_logout_page_url():
    return reverse('users:logout')


@pytest.fixture
def user_signup_page_url():
    return reverse('users:signup')


@pytest.fixture
def sample_author(django_user_model):
    return django_user_model.objects.create(username='Автор новости')


@pytest.fixture
def sample_not_author(django_user_model):
    return django_user_model.objects.create(username='Сторонний юзер')


@pytest.fixture
def authenticated_author_client(sample_author):
    client = Client()
    client.force_login(sample_author)
    return client


@pytest.fixture
def authenticated_not_author_client(sample_not_author):
    client = Client()
    client.force_login(sample_not_author)
    return client


DEFAULT_CLIENT = pytest.lazy_fixture('anon_client')

AUTHORIZED_AUTHOR_CLIENT = pytest.lazy_fixture('authenticated_author_client')

NOT_AUTHORIZED_CLIENT = pytest.lazy_fixture('authenticated_not_author_client')

COMMENT_EDIT_URL = pytest.lazy_fixture('update_comment_url')

COMMENT_REMOVE_URL = pytest.lazy_fixture('delete_comment_url')

HOME_PAGE_NEWS_URL = pytest.lazy_fixture('home_page_news_url')

NEWS_DETAIL_PAGE_URL = pytest.lazy_fixture('detail_page_news_url')

USER_LOGIN_PAGE_URL = pytest.lazy_fixture('user_login_page_url')

USER_LOGOUT_PAGE_URL = pytest.lazy_fixture('user_logout_page_url')

USER_SIGNUP_PAGE_URL = pytest.lazy_fixture('user_signup_page_url')
