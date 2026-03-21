import jsonschema
import itertools

from .admin import (
    MSG_RQ_WORLD_REPORT,
    MSG_CONFIG_UNIVERSE,
    MSG_TOURNAMENT,
)
from .game import (
    MSG_START,
    MSG_CONNECT,
)
from .vessels import (
    MSG_MOVE,
    MSG_FIRE_TORPEDO,
    MSG_DROP_MINE,
    MSG_FIRE_LASER,
    MSG_FIRE_IEM,
    MSG_SCAN_RADAR,
    MSG_AUTODESTRUCTION,
)
from .misc import (
    MSG_PING,
)

MAX_RESOURCES = 30

validators = dict(map(
    lambda kv: (
        kv[0],
        jsonschema.validators.Draft202012Validator(kv[1])
    ),
    (
        ('start', MSG_START),
        ('connect', MSG_CONNECT),
        ('move', MSG_MOVE),
        ('fire_torpedo', MSG_FIRE_TORPEDO),
        ('drop_mine', MSG_DROP_MINE),
        ('fire_laser', MSG_FIRE_LASER),
        ('fire_iem', MSG_FIRE_IEM),
        ('scan_radar', MSG_SCAN_RADAR),
        ('autodestruction', MSG_AUTODESTRUCTION),
        ('ping', MSG_PING),
        ('rq_world_report', MSG_RQ_WORLD_REPORT),
        ('config_universe', MSG_CONFIG_UNIVERSE),
        ('tournament', MSG_TOURNAMENT),
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
