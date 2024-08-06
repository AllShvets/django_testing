from notes.forms import NoteForm
from .test_case_base import TestCaseBase


class TestContent(TestCaseBase):

    def test_user_note_visibility(self):
        """
        Проверяет видимость заметки для авторизованных и
        неавторизованных пользователей.
        """
        users_visibility = {
            self.author: True,
            self.not_author: False,
        }

        for user, expected_visibility in users_visibility.items():
            self.client.force_login(user)
            response = self.client.get(self.LIST_URL)
            object_list = response.context.get('object_list', [])
            is_note_visible = self.note in object_list

            self.assertEqual(is_note_visible, expected_visibility)

    def test_pages_contain_form(self):
        """
        Проверяет, что форма передается на страницы создания
        и редактирования заметки.
        """
        self.client.force_login(self.author)

        urls_to_test = [self.ADD_URL, self.UPDATE_URL]

        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                form = response.context.get('form')

                self.assertIn('form', response.context)
                self.assertIsInstance(form, NoteForm)
