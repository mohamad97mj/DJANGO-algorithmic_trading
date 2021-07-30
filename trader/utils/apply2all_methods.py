def apply2all_methods(*decorators):
    def decorate(cls):
        for decorator in decorators:
            for attr in cls.__dict__:
                if callable(getattr(cls, attr)):
                    setattr(cls, attr, decorator(getattr(cls, attr)))
            return cls

    return decorate
