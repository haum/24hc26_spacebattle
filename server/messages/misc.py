MSG_PING = {
    "properties": {
        "type": {
            "const": "ping"
        },
        "n": {
            "type": ["string", "number"]
        }
    },
    "required": ["type"],
    "additionalProperties": False
}
