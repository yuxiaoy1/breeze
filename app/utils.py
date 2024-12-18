from pathlib import Path
from urllib.parse import urljoin, urlparse
from uuid import uuid4

from flask import current_app, redirect, request, url_for


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def redirect_back(default="blog.index", **kwargs):
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def allowed_file(filename):
    return (
        "." in filename
        and Path(filename).suffix.lower()
        in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    )


def random_filename(filename):
    return uuid4().hex + Path(filename).suffix
