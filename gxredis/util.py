def is_key_matured(key, key_params):
    """ key_params provides full information for key or not """
    try:
        key.format(**key_params)
    except KeyError:
        return False
    else:
        return True
