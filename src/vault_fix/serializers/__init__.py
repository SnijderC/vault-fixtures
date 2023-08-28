import enum


class _SerializerChoices(str, enum.Enum):
    json = "json"
    yaml = "yaml"


class _DeSerializerChoices(str, enum.Enum):
    json = "json"
    yaml = "yaml"
    auto = "auto"
