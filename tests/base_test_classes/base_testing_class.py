class BaseTestingClass:
    model = None
    model_attributes: tuple[str] | None = None
    factory = None
    batch_size: int = 99

    class Meta:
        abstract = True

    def _build(self, size=1, **kwargs):
        return (self.factory.build_batch(size, **kwargs)
                if size > 1 else self.factory.build(**kwargs))

    def _create(self, size=1, **kwargs):
        assert self.model.objects.count() == 0
        created = (self.factory.create_batch(size, **kwargs)
                   if size > 1 else self.factory(**kwargs))
        assert self.model.objects.count() == size
        return created

    def _to_dict(self, obj) -> dict:
        d = {}
        for field in obj._meta.fields:
            if field.name != 'id':
                d[field.name] = getattr(obj, field.name)
        return d

    def _any_is_none(self, *attrs) -> bool:
        return True if None in attrs else False
