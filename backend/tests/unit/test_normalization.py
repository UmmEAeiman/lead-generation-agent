from app.utils.normalization import normalize_domain, normalize_email, normalize_url


def test_normalize_domain_from_url() -> None:
    assert normalize_domain("https://www.Acme-Corp.com/about") == "acme-corp.com"


def test_normalize_domain_from_bare_domain() -> None:
    assert normalize_domain("example.org") == "example.org"


def test_normalize_domain_empty() -> None:
    assert normalize_domain(None) is None
    assert normalize_domain("   ") is None


def test_normalize_email() -> None:
    assert normalize_email("  User@Example.COM ") == "user@example.com"
    assert normalize_email("not-an-email") is None
    assert normalize_email(None) is None


def test_normalize_url_adds_scheme() -> None:
    assert normalize_url("example.com/page") == "https://example.com/page"
    assert normalize_url("http://example.com") == "http://example.com"
    assert normalize_url(None) is None
