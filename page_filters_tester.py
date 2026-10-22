import page_filters as pf


def test_normal_url_allowed():
    assert pf.is_trap("https://www.ics.uci.edu/about/people") is False


def test_repeating_path_blocked():
    assert pf.is_trap("https://t1.ics.uci.edu/a/b/a/b/a/b/c") is True
    assert pf.is_trap("https://t1.ics.uci.edu/x/x/x") is True
    assert pf.is_trap("https://t1.ics.uci.edu/x/x") is False


def test_deep_long_and_many_params_blocked():
    deep = "https://t1.ics.uci.edu/" + "/".join(f"d{i}" for i in range(12))
    assert pf.is_trap(deep) is True
    assert pf.is_trap("https://t1.ics.uci.edu/" + "a" * 250) is True
    assert pf.is_trap("https://t1.ics.uci.edu/p?a=1&b=2&c=3&d=4&e=5") is True
    assert pf.is_trap("https://t1.ics.uci.edu/p?a=1&b=2") is False


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)