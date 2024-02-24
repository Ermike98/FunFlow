def rename_names(_names: list[str],
                 _map: dict[str, str]) -> list[str]:
    return [name if name not in _map else _map[name] for name in _names]


def rename_dict_keys(_dict: dict,
                     _map: dict[str, str]) -> dict:
    new_dict = dict()

    for key, value in _dict.items():
        if key in _map:
            new_dict[_map[key]] = value
        else:
            new_dict[key] = value

    return new_dict


def set_cross_difference(expected_values, actual_values):
    expected_set = set(expected_values)
    actual_set = set(actual_values)
    expected_but_not_received = expected_set.difference(actual_set)
    received_but_not_expected = actual_set.difference(expected_set)
    return expected_but_not_received, received_but_not_expected


def check_expected_vs_actual_names(expected_names, actual_names, object_name="", debug=False):
    expected_but_not_received, received_but_not_expected = set_cross_difference(expected_names,
                                                                                actual_names)
    if debug:
        print(f'object_name: "{object_name}";', end=' ')
        print(f'expected_names: {set(expected_names)}, actual_names: {set(actual_names)}; ', end=' ')
        print(
            f'expected_but_not_received: {set(expected_but_not_received)}, received_but_not_expected: {set(received_but_not_expected)}')

    if expected_but_not_received:
        raise Exception(
            (f'Expected{" " + object_name}: {set(expected_names)}; got {set(actual_names)} instead!\n' +
             f'{object_name.title()} {expected_but_not_received} are missing!'))

    if received_but_not_expected and debug:
        print(f"Warning: the following {object_name + ' '}were not expected: {received_but_not_expected}")


def concat_list_without_duplicates(l1: list, l2: list, object_name="") -> list:
    concat_list = l1 + l2
    if len(object_name) > 0:
        object_name = ' as ' + object_name + ' variables'
    if len(set(concat_list)) != len(concat_list):
        intersection_set = set(l1).intersection(l2)
        raise Exception(f"The variables {intersection_set} have already been used{object_name}!")

    return concat_list


def overlapping_keys_in_dicts(d1: dict, d2: dict):
    return set(d1.keys()).intersection(d2.keys())
