"""Copy the official NTU site's favicon without redrawing or recoloring it."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
import json

HOME = "https://www.ntu.edu.tw/"


class Icons(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "link" and "icon" in attrs.get("rel", "").lower().split():
            if attrs.get("href"):
                self.urls.append(urljoin(HOME, attrs["href"]))


def download(url):
    request = Request(url, headers={"User-Agent": "AcademicWebsiteAssetRefresh/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.read(), response.url


parser = Icons()
html, _ = download(HOME)
parser.feed(html.decode("utf-8", errors="replace"))
errors = []
for url in dict.fromkeys([*parser.urls, urljoin(HOME, "favicon.ico")]):
    try:
        host = urlsplit(url).hostname or ""
        if urlsplit(url).scheme != "https" or not (host == "ntu.edu.tw" or host.endswith(".ntu.edu.tw")):
            continue
        data, resolved = download(url)
        host = urlsplit(resolved).hostname or ""
        if urlsplit(resolved).scheme != "https" or not (host == "ntu.edu.tw" or host.endswith(".ntu.edu.tw")):
            raise ValueError("Icon redirected outside NTU HTTPS")
        if data.startswith(b"\x00\x00\x01\x00"):
            extension = "ico"
        elif data.startswith(b"\x89PNG\r\n\x1a\n"):
            extension = "png"
        elif b"<svg" in data[:1024]:
            extension = "svg"
        else:
            raise ValueError("Response is not an ICO, PNG, or SVG image")
        target = Path("src/assets") / f"ntu-emblem.{extension}"
        target.write_bytes(data)
        Path("src/assets/ntu-emblem-source.json").write_text(json.dumps({
            "institution": "National Taiwan University",
            "source": resolved,
            "file": target.name
        }, indent=2) + "\n")
        print(f"Saved {target} ({len(data)} bytes) from {resolved}")
        break
    except Exception as error:
        errors.append(f"{url}: {error}")
else:
    raise RuntimeError("Could not retrieve an official NTU icon: " + "; ".join(errors))
