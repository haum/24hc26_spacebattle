MAX_VESSELS = 6
MAX_STAT = 9
STAT_SZ = 4

MSG_START = {
    "properties": {
        "type": {
            "const": "start"
        },
        "team": {
            "type": "string"
        },
        "key": {
            "type": "string"
        },
        "vessels": {
            "type": "array",
            "minItems": 1,
            "maxItems": MAX_VESSELS,
            "items": {
                "type": "array",
                "minItems": STAT_SZ,
                "maxItems": STAT_SZ,
                "items": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": MAX_STAT
                    }
                }
            }
        },
    "required": ["type", "team", "vessels"],
    "additionalProperties": False
}

MSG_CONNECT = {
    "properties": {
        "type": {
            "const": "connect"
        },
        "id": {
            "type": "string"
        },
        "key": {
            "type": "string"
        },
        "required": ["type", "id"],
        "additionalProperties": False
    }
}
