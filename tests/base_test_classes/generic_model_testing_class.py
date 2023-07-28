import pytest
from django.db import IntegrityError

from .base_testing_class import BaseTestingClass


class GenericModelTests(BaseTestingClass):
    ordering: tuple[str, ...] | None = None
    verbose_name: str | None = None
    verbose_name_plural: str | None = None
    fields: tuple[str, ...] | None = None
    fields_verbose_names: tuple[str, ...] | None = None
    fields_help_text: tuple[str, ...] | None = None
    str_method_text_pattern: str | None = None
    str_method_fields: tuple[str, ...] | None = None
    unique_test: bool = True

    class Meta:
        abstract = True

    @pytest.mark.django_db
    def test_create(self):
        """Проверяем, что модель корректно создается."""
        assert self._create() == self.model.objects.get(id=1)

    @pytest.mark.django_db
    def test_uniqueness(self):
        """Проверяем, что не может быть создано двух и
           более идентичных записей в БД."""
        if not self.unique_test:
            pytest.skip('unique_test is False')
        created = self._create()
        with pytest.raises(IntegrityError):
            self.model.objects.create(**self._to_dict(created))

    @pytest.mark.django_db
    def test_ordering(self):
        """Проверяем, что у модели корректно работает order_by."""
        if self.ordering is None:
            pytest.skip('ordering is None')
        order_by_attr = self.ordering[0]
        if order_by_attr.startswith('-'):
            reverse = True
            order_by_attr = order_by_attr[1:]
        else:
            reverse = False
        objs = self._create(self.batch_size)
        expected_ordered_by = list(self.model.objects.all())
        assert expected_ordered_by == \
            sorted(objs,
                   key=lambda obj: getattr(obj, order_by_attr),
                   reverse=reverse)

    def test_verbose_names(self):
        """Проверяем, что verbose_name моделей совпадает с ожидаемым."""
        if self.verbose_name is None and self.verbose_name_plural is None:
            pytest.skip('both verbose_name and verbose_name_plural are None')
        if self.verbose_name is not None:
            assert self.model._meta.verbose_name == self.verbose_name
        if self.verbose_name_plural is not None:
            assert self.model._meta.verbose_name_plural == \
                self.verbose_name_plural

    def test_fields_verbose_names(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        if self._any_is_none(self.fields, self.fields_verbose_names):
            pytest.skip('fields or fields_verbose_names is None')
        for field, expected_value in dict(
            zip(self.fields, self.fields_verbose_names)
        ).items():
            actual_value = self.model._meta.get_field(field).verbose_name
            assert actual_value == expected_value, \
                f'{actual_value} != {expected_value}'

    def test_fields_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        if self._any_is_none(self.fields, self.fields_help_text):
            pytest.skip('fields or fields_help_text is None')
        for field, expected_value in dict(
            zip(self.fields, self.fields_help_text)
        ).items():
            actual_value = self.model._meta.get_field(field).help_text
            assert actual_value == expected_value, \
                f'{actual_value} != {expected_value}'

    def test_str_method(self):
        """Проверяем, что у модели корректно работает __str__."""
        if self._any_is_none(
            self.str_method_text_pattern, self.str_method_fields
        ):
            pytest.skip('str_method_text_pattern or str_method_fields is None')
        obj = self._build()
        values = [getattr(obj, field) for field in self.str_method_fields]
        assert str(obj) == self.str_method_text_pattern.format(*values)
