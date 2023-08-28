import enum


class _SerializerChoices(enum.StrEnum):
    json = "json"
    yaml = "yaml"


class _DeSerializerChoices(enum.StrEnum):
    json = "json"
    yaml = "yaml"
    auto = "auto"
