def my_copy(obj1, obj2):
    keys = vars(obj1).keys()
    for k in keys:
        setattr(obj2, k, getattr(obj1, k))
