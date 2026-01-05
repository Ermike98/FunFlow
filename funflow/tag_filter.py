from abc import ABC, abstractmethod
from .tags import Tag, TAG_VALUE_SEPARATOR, get_tag_name


class TagFilter(ABC):
    """
    Abstract base class for tag filters used in Templates to match input/output variables.
    """

    def __init__(self, name: str):
        """
        Initialize a TagFilter.

        :param name: The name of the tag this filter applies to.
        """
        self._name = name.strip()

    def match(self, tag: str | Tag):
        """
        Check if the provided tag matches this filter.

        :param tag: A Tag object or a string representation of a tag.
        :return: True if the tag matches, False otherwise.
        """
        if isinstance(tag, str):
            tag = Tag(tag)

        return self._match(tag)

    @abstractmethod
    def _match(self, tag: Tag) -> bool:
        """Internal match implementation."""
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
    """
    Filter that matches any tag name regardless of its value.
    In string representation, it looks like 'tag_name: {}'.
    """

    def __init__(self, name: str):
        super().__init__(name)

    def _match(self, tag: Tag) -> bool:
        return tag.name == self._name

    def __repr__(self):
        return f"NoTagFilter({self._name})"

    def __str__(self):
        return TAG_VALUE_SEPARATOR.join([self._name, "{}"])


class ValueTagFilter(TagFilter):
    """
    Filter that matches a tag name with a specific value.
    In string representation, it looks like 'tag_name: {value}'.
    """

    def __init__(self, name: str, value: str):
        super().__init__(name)
        self.__value = value

    def _match(self, tag: str | Tag) -> bool:
        return tag.name == self._name and tag.value == self.__value

    def __repr__(self):
        return f"ValueTagFilter({self._name}, {self.__value})"

    def __str__(self):
        return TAG_VALUE_SEPARATOR.join([self._name, "{" + self.__value + "}"])
