"""
Communication module for the Wattpad public API.
Contains every function that fetches raw data from the internet
(story info & chapter text), with no concern for display or file writing.
"""
import re
import threading
import time
from typing import Optional
from urllib.parse import urlparse

import requests

from .i18n import t

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# One shared `requests.Session` per thread, so chapter downloads reuse TCP/TLS
# connections instead of a full handshake per request. The downloads can run on
# several threads (--workers), so the session is kept thread-local (sessions are
# not documented as thread-safe). Requests to the same host reuse the pooled
# connection either way; that is where almost all of the time is saved.
_thread_local = threading.local()


def _http_session() -> requests.Session:
    session = getattr(_thread_local, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update(HEADERS)
        adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=10)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        _thread_local.session = session
    return session

STORY_INFO_URL = (
    "https://www.wattpad.com/api/v3/stories/{story_id}"
    "?fields=id,title,description,cover,tags,createDate,completed,"
    "user(name),numParts,parts(id,title)"
)
CHAPTER_TEXT_URL = "https://www.wattpad.com/apiv2/storytext?id={part_id}"

AUTHOR_STORIES_URL = (
    "https://www.wattpad.com/api/v3/users/{username}/stories/published"
    "?fields=stories(id,title,numParts,completed)"
)
SEARCH_URL = "https://www.wattpad.com/api/v3/stories"
SEARCH_FIELDS = "stories(id,title,numParts,completed,user(name))"

DELAY_SECONDS = 0.5   # base delay between chapters (do not remove)
MAX_RETRIES = 3       # default chapter download retry count
DEFAULT_TIMEOUT = 20  # default HTTP timeout in seconds
MAX_IMAGE_BYTES = 25 * 1024 * 1024  # max size of a downloaded image (cover or inline), 25 MB


class WattpadAPIError(Exception):
    """Base class for every Wattpad API error that already has a specific message."""


class StoryNotFoundError(WattpadAPIError):
    """Story not found, deleted by its author, or the ID/link is wrong."""


class StoryAccessError(WattpadAPIError):
    """Story exists but cannot be accessed (private/restricted)."""


class AdaptiveRateLimiter:
    """State for the delay between requests, shared by every chapter (and every
    worker in parallel downloads), so the download slows down automatically when
    Wattpad starts returning consecutive rate limits (429) or busy server errors (503),
    then gradually speeds up again once requests succeed. Thread-safe.
    """

    def __init__(self, base_delay: float = DELAY_SECONDS, max_delay: float = 10.0):
        self._lock = threading.Lock()
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._level = 0  # 0 = normal speed, higher means slower

    @property
    def current_delay(self) -> float:
        with self._lock:
            return min(self.max_delay, self.base_delay * (2 ** self._level))

    def report_throttled(self) -> None:
        """Call every time a 429/503 response is received."""
        with self._lock:
            self._level += 1

    def report_success(self) -> None:
        """Call every time a request succeeds, and lower the level gradually (not
        straight to 0, so it does not speed up again right away just because 1 request
        happened to get through while the server is still busy)."""
        with self._lock:
            if self._level > 0:
                self._level -= 1

    def wait(self) -> None:
        time.sleep(self.current_delay)


def extract_story_id(user_input: str) -> str:
    """Accept a full link or a numeric ID, and return only the story ID."""
    user_input = user_input.strip()
    match = re.search(r"story/(\d+)", user_input)
    if match:
        return match.group(1)
    if user_input.isdigit():
        return user_input

    # Wattpad share/mobile per-chapter links (e.g. wattpad.com/1234567-title-part)
    # do not contain "story/" and the number is a chapter (part) ID, not a story ID,
    # so it cannot be used directly here. Give a clear message instead of a generic one.
    chapter_link = re.search(r"wattpad\.com/(\d+)-", user_input)
    if chapter_link:
        raise ValueError(t("api.chapter_link"))

    raise ValueError(t("api.unrecognized"))


