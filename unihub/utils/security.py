from urllib.parse import urlparse


def safe_redirect_target(target, fallback):
    if not target:
        return fallback

    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or not target.startswith("/") or target.startswith("//"):
        return fallback
    return target
