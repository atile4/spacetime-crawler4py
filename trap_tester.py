import scraper
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

def test_junk_parameters_blocked():
    assert pf.is_trap("https://t2.ics.uci.edu/doc?do=edit") is True
    assert pf.is_trap("https://t2.ics.uci.edu/p?PHPSESSID=abc") is True


def test_template_limit_cuts_off_calendar():
    urls = [f"https://cal.ics.uci.edu/events/2026-10-{i:03d}" for i in range(305)]
    results = [pf.is_trap(u) for u in urls]
    assert not any(results[:300])
    assert all(results[300:])


def test_repeat_sightings_do_not_inflate_count():
    for _ in range(1000):
        pf.is_trap("https://t2.ics.uci.edu/news/12")
    assert pf.is_trap("https://t2.ics.uci.edu/news/12") is False


def test_normal_page_still_valid():
    assert scraper.is_valid("https://www.ics.uci.edu/about") is True


def test_other_domains_and_files_still_rejected():
    assert scraper.is_valid("https://www.google.com/") is False
    assert scraper.is_valid("https://www.ics.uci.edu/paper.pdf") is False


def test_traps_rejected():
    assert scraper.is_valid("https://h3.ics.uci.edu/a/b/a/b/a/b") is False
    assert scraper.is_valid("https://h3.ics.uci.edu/wiki?do=edit") is False


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
