import warnings

TAG_VALUE_SEPARATOR = ":"


def get_tag_name(tag_str: str):
    if TAG_VALUE_SEPARATOR not in tag_str:
        return tag_str.strip()

    return tag_str.split(TAG_VALUE_SEPARATOR)[0].strip()


class Tag:
    def __init__(self, name: str = None, value: str = None):
        if value is None:
            assert TAG_VALUE_SEPARATOR in name, "At least one between name and value must contain the Tag value!"

            name, value = name.split(TAG_VALUE_SEPARATOR)
        # elif tag_str is not None and name is not None or value is not None:
        #     warnings.warn(
        #         f"Both 'tag_str'={tag_str} and 'name'={name}, 'value'={value} were provided. "
        #         f"'name' and 'value' will be used instead.",
        #         UserWarning
        #     )

        self.__name = name.strip()
        self.__value = value.strip()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> str:
        return self.__value

    def __str__(self):
        return (TAG_VALUE_SEPARATOR + " ").join([self.__name, self.__value])

    def __repr__(self):
        return f'Tag("{self.__name}", "{self.__value}")'

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, str):
            other = Tag(other)

        return str(self) == str(other)

