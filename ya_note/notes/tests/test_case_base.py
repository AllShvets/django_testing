from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestCaseBase(TestCase):
    HOME_URL = reverse('notes:home')
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')
    LIST_URL = reverse('notes:list')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')

    # Данные формы
    FORM_DATA = {
        'title': 'Заголовок',
        'text': 'Текст',
        'slug': 'Slug',
    }

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='Сторонний юзер')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(
            title=cls.FORM_DATA['title'],
            text=cls.FORM_DATA['text'],
            slug=cls.FORM_DATA['slug'],
            author=cls.author
        )

        cls.DETAIL_URL = reverse('notes:detail', args=(cls.note.slug,))
        cls.UPDATE_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))
