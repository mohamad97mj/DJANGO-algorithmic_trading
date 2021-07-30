from django.utils.encoding import smart_str


def my_key_maker(key, key_prefix, version):
    new_key = smart_str(''.join([c for c in key if ord(c) > 32 and ord(c) != 127]))
    return new_key
