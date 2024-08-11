from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA_COMMENT = {'text': 'Текст комментария'}


def test_anonymous_user_cannot_post_comment(client, detail_page_news_url):
    """Проверяет, что анонимный пользователь не может оставить комментарий."""
    initial_count_comments = Comment.objects.count()
    form_data = FORM_DATA_COMMENT

    client.post(detail_page_news_url, data=form_data)

    count_comments = Comment.objects.count()
    assert count_comments == initial_count_comments


def test_auth_user_can_post_comment(
    authenticated_author_client,
    sample_author,
    test_news,
    detail_page_news_url
):
    """Проверяет, что авторизованный юзер может оставить комментарий."""
    initial_count_commit = Comment.objects.count()
    form_data = FORM_DATA_COMMENT

    response = authenticated_author_client.post(
        detail_page_news_url,
        data=form_data
    )

    assertRedirects(response, f'{detail_page_news_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == initial_count_commit + 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == test_news
    assert comment.author == sample_author


def test_user_cannot_submit_comments_with_prohibited_words(
    authenticated_author_client,
    detail_page_news_url
):
    """
    Проверяет, что попытка отправки комментария с запрещёнными словами
    приведёт к ошибке формы и не создаст новый комментарий.
    """
    comment_data = {
        'text': f'Текст комментария с {BAD_WORDS[0]} в нём.'
    }
    initial_comment_count = Comment.objects.count()

    response = authenticated_author_client.post(
        detail_page_news_url,
        data=comment_data
    )

    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )

    current_comment_count = Comment.objects.count()
    assert current_comment_count == initial_comment_count


def test_user_can_edit_own_comment(
    authenticated_author_client,
    sample_author,
    test_news,
    sample_comment,
    update_comment_url,
    detail_page_news_url
):
    """Проверяет, что пользователь может редактировать свой комментарий."""
    new_comment_text = 'Измененный текст комментария'
    update_data = {'text': new_comment_text}

    response = authenticated_author_client.post(
        update_comment_url,
        data=update_data
    )

    assertRedirects(response, f'{detail_page_news_url}#comments')

    sample_comment.refresh_from_db()
    assert sample_comment.text == new_comment_text


def test_author_can_delete_own_comment(
    authenticated_author_client,
    delete_comment_url,
    detail_page_news_url
):
    """Проверяет, что автор комментария может удалить свой комментарий."""
    initial_comment_count = Comment.objects.count()
    comments_url = detail_page_news_url + '#comments'

    response = authenticated_author_client.delete(delete_comment_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == comments_url
    assert Comment.objects.count() == initial_comment_count - 1

    comment_id = delete_comment_url.split('/')[-2]
    assert not Comment.objects.filter(id=comment_id).exists()


def test_user_cant_edit_comment_of_another_user(
    authenticated_not_author_client,
    sample_comment,
    update_comment_url
):
    """Проверяет, что юзер не может редактировать комментарий другого юзера."""
    new_comment_text = 'Измененный текст комментария'
    update_data = {'text': new_comment_text}
    original_comment_text = sample_comment.text

    authenticated_not_author_client.post(update_comment_url, data=update_data)
    sample_comment.refresh_from_db()

    assert sample_comment.text == original_comment_text


def test_user_cant_delete_comment_of_another_user(
    authenticated_not_author_client,
    delete_comment_url
):
    """Проверяет, что юзер не может удалить комментарий другого юзера."""
    comments_count_init = Comment.objects.count()

    authenticated_not_author_client.delete(delete_comment_url)

    comments_count = Comment.objects.count()
    assert comments_count == comments_count_init
