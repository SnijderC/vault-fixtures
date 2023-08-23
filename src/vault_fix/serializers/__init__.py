import enum


class SerializerChoices(enum.StrEnum):
    json = "json"
    yaml = "yaml"


class DeSerializerChoices(enum.StrEnum):
    json = "json"
    yaml = "yaml"
    auto = "auto"
