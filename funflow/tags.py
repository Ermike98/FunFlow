import warnings

TAG_VALUE_SEPARATOR = ":"


class Tag:
    def __init__(self, tag_str: str = None, name: str = None, value: str | None = None):
        if name is None and value is None:
            assert tag_str is not None, "At least one between tag_str and (name, value) must be not None!"

            if TAG_VALUE_SEPARATOR in tag_str:
                name, value = tag_str.split(TAG_VALUE_SEPARATOR)
            else:
                name = tag_str

        elif tag_str is not None and name is None:
            warnings.warn(
                f"Both 'tag_str' and 'name={name}' were provided. "
                f"'tag_str', and 'name' will be used instead.",
                UserWarning
            )

            # name, value = tag_str.split(TAG_VALUE_SEPARATOR)
        if isinstance(value, str):
            value = value.strip()

        self.__name = name.strip()
        self.__value = value

    def match(self, tag_str):
        # if TAG_VALUE_SEPARATOR not in tag_str:
        #     name = tag_str.strip()
        #     value = None
        # else:
        #     name, value = tag_str.split(TAG_VALUE_SEPARATOR)
        #     name = name.strip()
        #     value = value.strip()
        #
        # match name, value:
        #     case (self.name, self.value):
        #         return True
        #     case (self.name, None):
        #         return self.value is None
        #     case _:
        #         return False

        # tag_str does not contain a value
        if TAG_VALUE_SEPARATOR not in tag_str:
            # match if the name is the same and the tag value is missing
            return tag_str.strip() == self.__name and self.__value is None

        name, value = tag_str.split(TAG_VALUE_SEPARATOR)

        return name.strip() == self.__name and (value.strip() == self.__value or self.__value is None)

    def __str__(self):
        if self.__value is None:
            return self.__name
        return (TAG_VALUE_SEPARATOR + " ").join([self.__name, self.__value])

    def __repr__(self):
        return f'Tag("{self.__name}", "{self.__value}")'

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> str:
        return self.__value