from ansible.utils.unsafe_proxy import wrap_var, AnsibleUnsafe, AnsibleUnsafeText, AnsibleUnsafeBytes

# Test data
unsafe_str = AnsibleUnsafeText("unsafe text")
binary_data = b'some binary data'
text_data = "some text data"
list_data = [binary_data, text_data]
dict_data = {'key1': binary_data, 'key2': text_data}
set_data = {binary_data, text_data}

# Wrap function tests
def test_wrap_var():
    assert wrap_var(unsafe_str) is unsafe_str, "Failed to return AnsibleUnsafe input unchanged"
    assert isinstance(wrap_var(binary_data), AnsibleUnsafeBytes), "Failed to wrap binary data"
    assert isinstance(wrap_var(text_data), AnsibleUnsafeText), "Failed to wrap text data"
    wrapped_list = wrap_var(list_data)
    assert isinstance(wrapped_list[0], AnsibleUnsafeBytes), "Failed to wrap list binary element"
    assert isinstance(wrapped_list[1], AnsibleUnsafeText), "Failed to wrap list text element"
    wrapped_dict = wrap_var(dict_data)
    assert isinstance(wrapped_dict['key1'], AnsibleUnsafeBytes), "Failed to wrap dict binary element"
    assert isinstance(wrapped_dict['key2'], AnsibleUnsafeText), "Failed to wrap dict text element"
    wrapped_set = wrap_var(set_data)
    for item in wrapped_set:
        assert isinstance(item, (AnsibleUnsafeBytes, AnsibleUnsafeText)), "Failed to wrap set elements"

    print("All wrap_var tests passed.")

if __name__ == "__main__":
    test_wrap_var()