def _raise_specific_http_error(e: requests.HTTPError, context: str = None) -> None:
    """Turn a generic requests.HTTPError into a clear message based on the status code."""
    status = e.response.status_code if e.response is not None else None
    if context is None:
        context = t("api.context_story")
    if status == 404:
        raise StoryNotFoundError(
            t("api.not_found", context=context.capitalize())
        ) from e
    if status in (401, 403):
        raise StoryAccessError(
            t("api.private", context=context.capitalize())
        ) from e
    raise e


def get_story_info(story_id: str, timeout: Optional[int] = None) -> tuple[str, str, list, dict]:
    """
    Fetch story metadata: title, author, chapter list, and extra metadata.
    The extra metadata (the `meta` dict) is used to enrich .docx/.epub files:
      - cover_url    : URL of the story cover image (or None if there is none)
      - description  : story synopsis/description
      - tags         : list of story genres/tags
      - create_date  : date the story was first created, as-is from the API
      - completed    : True if the story has been marked as finished by its author

    Raise StoryNotFoundError / StoryAccessError with a clear message if the
    story is not found / cannot be accessed, instead of a generic
    requests.HTTPError.
    """
    url = STORY_INFO_URL.format(story_id=story_id)
    resp = _http_session().get(url, timeout=timeout or DEFAULT_TIMEOUT)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        _raise_specific_http_error(e, context=t("api.context_story"))
    data = resp.json()
    title = data.get("title", f"story_{story_id}")
    author = data.get("user", {}).get("name", "unknown")
    parts = data.get("parts", [])
    meta = {
        "cover_url": data.get("cover") or None,
        "description": (data.get("description") or "").strip(),
        "tags": [t for t in (data.get("tags") or []) if t],
        "create_date": data.get("createDate", ""),
        "completed": bool(data.get("completed", False)),
        "num_parts": data.get("numParts"),
    }
    return title, author, parts, meta


