MSG_RQ_WORLD_REPORT = {
    "properties": {
        "type": {
            "const": "rq_world_report"
        },
        "key": {
            "type": "string",
        },
        "dt": {
            "type": "number"
        },
        "universe": {
            "type": "string",
        }
    },
    "required": ["type", "universe"],
    "additionalProperties": False
}

MSG_CONFIG_UNIVERSE = {
    "properties": {
        "type": {
            "const": "config_universe"
        },
        "key": {
            "type": "string",
        },
        "size": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {
                "type": "integer",
                "minimum": 0,
            }
        }
    },
    "required": ["type", "size"],
    "additionalProperties": False
}
