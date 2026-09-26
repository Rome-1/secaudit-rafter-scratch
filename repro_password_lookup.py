from ansible.plugins.lookup.password import LookupModule

class DummyLoader:
    def path_dwim(self, path):
        return path

if __name__ == '__main__':
    lm = LookupModule(loader=DummyLoader())
    # Mimic loader setting plugin load name like Ansible would
    lm._load_name = 'password'

    terms = ['/dev/null seed=myseed']
    out1 = lm.run(terms, variables={})
    out2 = lm.run(terms, variables={})
    print('Test1 same-seed deterministic:', out1, out2, 'equal?', out1 == out2)

    # Different seed should produce different value
    out3 = lm.run(['/dev/null seed=otherseed'], variables={})
    print('Test1 different seed different?', out1 != out3)

    # Test chars as comma-separated string with literal comma
    out4 = lm.run(["/dev/null length=8 chars=digits,,._"], variables={})
    print('Test2 chars with literal comma:', out4)

    # Test chars provided as list via plugin options (kwargs) plus seed as default
    out5 = lm.run(['/dev/null'], variables={}, chars=['digits', 'abcdef'], seed='SAME')
    out6 = lm.run(['/dev/null'], variables={}, chars=['digits', 'abcdef'], seed='SAME')
    print('Test3 chars list via kwargs deterministic with seed option:', out5, out6, 'equal?', out5 == out6)

