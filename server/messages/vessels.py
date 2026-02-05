MSG_MOVE = {
    "properties": {
        "type": {
            "const": "move"
        },
        "direction": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {
                "type": "integer",
            }
        },
    },
    "required": ["type", "direction"],
    "additionalProperties": False
}

MSG_FIRE_TORPEDO = {
    "properties": {
        "type": {
            "const": "fire_torpedo"
        },
        "direction": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {
                "type": "number",
            }
        },
    },
    "required": ["type", "direction"],
    "additionalProperties": False
}

MSG_DROP_MINE = {
    "properties": {
        "type": {
            "const": "drop_mine"
        },
        "delay": {
            "type": "number",
        },
    },
    "required": ["type"],
    "additionalProperties": False
}

MSG_SCAN_RADAR = {
    "properties": {
        "type": {
            "const": "scan_radar"
        },
    },
    "required": ["type"],
    "additionalProperties": False
}

MSG_AUTODESTRUCTION = {
    "properties": {
        "type": {
            "const": "autodestruction"
        },
    },
    "required": ["type"],
    "additionalProperties": False
}
