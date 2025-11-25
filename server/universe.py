import collections
import weakref


class Universe:
    def __init__(self, size):
        self.objects = set()
        self.groups = collections.defaultdict(set)
        self.refs = collections.defaultdict(weakref.WeakSet)
        self.size = [10] * size

    def add(self, o, groups):
        for g in groups:
            self.refs[g].add(o)
            self.groups[o].add(g)
        self.objects.add(o)

    def remove(self, o, groups=None):
        if groups is None:
            groups = list(self.groups[o])
        for g in groups:
            self.refs[g].remove(o)
            if not self.refs[g]:
                self.refs.pop(g)
            self.groups[o].remove(g)
        if not self.groups[o]:
            self.groups.pop(o)
            self.objects.remove(o)

    def iter(self, group):
        if group in self.refs:
            for o in self.refs[group]:
                yield o
