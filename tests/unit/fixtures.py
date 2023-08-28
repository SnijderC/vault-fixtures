from vault_fix._type import NestedStrDict
from vault_fix.serializers.json import json_serializer
from vault_fix.serializers.yaml import yaml_serializer

PASSWORD = "hunter2"
SECRET_MESSAGE = "Some day this will be replaced by my lattice-based crypto"
ENCRYPTED_SECRET_MESSAGE = (
    "AgCBEAEAAABTU1NTU1NTU1NTU1NTU1NTTk5OTk5OTk5OTk5OFEwDr/XfJIqIcrX6qrFIS/Kmgf"
    "KRMfYpJhtGLjCIT6YwKY4RRMrvT93JqJ0qb9mBkpWlGyeAi7pBB64RvbYg/584d+fgkNEvtQ=="
)
DUMPED_DATA_PLAIN: NestedStrDict = {
    "10-things-they-dont-want-you-to-know/": {
        "advertisement/": {"annoying-popup-secret": {"pop-up-secret": "close-button-doesnt-work"}},
        "something-you-already-know/": {"secret-things-you-already-know": {"you-know-this": "click-bait-is-lame"}},
    }
}
DUMPED_DATA_ENCRYPTED: NestedStrDict = {
    "10-things-they-dont-want-you-to-know/": {
        "advertisement/": {
            "annoying-popup-secret": (
                "encrypted//AgCBEADiBABTU1NTU1NTU1NTU1NTU1NTTk5OTk5OTk5OTk5OkGqg20Csh9zRs0iFnFmRDDH/gkBbWnbnD0bfYUd9YP2"
                "e1yjW4oPbYxnCFSGVKum9P5aYLdEUtpQ6WfJpOQ=="
            )
        },
        "something-you-already-know/": {
            "secret-things-you-already-know": (
                "encrypted//AgCBEADiBABTU1NTU1NTU1NTU1NTU1NTTk5OTk5OTk5OTk5OkGqp20WsmcKTtwCShlWWDDH/gkBbXGbpD0bLfEc/Z6P"
                "X1CzI6dWLxlFRmNI3tJLsziKYqo+hfA=="
            )
        },
    }
}


JSON_DUMPED_PLAIN = json_serializer(DUMPED_DATA_PLAIN)
YAML_DUMPED_PLAIN = yaml_serializer(DUMPED_DATA_PLAIN)
JSON_DUMPED_ENCRYPTED = json_serializer(DUMPED_DATA_ENCRYPTED)
YAML_DUMPED_ENCRYPTED = yaml_serializer(DUMPED_DATA_ENCRYPTED)
