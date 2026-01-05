import warnings

from .tags import Tag, get_tag_name
from .tag_filter import TagFilter
from collections import Counter

TAG_SEPARATOR = ","


def find_duplicate_tags(tags: list[Tag]) -> list[str]:
    if not tags:
        return []

    # Find if there are multiple values associated to the same tag name
    counter = Counter([tag.name for tag in tags])
    if counter.most_common()[0][1]:
        duplicate_elements = list(map(lambda x: x[0], filter(lambda x: x[1] > 1, counter.most_common())))

        return duplicate_elements

    return []


class TemplateValue:
    """
    Represents an instantiated input/output variable name with its associated tags.
    (e.g., 'data, version: 1, type: raw')
    """

    def __init__(self, name: str, tags: list[Tag] = None):
        """
        Initialize a TemplateValue.

        :param name: The base name of the variable.
        :param tags: A list of Tag objects associated with this variable.
        """
        if tags is None:
            name, *tag_strings = name.split(TAG_SEPARATOR)
            tags = map(Tag, tag_strings)

        self.__name = name.strip()

        tags = list(set(tags))  # Use the set to remove duplicate tags
        duplicate_tags = find_duplicate_tags(tags)
        if duplicate_tags:
            raise ValueError(f"Multiple values for the same tag found: {duplicate_tags}.")
        self.__tags = sorted(tags, key=lambda x: x.name)

    @property
    def name(self) -> str:
        """The base name of the variable."""
        return self.__name

    @property
    def tags(self) -> list[Tag]:
        """A sorted list of Tag objects."""
        return list(self.__tags)

    def __str__(self):
        substrings = [self.name]

        if self.__tags:
            tags_str = (TAG_SEPARATOR + " ").join(map(str, self.__tags))
            substrings.append(tags_str)

        return (TAG_SEPARATOR + " ").join(substrings)

    def __repr__(self):
        tags_repr = ", ".join([f'"{tag.name}"= {repr(tag)}' for tag in self.__tags])
        return f'TemplateValue("{self.__name}", [{tags_repr}])'

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, str):
            other = TemplateValue(other)

        return str(self) == str(other)

    def to_dict(self, include_name: bool = True):
        """
        Convert the TemplateValue to a dictionary mapping tag names to values.
        
        :param include_name: Whether to include the base name in the dictionary.
        :return: A dictionary representation.
        """
        d = dict(map(lambda x: (x.name, x.value), self.__tags))
        if include_name:
            d["name"] = self.__name

        return d

class Template:
    """
    Represents a pattern for matching and instantiating TemplateValues.
    Used by Layers to specify dynamic inputs and outputs.
    """

    def __init__(self, name: str,
                 tags: list[Tag] = None,
                 filters: list[TagFilter] = None):
        """
        Initialize a Template.

        :param name: The base name to match.
        :param tags: Static tags that will be added upon instantiation.
        :param filters: Tag filters to matches against available input/output variables.
        """
        name, *tag_strings = name.split(TAG_SEPARATOR)
        self.__name = name.strip()

        if tags is None:
            tags = []

        tags += list(set(map(Tag, tag_strings)))

        duplicate_tags = find_duplicate_tags(tags)
        if duplicate_tags:
            raise ValueError(f"Duplicate tag found: the tags {duplicate_tags} appear more than once in the list.")

        self.__tags = {tag.name: tag for tag in tags}

        if filters is None:
            filters = []

        # duplicate_tag_filters = find_duplicate_tags([tag_filter.name for tag_filter in filters])
        # if duplicate_tags:
        #     raise ValueError(f"Multiple filter for the same tag found: "
        #                      f"the tags {duplicate_tags} appear more than once in the list.")

        self.__tag_filters = {tag_filter.name: tag_filter for tag_filter in filters}

    def match(self, templ_value: str | TemplateValue) -> bool:
        """
        Check if a TemplateValue (or its string representation) matches this pattern.

        :param templ_value: The value to check.
        :return: True if base name matches and all filters pass.
        """
        if isinstance(templ_value, str):
            name, *tags = templ_value.split(TAG_SEPARATOR)
        else:  # isinstance(templ_value, TemplateValue)
            name = templ_value.name
            tags = templ_value.tags

        return name.strip() == self.__name and self.match_tags(tags)

    def match_tags(self, tags: list[Tag | str]) -> bool:
        """
        Check if a set of tags satisfies all the filters in this template.

        :param tags: The tags to check.
        :return: True if all filters find a match, False otherwise.
        """
        for tag_filter in self.tag_filters:
            if not any(map(tag_filter.match, tags)):
                return False

        # for tag in tags:
        #     if isinstance(tag, str):
        #         tag = Tag(tag)
        #
        #     tag_name = tag.name
        #
        #     # Ignore the tags that are present in the string but are not in the tag filters list
        #     if tag_name not in self.__tag_filters:
        #         continue
        #
        #     # If the tag does not match then the tag filter does not match
        #     if not self.__tag_filters[tag_name].match(tag):
        #         return False

        return True

    def instantiate(self, tags: list[Tag | str]) -> TemplateValue | None:
        """
        Create a TemplateValue by merging these template's static tags 
        with the provided tags, if they satisfy the filters.

        :param tags: Dynamic tags from the state context.
        :return: A TemplateValue if it matches filters, or None.
        """
        instantiated_tags = []
        for tag in tags:
            if isinstance(tag, str):
                tag = Tag(tag)

            if tag.name in self.__tags:
                if tag.name in self.__tag_filters:
                    raise ValueError(f"Duplicate tag found: tag {tag.name} found both in tags and tag_filters.")
                else:
                    warnings.warn(
                        f"Tag '{tag.name}' is already present in tags. "
                        f"The tag {tag}' will be overwritten with '{self.__tags[tag.name]}'.",
                        UserWarning
                    )
                    continue

            if tag.name in self.__tag_filters and not self.__tag_filters[tag.name].match(tag):
                return None

            instantiated_tags.append(tag)

        if find_duplicate_tags(list(set(instantiated_tags))):
            return None

        return TemplateValue(self.__name, self.tags + instantiated_tags)

    def __str__(self):
        substrings = [self.__name]

        if self.__tags:
            tags_str = (TAG_SEPARATOR + " ").join(map(str, self.__tags.values()))
            substrings.append(tags_str)

        if self.__tag_filters:
            tag_filter_str = (TAG_SEPARATOR + " ").join(map(str, self.__tag_filters.values()))
            substrings.append(tag_filter_str)

        return (TAG_SEPARATOR + " ").join(substrings)

    def __repr__(self):
        tags_repr = ", ".join([f'"{tag_name}"= {repr(tag)}' for tag_name, tag in self.__tags.items()])
        # tag_filters_repr = ", ".join([f'"{tag_name}"= {repr(tag_filter)}'
        #                               for tag_name, tag_filter in self.__tag_filters.items()])
        return f'Template("{self.__name}", [{tags_repr}], [...filters...])'

    @property
    def name(self) -> str:
        """The base name of the template."""
        return self.__name

    @property
    def tags(self) -> list[Tag]:
        """A list of static tags."""
        return list(self.__tags.values())

    @property
    def tag_filters(self) -> list[TagFilter]:
        """A list of tag filters."""
        return list(self.__tag_filters.values())