def search_stories(query: str, timeout: Optional[int] = None, limit: int = 10) -> list:
    """
    Search Wattpad public API (v3 stories endpoint).
    Return a list of dicts: [{"id": str, "title": str, "num_parts": int, "completed": bool, "author": str}, ...]

    Used by the `--search "<query>"` feature (issue: search fanfics and
    download several by index). `limit` is clamped to 1-100 (Wattpad
    serves at most 100 results per request). The result order is
    Wattpad's relevance order, the same as when searching on the website;
    the titles are shown as-is.
    """
    query = (query or "").strip()
    if not query:
        return []
    limit = max(1, min(int(limit), 100))
    resp = _http_session().get(
        SEARCH_URL,
        params={"query": query, "fields": SEARCH_FIELDS, "limit": limit},
        timeout=timeout or DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    stories = data.get("stories", [])
    return [
        {
            "id": str(s.get("id")),
            "title": s.get("title", f"story_{s.get('id')}"),
            "num_parts": s.get("numParts", 0),
            "completed": bool(s.get("completed", False)),
            "author": (s.get("user") or {}).get("name", "unknown"),
        }
        for s in stories
    ]


def get_author_stories(username: str, timeout: Optional[int] = None) -> list:
    """
    Fetch the list of stories published by a Wattpad author.
    Return a list of dicts: [{"id": str, "title": str, "num_parts": int, "completed": bool}, ...]

    Used by the `--user <username>` feature (download all or selected stories
    from one author at once, without looking up IDs one by one).
    """
    url = AUTHOR_STORIES_URL.format(username=username)
    resp = _http_session().get(url, timeout=timeout or DEFAULT_TIMEOUT)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        _raise_specific_http_error(e, context=t("api.context_author"))
    data = resp.json()
    stories = data.get("stories", [])
    return [
        {
            "id": str(s.get("id")),
            "title": s.get("title", f"story_{s.get('id')}"),
            "num_parts": s.get("numParts", 0),
            "completed": bool(s.get("completed", False)),
        }
        for s in stories
    ]


def _is_private_host(host) -> bool:
    """True when `host` resolves to anything other than a globally routable,
    non-multicast address (loopback, RFC1918, link-local like the cloud
    metadata endpoint 169.254.169.254, CGNAT 100.64.0.0/10, unspecified,
    reserved). Used to stop inline-image fetches, whose URLs come from
    story HTML, from being aimed at internal networks."""
    import ipaddress
    import socket

    host = (host or "").strip().rstrip(".").lower()
    if not host or host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        addrinfos = socket.getaddrinfo(host, None)
    except OSError:
        # DNS failed; the request will fail anyway, no need to block it here
        return False
    for info in addrinfos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return True
        if ip.is_multicast or not ip.is_global:
            return True
    return False


def download_image(image_url: str, timeout: Optional[int] = None) -> Optional[bytes]:
    """Download 1 image (used for inline images inside a chapter, and for the
    story cover). A failure must not break the whole process, images are only
    extras, so always return None on failure and never raise an exception.
    """
    if not image_url:
        return None
    try:
        parsed = urlparse(image_url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return None
        if _is_private_host(parsed.hostname):
            return None
        resp = _http_session().get(
            image_url,
            timeout=timeout or DEFAULT_TIMEOUT,
            stream=True,
        )
        resp.raise_for_status()
        chunks, total = [], 0
        for chunk in resp.iter_content(chunk_size=65536):
            total += len(chunk)
            if total > MAX_IMAGE_BYTES:
                return None
            chunks.append(chunk)
        return b"".join(chunks)
    except requests.RequestException:
        return None


def download_cover_image(cover_url: str, timeout: Optional[int] = None) -> Optional[bytes]:
    """Download the story cover image. Used to embed the cover in .docx/.epub files.
    Same contract as download_image: a failure must not stop the story download,
    return None on failure instead of raising. Kept as a separate name for
    backwards compatibility.
    """
    return download_image(cover_url, timeout=timeout)


def get_chapter_html(
    part_id: int,
    retries: int = MAX_RETRIES,
    on_retry=None,
    rate_limiter: Optional[AdaptiveRateLimiter] = None,
    timeout: Optional[int] = None,
) -> str:
    """
    Download the chapter text HTML with automatic retry.
    on_retry: optional callback called with (attempt, retries, wait, error)
    every time an attempt fails, used by the CLI to show a warning message
    without this module needing to know about `rich`/console.
    rate_limiter: optional, if given then 429/503 responses report
    themselves to the rate limiter so the delay between chapters slows down automatically.
    """
    if retries < 1:
        raise ValueError("retries must be >= 1")

    url = CHAPTER_TEXT_URL.format(part_id=part_id)
    session = _http_session()
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=timeout or DEFAULT_TIMEOUT)
            resp.raise_for_status()
            if rate_limiter:
                rate_limiter.report_success()
            return resp.text
        except requests.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if rate_limiter and status in (429, 503):
                rate_limiter.report_throttled()
            if attempt == retries:
                if status in (404, 401, 403):
                    _raise_specific_http_error(e, context=t("api.context_chapter"))
                raise
            wait = attempt * 2
            if on_retry:
                on_retry(attempt, retries, wait, e)
            time.sleep(wait)


_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_IMG_ATTR_RES = [
    re.compile(rf'(?<![\w-]){attr}\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    for attr in ("src", "data-src", "data-original")
]


def extract_chapter_images(html: str) -> list:
    """Find all inline image URLs (<img> tags) inside the HTML of 1 chapter, in
    the order they appear in the text. Used by the inline image download
    feature (not just the cover) for .docx/.epub/.pdf.
    """
    urls = []
    for tag in _IMG_TAG_RE.findall(html or ""):
        for attr_re in _IMG_ATTR_RES:  # src first, then lazy-load attributes
            m = attr_re.search(tag)
            if not m:
                continue
            url = m.group(1).strip()
            if url.startswith("//"):
                url = "https:" + url
            if url.lower().startswith(("http://", "https://")):
                urls.append(url)
                break
    return urls
