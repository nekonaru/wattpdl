"""
Communication module for the Wattpad public API.
Contains every function that fetches raw data from the internet
(story info & chapter text), with no concern for display or file writing.
"""
import re
import threading
import time
from typing import Optional

import requests

from .i18n import t

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

STORY_INFO_URL = (
    "https://www.wattpad.com/api/v3/stories/{story_id}"
    "?fields=id,title,description,cover,tags,createDate,completed,"
    "user(name),numParts,parts(id,title)"
)
CHAPTER_TEXT_URL = "https://www.wattpad.com/apiv2/storytext?id={part_id}"

# NOTE: this endpoint (get_author_stories) follows the same public Wattpad
# API v3 URL pattern as STORY_INFO_URL above, but has not yet been
# verified against the real server because this development environment
# has no network access to wattpad.com. If the real JSON response structure
# turns out to differ, only the parsing in
# `get_author_stories()` needs adjusting; its signature and callers stay the same.
AUTHOR_STORIES_URL = (
    "https://www.wattpad.com/api/v3/users/{username}/stories/published"
    "?fields=stories(id,title,numParts,completed)"
)

DELAY_SECONDS = 0.5   # base delay between chapters (do not remove)
MAX_RETRIES = 3


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


def get_story_info(story_id: str) -> tuple[str, str, list, dict]:
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
    resp = requests.get(url, headers=HEADERS, timeout=20)
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


def get_author_stories(username: str) -> list:
    """
    Fetch the list of stories published by a Wattpad author.
    Return a list of dicts: [{"id": str, "title": str, "num_parts": int, "completed": bool}, ...]

    Used by the `--user <username>` feature (download all or selected stories
    from one author at once, without looking up IDs one by one).
    """
    url = AUTHOR_STORIES_URL.format(username=username)
    resp = requests.get(url, headers=HEADERS, timeout=20)
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


def download_cover_image(cover_url: str) -> Optional[bytes]:
    """
    Download the story cover image. Used to embed the cover in .docx/.epub files.
    A failure here must not stop the story download: the cover is only a
    nice-to-have, not an essential part, so always return None on failure
    and never raise an exception.
    """
    if not cover_url:
        return None
    try:
        resp = requests.get(cover_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException:
        return None


def download_image(image_url: str) -> Optional[bytes]:
    """Download 1 generic image (used for inline images inside a chapter).
    Same as download_cover_image: a failure must not break the whole
    process, inline images are only extras, return None on failure.
    """
    if not image_url:
        return None
    try:
        resp = requests.get(image_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException:
        return None


def get_chapter_html(
    part_id: int,
    retries: int = MAX_RETRIES,
    on_retry=None,
    rate_limiter: Optional[AdaptiveRateLimiter] = None,
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
        raise ValueError("retries harus >= 1")

    url = CHAPTER_TEXT_URL.format(part_id=part_id)
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            if rate_limiter:
                rate_limiter.report_success()
            return resp.text
        except requests.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if rate_limiter and status in (429, 503):
                rate_limiter.report_throttled()
            if attempt == retries:
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
