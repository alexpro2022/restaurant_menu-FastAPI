def is_text(field):
    if field in ('', ' '):
        raise ValueError('Поле не может быть пустой строкой или пробелом!')
    if len(set(field)) < 2:
        raise ValueError(
            'Поле не может быть последовательностью одного символа!')
