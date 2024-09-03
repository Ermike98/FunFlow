from .tags import Tag, TAG_VALUE_SEPARATOR

TAG_SEPARATOR = ","


class Template:
    def __init__(self, template_str: str, *tags: Tag, **tag_values: str):
        name, *tag_strings = template_str.split(TAG_SEPARATOR)

        self.__name = name
        self.__tags = dict()

        for tag_str in tag_strings:
            tag = Tag(tag_str)
            assert tag.name not in self.__tags, f"Duplicate tag found: A tag with name '{tag.name}' already exists.!"
            self.__tags[tag.name] = tag

        for tag in tags:
            assert tag.name not in self.__tags, f"Duplicate tag found: A tag with name '{tag.name}' already exists.!"
            self.__tags[tag.name] = tag

        for tag_name, tag_value in tag_values.items():
            assert tag_name not in self.__tags, f"Duplicate tag found: A tag with name '{tag_name}' already exists.!"
            self.__tags[tag_name] = Tag(name=tag_value, value=tag_value)

    def match(self, template_str: str) -> bool:
        name, *tags = template_str.split(TAG_SEPARATOR)

        if name.strip() != self.__name:
            return False

        for tag_str in tags:
            tag_name = tag_str.split(TAG_VALUE_SEPARATOR)[0].strip()

            # Ignore the tags that are present in the string but are not in the tags list
            if tag_name not in self.__tags:
                continue

            # If the tag does not match then the template does not match
            if not self.__tags[tag_name].match(tag_str):
                return False

        return True

    def __str__(self):
        tags_str = (TAG_SEPARATOR + " ").join(map(str, self.__tags.values()))
        return (TAG_SEPARATOR + " ").join([self.__name, tags_str])

    def __repr__(self):
        tags_repr = ", ".join([f'"{tag_name}"= {repr(tag)}' for tag_name, tag in self.__tags.items()])
        return f"Template({self.__name}, {tags_repr})"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def tags(self) -> list[Tag]:
        return list(self.__tags.values())
