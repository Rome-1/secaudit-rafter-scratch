
import sys
from ansible.utils.unsafe_proxy import wrap_var, UnsafeProxy, AnsibleUnsafeText, AnsibleUnsafeBytes
from ansible.module_utils.common._collections_compat import Mapping, MutableSequence, Set

def test_wrap_var():
    # Test with binary_type
    binary_string = b'test'
    wrapped_binary = wrap_var(binary_string)
    assert isinstance(wrapped_binary, AnsibleUnsafeBytes), "Failed to wrap binary_type"

    # Test with text_type
    text_string = 'test'
    wrapped_text = wrap_var(text_string)
    assert isinstance(wrapped_text, AnsibleUnsafeText), "Failed to wrap text_type"

    # Test with existing AnsibleUnsafe object
    unsafe_text = AnsibleUnsafeText('unsafe')
    wrapped_unsafe = wrap_var(unsafe_text)
    assert wrapped_unsafe is unsafe_text, "Should not wrap existing AnsibleUnsafe object"

    print("test_wrap_var passed")

def test_unsafe_proxy_deprecation():
    # Test deprecation warning
    with open('deprecation_output.txt', 'w') as f:
        sys.stderr = f
        proxy = UnsafeProxy('test')
        sys.stderr = sys.__stderr__

    with open('deprecation_output.txt', 'r') as f:
        output = f.read()
        assert "UnsafeProxy is being removed" in output, "Deprecation warning not issued"

    # Test functionality
    assert isinstance(proxy, AnsibleUnsafeText), "UnsafeProxy did not wrap correctly"

    print("test_unsafe_proxy_deprecation passed")

def test_recursive_wrapping():
    # Test with Mapping
    mapping = {'key': 'value'}
    wrapped_mapping = wrap_var(mapping)
    assert isinstance(wrapped_mapping['key'], AnsibleUnsafeText), "Failed to wrap Mapping values"

    # Test with MutableSequence
    sequence = ['item1', 'item2']
    wrapped_sequence = wrap_var(sequence)
    assert isinstance(wrapped_sequence[0], AnsibleUnsafeText), "Failed to wrap MutableSequence values"

    # Test with Set
    set_obj = {'item1', 'item2'}
    wrapped_set = wrap_var(set_obj)
    for item in wrapped_set:
        assert isinstance(item, AnsibleUnsafeText), "Failed to wrap Set values"
        break

    print("test_recursive_wrapping passed")

if __name__ == '__main__':
    test_wrap_var()
    test_unsafe_proxy_deprecation()
    test_recursive_wrapping()
