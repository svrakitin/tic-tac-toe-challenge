from functools import singledispatch, update_wrapper


def instance_method_dispatch(func):
    dispatcher = singledispatch(func)

    def wrapper(*args, **kwargs):
        return dispatcher.dispatch(args[1].__class__)(*args, **kwargs)

    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper
