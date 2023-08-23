from vault_fix.type import NestedStrDict

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
