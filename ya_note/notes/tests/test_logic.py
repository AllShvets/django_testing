from .test_case_base import TestCaseBase

from notes.models import Note

from slugify import slugify


class TestLogic(TestCaseBase):
    def test_authenticated_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        self.client.force_login(self.author)
        initial_notes_count = self.get_notes_count()

        response = self.client.post(self.ADD_URL, data=self.FORM_DATA)

        self.assert_creation_success(response, initial_notes_count)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        Note.objects.all().delete()
        notes_count_init = Note.objects.count()
        response = self.client.post(self.ADD_URL, data=self.FORM_DATA)
        expected_url = f'{self.USERS_LOGIN_URL}?next={self.ADD_URL}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_init)

    def get_notes_count(self):
        """Возвращает текущее количество заметок."""
        return Note.objects.count()

    def assert_creation_success(self, response, initial_count):
        """Проверяет успешное создание заметки."""
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.latest('id')
        self.assert_note_matches_form_data(new_note)

    def assert_creation_failure(self, response, initial_count):
        """Проверяет, что заметка не была создана."""
        self.assertEqual(Note.objects.count(), initial_count)
        self.assertEqual(response.status_code, 403)

    def assert_note_matches_form_data(self, note):
        """Проверяет соответствие заметки данным формы."""
        self.assertEqual(note.title, self.FORM_DATA['title'])
        self.assertEqual(note.text, self.FORM_DATA['text'])
        self.assertEqual(note.slug, self.FORM_DATA['slug'])
        self.assertEqual(note.author, self.author)

    def test_create_note_without_slug(self):
        """
        Проверяет автоматическое создание slug
        при отсутствии его в данных заметки,
        используя функцию pytils.translit.slugify.
        """
        self.client.force_login(self.author)
        form_data_without_slug = self.FORM_DATA.copy()
        form_data_without_slug.pop('slug')
        Note.objects.all().delete()

        initial_notes_count = Note.objects.count()
        response = self.client.post(
            self.ADD_URL,
            data=form_data_without_slug
        )

        self.assertRedirects(response, self.SUCCESS_URL)
        new_notes_count = Note.objects.count()
        self.assertEqual(new_notes_count, initial_notes_count + 1)

        created_note = Note.objects.get()
        expected_slug = slugify(form_data_without_slug['title'])
        self.assertEqual(created_note.slug, expected_slug)

    def test_author_can_edit_note_correctly(self):
        """
        Проверяем, что автор может редактировать и удалять свои заметки,
        но не имеет доступа к редактированию или удалению чужих.
        """
        self.client.login(username=self.author.username, password='password')
        response = self.client.post(self.UPDATE_URL, data=self.FORM_DATA)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.SUCCESS_URL)

        self.note.refresh_from_db()

        for field in ['title', 'text', 'slug']:
            self.assertEqual(getattr(self.note, field), self.FORM_DATA[field])

    def test_author_can_delete_his_note(self):
        """
        Проверяем, что автор может удалять свои заметки,
        но не имеет права удалять заметки других пользователей.
        """
        self.client.login(username=self.author.username, password='password')
        initial_notes_count = Note.objects.count()

        response = self.client.post(self.DELETE_URL)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.SUCCESS_URL)

        updated_notes_count = Note.objects.count()
        self.assertEqual(initial_notes_count - 1, updated_notes_count)
