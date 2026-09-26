from __future__ import annotations

from ansible.errors import AnsibleError
from ansible.galaxy.collection import _extract_tar_dir

class FakeTar:
    def __init__(self, members):
        self._members = set(members)
        self.SYMTYPE = object()  # sentinel, not used in this test
        self.name = 'fake.tar'
    def getmember(self, name):
        if name in self._members:
            class M:
                type = 0
                linkname = ''
            return M()
        raise KeyError(name)


def main():
    tar = FakeTar(members={'/some/dir'})
    try:
        _extract_tar_dir(tar, '/some/dir/', b'/tmp/dest')
    except AnsibleError as e:
        print('Caught:', str(e))
    else:
        print('ERROR: expected AnsibleError for missing member with trailing slash')

if __name__ == '__main__':
    main()
