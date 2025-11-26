import jsonschema
import itertools

MAX_RESOURCES = 30
MAX_VESSELS = 6
MAX_STAT = 10
STAT_SZ = 4

MSG_START = {
    "properties": {
        "type": {
            "const": "start"
            },
        "team": {
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
        "required": ["type", "id"],
        "additionalProperties": False
    }
}

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

validators = dict(map(
    lambda kv: (
        kv[0],
        jsonschema.validators.Draft202012Validator(kv[1])
    ),
    (
        ('start', MSG_START),
        ('connect', MSG_CONNECT),
        ('ping', MSG_PING),
        ('config_universe', MSG_CONFIG_UNIVERSE),
    )
))


def validate_msg(msg):
    t = msg.get('type', False)
    if not t:
        return ['Unknown type']
    if not isinstance(t, str) or t not in validators:
        return ['Invalid type']
    inval = list(map(
        lambda v: f'{v.json_path}: {v.message}',
        itertools.islice(validators[t].iter_errors(msg), 20)
    ))
    if len(inval) == 20:
        inval.append("…and more")
    if not inval:
        # Special cases not handled by jsonschema
        if t == 'start':
            if sum((sum(v) for v in msg.get('vessels'))) > MAX_RESOURCES:
                inval.append("$.vessels: too much resources allocated")
    return inval
