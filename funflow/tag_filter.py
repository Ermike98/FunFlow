from abc import ABC, abstractmethod
from .tags import Tag, TAG_VALUE_SEPARATOR, get_tag_name


class TagFilter(ABC):
    def __init__(self, name: str):
        self._name = name.strip()

    def match(self, tag: str | Tag):
        if isinstance(tag, str):
            tag = Tag(tag)

        return self._match(tag)

    @abstractmethod
    def _match(self, tag: Tag) -> bool:
        pass

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass


class NoTagFilter(TagFilter):
    def __init__(self, name: str):
        super().__init__(name)

    def _match(self, tag: Tag) -> bool:
        return tag.name == self._name

    def __repr__(self):
        return f"NoTagFilter({self._name})"

    def __str__(self):
        return TAG_VALUE_SEPARATOR.join([self._name, "{}"])


class ValueTagFilter(TagFilter):
    def __init__(self, name: str, value: str):
        super().__init__(name)
        self.__value = value

    def _match(self, tag: str | Tag) -> bool:
        return tag.name == self._name and tag.value == self.__value

    def __repr__(self):
        return f"ValueTagFilter({self._name}, {self.__value})"

    def __str__(self):
        return TAG_VALUE_SEPARATOR.join([self._name, "{" + self.__value + "}"])
