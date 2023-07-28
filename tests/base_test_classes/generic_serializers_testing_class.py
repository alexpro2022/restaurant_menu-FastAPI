import pytest

from .base_testing_class import BaseTestingClass


class GenericSerializerTests(BaseTestingClass):
    serializer = None
    invalid_factory = None
    fields: tuple[str] | None = None
    read_only_fields: tuple[str] | None = None
    write_only_fields: tuple[str] | None = None
    valid_values: tuple[str] | None = None
    invalid_values: tuple[str] | None = None
    expected_serialization: dict | None = None
    nested_data: bool = False

    class Meta:
        abstract = True

    def _get_valid_data(self):
        return (
            self._to_dict(self._build()) if self.valid_values is None
            else dict(zip(self.fields, self.valid_values)))

    @pytest.mark.django_db
    def test_serialize_valid_model(self):
        valid_model = self.factory()
        serializer = self.serializer(valid_model)
        assert serializer.data
        fields_out = (
            tuple(set(self.fields) - set(self.write_only_fields))
            if self.write_only_fields is not None else self.fields)
        for field in fields_out:
            # преобразуем в str числовые форматы для корректного сравнения
            # отсекаем лишние нули справа в данных модели
            data_value = str(serializer.data[field])
            model_value = str(getattr(valid_model, field))[:len(data_value)]
            assert str(data_value) == model_value, f'{data_value} != {model_value}'

    def test_serialize_invalid_model(self):
        invalid_model = self.invalid_factory.build()
        serializer = self.serializer(invalid_model)
        with pytest.raises(AttributeError):
            serializer.data

    @pytest.mark.django_db
    def test_deserialize_valid_data(self):
        valid_data = self._get_valid_data()
        # if self.nested_data:
        serializer = self.serializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.errors == {}

    @pytest.mark.django_db
    def test_deserialize_invalid_data(self):
        if self.valid_values is None:
            pytest.skip(reason='No valid_values provided')
        if self.invalid_values is None:
            pytest.skip(reason='No invalid_values provided')
        for index, field in enumerate(self.fields):
            invalid_data = dict(zip(self.fields, self.valid_values))
            invalid_data[field] = self.invalid_values[index]
            serializer = self.serializer(data=invalid_data)
            assert not serializer.is_valid(), serializer.validated_data
            assert serializer.errors != {}
