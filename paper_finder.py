from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import re
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable


CONFIG_PATH = Path("paper_finder_config.json")
STATE_PATH = Path(".paper_finder_state.json")
ARXIV_CACHE_PATH = Path(".paper_finder_arxiv_cache.json")

DEFAULT_CONFIG: dict[str, Any] = {
    "papers_dir": "papers",
    "reports_dir": "reports",
    "sources": ["arxiv", "openalex", "semantic_scholar", "crossref", "github"],
    "keywords_per_paper": 12,
    "max_keywords": 10,
    "days_back": 14,
    "max_results_per_source": 20,
    "max_pdf_pages": 8,
    "http_timeout_seconds": 20,
    "arxiv_mode": "web",
    "arxiv_web_queries": [
        "kv cache",
        "key value cache",
        "kv-cache",
        "prefix cache",
        "prompt cache",
        "cache reuse",
    ],
    "arxiv_web_categories": ["cs.CL", "cs.AI", "cs.LG", "cs.DC"],
    "arxiv_web_recent_show": 100,
    "arxiv_web_advanced_size": 50,
    "arxiv_timeout_seconds": 45,
    "arxiv_max_results": 12,
    "arxiv_query_delay_seconds": 5,
    "arxiv_cache_hours": 12,
    "arxiv_cooldown_hours": 24,
    "http_retries": 3,
    "min_relevance_score": 3,
    "min_keyword_length": 3,
    "query_language": "en",
    "seed_keywords": [
        "kv cache sharing",
        "cross model kv cache sharing",
        "multi agent kv cache communication",
        "kv cache reuse",
        "kv cache compression",
        "kv cache quantization",
        "long context inference",
        "llm inference acceleration",
    ],
    "exclude_terms": [],
}

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "can", "could",
    "for", "from", "has", "have", "in", "into", "is", "it", "its", "may",
    "more", "most", "of", "on", "or", "our", "such", "than", "that", "the",
    "their", "these", "this", "those", "to", "was", "we", "were", "which",
    "with", "within", "without", "also", "between", "both", "each", "other",
    "over", "under", "used", "via", "where", "while",
}


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        config = json.load(fh)
    merged = DEFAULT_CONFIG.copy()
    merged.update(config)
    return merged


def init_project() -> None:
    config = load_config()
    Path(config["papers_dir"]).mkdir(exist_ok=True)
    Path(config["reports_dir"]).mkdir(exist_ok=True)
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if not STATE_PATH.exists():
        STATE_PATH.write_text('{"seen_ids": []}\n', encoding="utf-8")


def read_pdf(path: Path, max_pages: int) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            f"{path.name} is a PDF, but pypdf is not installed. Run: python -m pip install pypdf"
        ) from exc

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages[:max_pages]]
    return "\n".join(pages)


def read_paper(path: Path, config: dict[str, Any]) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return read_pdf(path, int(config["max_pdf_pages"]))
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {path}")


def paper_paths(papers_dir: Path) -> list[Path]:
    supported = {".pdf", ".txt", ".md"}
    return sorted(path for path in papers_dir.iterdir() if path.suffix.lower() in supported)


def tokenize(text: str, min_len: int, exclude_terms: set[str]) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]+", text.lower())
    return [
        word.strip("-")
        for word in words
        if len(word.strip("-")) >= min_len
        and word not in STOPWORDS
        and word not in exclude_terms
        and not word.isdigit()
    ]


def extract_phrases(text: str, min_len: int, exclude_terms: set[str]) -> Counter[str]:
    phrases: Counter[str] = Counter()
    sentences = re.split(r"[\n.;:!?()\[\]{}]", text.lower())
    for sentence in sentences:
        tokens = tokenize(sentence, min_len, exclude_terms)
        for size in (3, 2):
            for idx in range(0, max(0, len(tokens) - size + 1)):
                phrase = " ".join(tokens[idx : idx + size])
                if not any(part in exclude_terms for part in phrase.split()):
                    phrases[phrase] += 1
    return phrases


def extract_keywords(texts: dict[Path, str], config: dict[str, Any]) -> list[str]:
    min_len = int(config["min_keyword_length"])
    exclude_terms = set(config.get("exclude_terms", []))
    doc_tokens = {path: tokenize(text, min_len, exclude_terms) for path, text in texts.items()}
    doc_freq: Counter[str] = Counter()
    for tokens in doc_tokens.values():
        doc_freq.update(set(tokens))

    doc_count = max(1, len(doc_tokens))
    scores: Counter[str] = Counter()
    for tokens in doc_tokens.values():
        term_freq = Counter(tokens)
        for term, freq in term_freq.items():
            idf = math.log((doc_count + 1) / (doc_freq[term] + 1)) + 1
            scores[term] += freq * idf

    phrase_scores: Counter[str] = Counter()
    for text in texts.values():
        phrase_scores.update(extract_phrases(text, min_len, exclude_terms))

    selected: list[str] = list(config.get("seed_keywords", []))
    for phrase, _ in phrase_scores.most_common(int(config["max_keywords"])):
        if len(selected) >= int(config["max_keywords"]):
            break
        if phrase not in selected:
            selected.append(phrase)

    for keyword, _ in scores.most_common(int(config["max_keywords"]) * 3):
        if len(selected) >= int(config["max_keywords"]):
            break
        if not any(keyword in existing.split() for existing in selected):
            selected.append(keyword)

    return selected[: int(config["max_keywords"])]


def http_get(
    url: str,
    accept: str = "application/json, application/atom+xml, */*",
    timeout: int | None = None,
    retries: int | None = None,
) -> bytes:
    config = load_config()
    attempts = retries if retries is not None else int(config["http_retries"])
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "paper-finder/1.0 (mailto:local@example.com)",
                "Accept": accept,
            },
        )
        try:
            with urllib.request.urlopen(
                req,
                timeout=timeout or int(config["http_timeout_seconds"]),
            ) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                raise RuntimeError("HTTP 429 rate limited; wait before retrying this source") from exc
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(min(2 * attempt, 8))
        except Exception as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(min(2 * attempt, 8))
    raise RuntimeError(str(last_error))


def arxiv_query(keywords: list[str]) -> str:
    return " OR ".join(f'"{keyword}"' if " " in keyword else keyword for keyword in keywords[:4])


def arxiv_web_query(keywords: list[str]) -> str:
    return keywords[0] if keywords else ""


def plain_query(keywords: list[str], limit: int = 6) -> str:
    return " ".join(keywords[:limit])


def load_json_file(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return default


def save_json_file(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_utc(value: str) -> dt.datetime | None:
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def cache_fresh(cache: dict[str, Any], query: str, max_age_hours: int, max_results: int) -> bool:
    fetched_at = parse_utc(str(cache.get("fetched_at", "")))
    if cache.get("query") != query or not fetched_at:
        return False
    if int(cache.get("max_results", 0)) < max_results:
        return False
    return utc_now() - fetched_at <= dt.timedelta(hours=max_age_hours)


def arxiv_cooldown_active(cache: dict[str, Any]) -> bool:
    blocked_until = parse_utc(str(cache.get("blocked_until", "")))
    return bool(blocked_until and utc_now() < blocked_until)


class ArxivSearchHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.capture: str | None = None
        self.link_candidate = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        classes = set(attr.get("class", "").split())
        if tag == "li" and "arxiv-result" in classes:
            self.current = {
                "kind": "paper",
                "source": "arXiv",
                "id": "",
                "title": "",
                "url": "",
                "published": "",
                "authors": "",
                "abstract": "",
            }
        if not self.current:
            return
        if tag == "p" and "title" in classes:
            self.capture = "title"
        elif tag == "p" and "authors" in classes:
            self.capture = "authors"
        elif tag == "span" and "abstract-full" in classes:
            self.capture = "abstract"
        elif tag == "p" and "is-size-7" in classes:
            self.capture = "meta"
        elif tag == "a":
            href = attr.get("href", "")
            if "/abs/" in href and not self.current.get("url"):
                self.current["url"] = href if href.startswith("http") else f"https://arxiv.org{href}"
                self.current["id"] = self.current["url"]
            self.link_candidate = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "li" and self.current:
            self.current = normalize_arxiv_web_item(self.current)
            if self.current.get("title") and self.current.get("url"):
                self.results.append(self.current)
            self.current = None
        if tag == "p":
            self.capture = None
        elif tag == "span" and self.capture == "abstract":
            self.capture = None
        if tag == "a":
            self.link_candidate = False

    def handle_data(self, data: str) -> None:
        if not self.current or not self.capture:
            return
        text = " ".join(html.unescape(data).split())
        if not text:
            return
        existing = self.current.get(self.capture, "")
        self.current[self.capture] = f"{existing} {text}".strip()


def normalize_arxiv_web_item(item: dict[str, str]) -> dict[str, str]:
    item["title"] = item.get("title", "").replace("Title:", "").strip()
    item["authors"] = item.get("authors", "").replace("Authors:", "").strip()
    item["abstract"] = (
        item.get("abstract", "")
        .replace("△ Less", "")
        .replace("Abstract:", "")
        .strip()
    )
    meta = item.pop("meta", "")
    match = re.search(r"Submitted\s+(\d{1,2}\s+\w+,\s+\d{4})", meta)
    if match:
        try:
            item["published"] = dt.datetime.strptime(match.group(1), "%d %B, %Y").date().isoformat()
        except ValueError:
            item["published"] = ""
    return item


class ArxivRecentHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self.current_id = ""
        self.current_url = ""
        self.current_title = ""
        self.current_authors = ""
        self.current_date = ""
        self.capture: str | None = None
        self.in_list_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        classes = set(attr.get("class", "").split())
        if tag == "a" and attr.get("title") == "Abstract":
            href = attr.get("href", "")
            self.current_url = href if href.startswith("http") else f"https://arxiv.org{href}"
            self.current_id = self.current_url
        elif tag == "div" and "list-title" in classes:
            self.capture = "title"
            self.in_list_title = True
        elif tag == "div" and "list-authors" in classes:
            self.capture = "authors"
        elif tag == "h3":
            self.capture = "date"

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.capture:
            self.capture = None
        if tag == "dd" and self.current_url:
            self.results.append(
                {
                    "kind": "paper",
                    "source": "arXiv",
                    "id": self.current_id,
                    "title": self.current_title.replace("Title:", "").strip(),
                    "url": self.current_url,
                    "published": self.current_date,
                    "authors": self.current_authors.replace("Authors:", "").strip(),
                    "abstract": "",
                }
            )
            self.current_id = ""
            self.current_url = ""
            self.current_title = ""
            self.current_authors = ""

    def handle_data(self, data: str) -> None:
        if not self.capture:
            return
        text = " ".join(html.unescape(data).split())
        if not text:
            return
        if self.capture == "title":
            self.current_title = f"{self.current_title} {text}".strip()
        elif self.capture == "authors":
            self.current_authors = f"{self.current_authors} {text}".strip()
        elif self.capture == "date":
            match = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", text)
            if match:
                try:
                    self.current_date = dt.datetime.strptime(match.group(1), "%d %B %Y").date().isoformat()
                except ValueError:
                    self.current_date = ""


def fetch_arxiv_query(query: str, max_results: int, config: dict[str, Any]) -> list[dict[str, str]]:
    encoded = urllib.parse.urlencode(
        {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    raw = http_get(
        f"https://export.arxiv.org/api/query?{encoded}",
        timeout=int(config["arxiv_timeout_seconds"]),
        retries=int(config["http_retries"]),
    )
    root = ET.fromstring(raw)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results: list[dict[str, str]] = []
    for entry in root.findall("atom:entry", ns):
        paper_id = entry.findtext("atom:id", default="", namespaces=ns)
        authors = [
            author.findtext("atom:name", default="", namespaces=ns)
            for author in entry.findall("atom:author", ns)
        ]
        results.append(
            {
                "kind": "paper",
                "source": "arXiv",
                "id": paper_id,
                "title": " ".join(entry.findtext("atom:title", default="", namespaces=ns).split()),
                "url": paper_id,
                "published": entry.findtext("atom:published", default="", namespaces=ns)[:10],
                "authors": ", ".join(authors[:5]),
                "abstract": " ".join(entry.findtext("atom:summary", default="", namespaces=ns).split()),
            }
        )
    return results


def fetch_arxiv_web_search(query: str, max_results: int, config: dict[str, Any]) -> list[dict[str, str]]:
    params = {
        "query": query,
        "searchtype": "all",
        "abstracts": "show",
        "order": "-announced_date_first",
        "size": 25,
    }
    raw = http_get(
        f"https://arxiv.org/search/?{urllib.parse.urlencode(params)}",
        accept="text/html,application/xhtml+xml,*/*",
        timeout=int(config["arxiv_timeout_seconds"]),
        retries=1,
    )
    parser = ArxivSearchHTMLParser()
    parser.feed(raw.decode("utf-8", errors="ignore"))
    return parser.results[:max_results]


def fetch_arxiv_advanced_search(
    query: str,
    since: dt.date,
    until: dt.date,
    max_results: int,
    config: dict[str, Any],
) -> list[dict[str, str]]:
    params = {
        "advanced": "",
        "terms-0-operator": "AND",
        "terms-0-term": query,
        "terms-0-field": "all",
        "classification-computer_science": "y",
        "classification-include_cross_list": "include",
        "date-filter_by": "date_range",
        "date-from_date": since.isoformat(),
        "date-to_date": until.isoformat(),
        "date-date_type": "submitted_date",
        "abstracts": "show",
        "size": int(config.get("arxiv_web_advanced_size", 50)),
        "order": "-announced_date_first",
    }
    raw = http_get(
        f"https://arxiv.org/search/advanced?{urllib.parse.urlencode(params)}",
        accept="text/html,application/xhtml+xml,*/*",
        timeout=int(config["arxiv_timeout_seconds"]),
        retries=1,
    )
    parser = ArxivSearchHTMLParser()
    parser.feed(raw.decode("utf-8", errors="ignore"))
    return parser.results[:max_results]


def fetch_arxiv_web_backfill(
    keywords: list[str],
    since: dt.date,
    max_results: int,
    config: dict[str, Any],
) -> list[dict[str, str]]:
    queries = list(config.get("arxiv_web_queries", [])) or [arxiv_web_query(keywords)]
    results: list[dict[str, str]] = []
    for idx, query in enumerate(dict.fromkeys(queries)):
        if idx > 0:
            time.sleep(int(config["arxiv_query_delay_seconds"]))
        results.extend(fetch_arxiv_advanced_search(query, since, dt.date.today(), max_results, config))
    return dedupe_items(results)[:max_results]


def fetch_arxiv_recent_categories(max_results: int, config: dict[str, Any]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    categories = list(config.get("arxiv_web_categories", []))
    show = int(config.get("arxiv_web_recent_show", 100))
    for idx, category in enumerate(categories):
        if idx > 0:
            time.sleep(int(config["arxiv_query_delay_seconds"]))
        raw = http_get(
            f"https://arxiv.org/list/{urllib.parse.quote(category)}/recent?show={show}",
            accept="text/html,application/xhtml+xml,*/*",
            timeout=int(config["arxiv_timeout_seconds"]),
            retries=1,
        )
        parser = ArxivRecentHTMLParser()
        parser.feed(raw.decode("utf-8", errors="ignore"))
        results.extend(parser.results)
    return dedupe_items(results)[:max_results]


def search_arxiv(keywords: list[str], max_results: int, from_date: dt.date) -> list[dict[str, str]]:
    config = load_config()
    per_query = min(max_results, int(config["arxiv_max_results"]))
    mode = str(config.get("arxiv_mode", "web"))
    query = (
        f"advanced:{from_date.isoformat()}:{dt.date.today().isoformat()}:"
        + ";".join(config.get("arxiv_web_queries", []))
        if mode == "web"
        else arxiv_query(keywords)
    )
    cache = load_json_file(ARXIV_CACHE_PATH, {})

    if cache.get("mode") == mode and cache_fresh(cache, query, int(config["arxiv_cache_hours"]), max_results):
        return list(cache.get("results", []))[:max_results]

    if cache.get("mode") == mode and arxiv_cooldown_active(cache):
        cached_results = list(cache.get("results", []))
        if cached_results:
            return cached_results[:max_results]
        raise RuntimeError(f"cooldown active until {cache.get('blocked_until')}")

    try:
        if mode == "web":
            try:
                results = fetch_arxiv_web_backfill(keywords, from_date, max_results, config)
            except Exception:
                results = fetch_arxiv_recent_categories(max_results, config)
        else:
            results = fetch_arxiv_query(query, per_query, config)
    except Exception as exc:
        if "429" in str(exc):
            cache["mode"] = mode
            cache["query"] = query
            cache["blocked_until"] = (
                utc_now() + dt.timedelta(hours=int(config["arxiv_cooldown_hours"]))
            ).isoformat()
            save_json_file(ARXIV_CACHE_PATH, cache)
        raise

    cache = {
        "mode": mode,
        "query": query,
        "max_results": max_results,
        "fetched_at": utc_now().isoformat(),
        "blocked_until": "",
        "results": dedupe_items(results)[:max_results],
    }
    save_json_file(ARXIV_CACHE_PATH, cache)
    return dedupe_items(results)[:max_results]


def search_openalex(keywords: list[str], max_results: int, from_date: dt.date) -> list[dict[str, str]]:
    params = {
        "search": plain_query(keywords),
        "filter": f"from_publication_date:{from_date.isoformat()}",
        "sort": "publication_date:desc",
        "per-page": max_results,
    }
    data = json.loads(http_get(f"https://api.openalex.org/works?{urllib.parse.urlencode(params)}"))
    results: list[dict[str, str]] = []
    for item in data.get("results", []):
        authorships = item.get("authorships", [])
        authors = [
            entry.get("author", {}).get("display_name", "")
            for entry in authorships
            if entry.get("author")
        ]
        results.append(
            {
                "kind": "paper",
                "source": "OpenAlex",
                "id": item.get("id", ""),
                "title": item.get("display_name", ""),
                "url": item.get("doi") or item.get("id", ""),
                "published": item.get("publication_date", ""),
                "authors": ", ".join(authors[:5]),
                "abstract": inverted_index_to_text(item.get("abstract_inverted_index")),
            }
        )
    return results


def search_semantic_scholar(
    keywords: list[str], max_results: int, _from_date: dt.date
) -> list[dict[str, str]]:
    params = {
        "query": plain_query(keywords),
        "limit": min(max_results, 100),
        "fields": "title,url,abstract,authors,publicationDate,year,externalIds",
    }
    data = json.loads(
        http_get(f"https://api.semanticscholar.org/graph/v1/paper/search?{urllib.parse.urlencode(params)}")
    )
    results: list[dict[str, str]] = []
    for item in data.get("data", []):
        external_ids = item.get("externalIds") or {}
        paper_id = external_ids.get("DOI") or item.get("paperId") or item.get("url", "")
        authors = [author.get("name", "") for author in item.get("authors", [])]
        results.append(
            {
                "kind": "paper",
                "source": "Semantic Scholar",
                "id": str(paper_id),
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "published": item.get("publicationDate") or str(item.get("year") or ""),
                "authors": ", ".join(authors[:5]),
                "abstract": item.get("abstract") or "",
            }
        )
    return results


def search_crossref(keywords: list[str], max_results: int, from_date: dt.date) -> list[dict[str, str]]:
    params = {
        "query": plain_query(keywords),
        "filter": f"from-pub-date:{from_date.isoformat()},until-pub-date:{dt.date.today().isoformat()}",
        "sort": "published",
        "order": "desc",
        "rows": max_results,
    }
    data = json.loads(http_get(f"https://api.crossref.org/works?{urllib.parse.urlencode(params)}"))
    results: list[dict[str, str]] = []
    for item in data.get("message", {}).get("items", []):
        authors = [
            " ".join(part for part in [author.get("given", ""), author.get("family", "")] if part)
            for author in item.get("author", [])
        ]
        published = date_parts_to_iso(item.get("published-print") or item.get("published-online"))
        doi = item.get("DOI", "")
        results.append(
            {
                "kind": "paper",
                "source": "Crossref",
                "id": doi or item.get("URL", ""),
                "title": " ".join(item.get("title", [""])[0].split()) if item.get("title") else "",
                "url": f"https://doi.org/{doi}" if doi else item.get("URL", ""),
                "published": published,
                "authors": ", ".join(authors[:5]),
                "abstract": strip_html(" ".join(item.get("abstract", "").split())),
            }
        )
    return results


def search_github(keywords: list[str], max_results: int, from_date: dt.date) -> list[dict[str, str]]:
    terms = plain_query(keywords, limit=4)
    query = f'{terms} paper arxiv research created:>={from_date.isoformat()}'
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": min(max_results, 100),
    }
    data = json.loads(
        http_get(
            f"https://api.github.com/search/repositories?{urllib.parse.urlencode(params)}",
            accept="application/vnd.github+json",
        )
    )
    results: list[dict[str, str]] = []
    for item in data.get("items", []):
        results.append(
            {
                "kind": "resource",
                "source": "GitHub",
                "id": str(item.get("id", "")),
                "title": item.get("full_name", ""),
                "url": item.get("html_url", ""),
                "published": item.get("created_at", "")[:10],
                "authors": item.get("owner", {}).get("login", ""),
                "abstract": item.get("description") or "",
            }
        )
    return results


def date_parts_to_iso(value: Any) -> str:
    parts = value.get("date-parts", [[]])[0] if isinstance(value, dict) else []
    if not parts:
        return ""
    year = int(parts[0])
    month = int(parts[1]) if len(parts) > 1 else 1
    day = int(parts[2]) if len(parts) > 2 else 1
    return dt.date(year, month, day).isoformat()


def strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def inverted_index_to_text(index: Any) -> str:
    if not isinstance(index, dict):
        return ""
    positioned: dict[int, str] = {}
    for word, positions in index.items():
        for position in positions:
            positioned[int(position)] = word
    return " ".join(word for _, word in sorted(positioned.items()))


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"seen_ids": []}
    return load_json_file(STATE_PATH, {"seen_ids": []})


def save_state(state: dict[str, Any]) -> None:
    save_json_file(STATE_PATH, state)


def dedupe_items(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in items:
        key = item.get("id") or item.get("url") or item.get("title", "").lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def within_date_window(item: dict[str, str], from_date: dt.date) -> bool:
    published = item.get("published", "")
    if not published:
        return True
    if len(published) == 4 and published.isdigit():
        year = int(published)
        return from_date.year <= year <= dt.date.today().year
    try:
        published_date = dt.date.fromisoformat(published[:10])
        return from_date <= published_date <= dt.date.today()
    except ValueError:
        return True


def relevance_score(item: dict[str, str], keywords: list[str]) -> int:
    haystack = f"{item.get('title', '')} {item.get('abstract', '')}".lower()
    score = 0
    for phrase in keywords:
        phrase = phrase.lower()
        if " " in phrase and phrase in haystack:
            score += 4

    key_terms = {
        term
        for keyword in keywords
        for term in keyword.lower().split()
        if term in {"kv", "cache", "quantization", "compression", "inference", "context", "prefill", "latent"}
    }
    for term in key_terms:
        if re.search(rf"\b{re.escape(term)}\b", haystack):
            score += 1
    return score


def item_text(item: dict[str, str]) -> str:
    text = f"{item.get('title', '')} {item.get('abstract', '')}".lower()
    text = re.sub(r"\bkv\s*-\s*cache\b", "kv cache", text)
    text = re.sub(r"\bkey\s*-\s*value\b", "key value", text)
    text = re.sub(r"\blong\s*-\s*context\b", "long-context", text)
    return text


def contains_kv_cache(text: str) -> bool:
    return bool(re.search(r"\bkv[-\s]?(cache|caching)\b|\bkey[-\s]?value[-\s]?cache\b", text))


def has_p1_sharing_signal(text: str) -> bool:
    patterns = [
        r"\bkv[-\s]?(cache|caching)\s+(shar(e|ed|ing)|communication|collaboration)\b",
        r"\b(shar(e|ed|ing)|collaborative)\s+(prefix\s+)?kv[-\s]?(cache|caching)\b",
        r"\bcross[-\s]?(user|request|context|model)\b",
        r"\bacross\s+(users|requests|models|contexts)\b",
        r"\bmulti[-\s]?(agent|model)\b",
        r"\bkv[-\s]?cache[-\s]?communication\b",
        r"\bkv\s+state\s+disaggregation\b",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def has_system_management_signal(text: str) -> bool:
    patterns = [
        r"\b(disaggregated|cross[-\s]?datacenter|remote|tiered|multi[-\s]?tier|offload|offloading)\b",
        r"\b(serving|serverless|service-aware|runtime|scheduler|scheduling|deployment|cluster|gpu cluster)\b",
        r"\b(prefill[-\s]?as[-\s]?a[-\s]?service|pd separation|resource allocation|memory pool)\b",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def has_algorithmic_kv_signal(text: str) -> bool:
    patterns = [
        r"\b(compress|compression|quantization|quantized|low[-\s]?precision)\b",
        r"\b(eviction|pruning|retention|sparsity|sparse|routing|token dropping)\b",
        r"\b(hidden states|semantic chunking|clustered merging|attention similarity)\b",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def has_application_signal(text: str) -> bool:
    patterns = [
        r"\b(prefix caching|prompt caching|cache reuse|reuse|reusing)\b",
        r"\b(rag|agent|tool calling|video|vision-language|vlm|vla|moe|diffusion|code generation)\b",
        r"\b(inference acceleration|latency|throughput|long-context|long context)\b",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def rank_item(item: dict[str, str], keywords: list[str]) -> dict[str, Any]:
    text = item_text(item)
    score = relevance_score(item, keywords)
    has_kv_cache = contains_kv_cache(text)

    if has_kv_cache and has_p1_sharing_signal(text):
        priority = 1
        category = "P1 KV cache sharing and communication"
    elif has_kv_cache and has_system_management_signal(text):
        priority = 2
        category = "P2 KV serving systems and lifecycle management"
    elif has_kv_cache and has_algorithmic_kv_signal(text):
        priority = 3
        category = "P3 KV compression, quantization, and eviction algorithms"
    elif has_kv_cache and has_application_signal(text):
        priority = 4
        category = "P4 KV-enabled application acceleration"
    elif has_kv_cache:
        priority = 5
        category = "P5 general KV cache research"
    else:
        priority = 6
        category = "P6 peripheral cache/context/inference reference"

    item["rank_priority"] = str(priority)
    item["rank_category"] = category
    item["rank_score"] = str(score)
    item["fit_reason"] = fit_reason(text, priority)
    return {"priority": priority, "score": score, "published": item.get("published", "")}


def fit_reason(text: str, priority: int) -> str:
    reasons: list[str] = []
    if priority == 1:
        reasons.append("directly targets KV sharing, cross-request/cross-model reuse, or KV communication")
    if priority == 2:
        reasons.append("focuses on serving architecture, disaggregation, scheduling, offloading, or lifecycle management")
    if priority == 3:
        reasons.append("proposes KV representation or retention algorithms")
    if priority == 4:
        reasons.append("uses KV/cache behavior to accelerate a workload or task")
    mechanism_matches = [
        term
        for term in ["compression", "quantization", "eviction", "offloading", "management", "prefill", "disaggregated", "sharing", "reuse"]
        if term in text
    ]
    if mechanism_matches:
        reasons.append("mechanisms: " + ", ".join(mechanism_matches[:4]))
    context_matches = [
        term
        for term in ["inference", "serving", "latency", "throughput", "memory", "bandwidth", "long-context", "agent", "multi-agent"]
        if term in text
    ]
    if context_matches:
        reasons.append("context: " + ", ".join(context_matches[:4]))
    if not reasons:
        reasons.append("broader cache/context/inference relation")
    return "; ".join(reasons)


def relevant_enough(item: dict[str, str], keywords: list[str], config: dict[str, Any]) -> bool:
    rank = rank_item(item, keywords)
    return rank["priority"] <= 5 or rank["score"] >= int(config.get("min_relevance_score", 3))


def sort_items(items: list[dict[str, str]], keywords: list[str]) -> list[dict[str, str]]:
    ranked: list[tuple[tuple[int, int, str], dict[str, str]]] = []
    for item in items:
        rank = rank_item(item, keywords)
        ranked.append(((rank["priority"], -rank["score"], date_sort_key(str(rank["published"]))), item))
    ranked.sort(key=lambda pair: pair[0])
    return [item for _, item in ranked]


def date_sort_key(value: str) -> str:
    if not value:
        return "9999-99-99"
    try:
        parsed = dt.date.fromisoformat(value[:10])
    except ValueError:
        return "9999-99-99"
    inverted = dt.date.max.toordinal() - parsed.toordinal()
    return f"{inverted:08d}"


def sort_new_items_like_all_items(
    new_items: list[dict[str, str]], sorted_items: list[dict[str, str]]
) -> list[dict[str, str]]:
    order = {item.get("id") or item.get("url") or item.get("title", ""): idx for idx, item in enumerate(sorted_items)}
    return sorted(
        new_items,
        key=lambda item: order.get(item.get("id") or item.get("url") or item.get("title", ""), len(order)),
    )


def enabled_searches(config: dict[str, Any]) -> list[tuple[str, Callable[[list[str], int, dt.date], list[dict[str, str]]]]]:
    registry: dict[str, Callable[[list[str], int, dt.date], list[dict[str, str]]]] = {
        "arxiv": search_arxiv,
        "openalex": search_openalex,
        "semantic_scholar": search_semantic_scholar,
        "crossref": search_crossref,
        "github": search_github,
    }
    return [(name, registry[name]) for name in config.get("sources", []) if name in registry]


def render_report(
    report_date: dt.date,
    items: list[dict[str, str]],
    new_items: list[dict[str, str]],
    keywords: list[str],
    config: dict[str, Any],
) -> str:
    paper_count = sum(1 for item in items if item.get("kind") == "paper")
    resource_count = sum(1 for item in items if item.get("kind") == "resource")
    lines = [
        f"# Paper discovery report {report_date.isoformat()}",
        "",
        "## Extracted keywords",
        "",
        ", ".join(keywords) if keywords else "No keywords extracted.",
        "",
        "## Search settings",
        "",
        f"- Sources: {', '.join(config.get('sources', []))}",
        f"- Days back: {config['days_back']}",
        f"- Total papers: {paper_count}",
        f"- Total GitHub/resources: {resource_count}",
        f"- New items: {len(new_items)}",
        "",
    ]
    lines.extend(render_section("New papers", [item for item in new_items if item.get("kind") == "paper"]))
    lines.extend(render_section("New GitHub/resources", [item for item in new_items if item.get("kind") != "paper"]))
    return "\n".join(lines).rstrip() + "\n"


def weekly_report_path(reports_dir: Path, report_date: dt.date) -> Path:
    iso_year, iso_week, _ = report_date.isocalendar()
    return reports_dir / f"{iso_year}-W{iso_week:02d}.md"


def update_weekly_report(weekly_report: Path, report_date: dt.date, report: str) -> None:
    iso_year, iso_week, _ = report_date.isocalendar()
    start_marker = f"<!-- paper-finder-run:{report_date.isoformat()}:start -->"
    end_marker = f"<!-- paper-finder-run:{report_date.isoformat()}:end -->"
    body = "\n".join(report.splitlines()[1:]).strip()
    entry = (
        f"{start_marker}\n"
        f"## Run {report_date.isoformat()}\n\n"
        f"{body}\n"
        f"{end_marker}\n"
    )

    if weekly_report.exists():
        current = weekly_report.read_text(encoding="utf-8")
    else:
        current = f"# Paper discovery weekly report {iso_year}-W{iso_week:02d}\n\n"

    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}\n?",
        flags=re.DOTALL,
    )
    if pattern.search(current):
        updated = pattern.sub(entry, current)
    else:
        updated = current.rstrip() + "\n\n" + entry
    weekly_report.write_text(updated.rstrip() + "\n", encoding="utf-8")


def render_section(title: str, items: list[dict[str, str]]) -> list[str]:
    lines = [f"## {title}", ""]
    if not items:
        lines.extend(["No new items.", ""])
        return lines
    for idx, item in enumerate(items, start=1):
        abstract = textwrap.shorten(item.get("abstract", ""), width=500, placeholder="...")
        lines.extend(
            [
                f"### {idx}. {item.get('title', 'Untitled')}",
                "",
                f"- Source: {item.get('source', '')}",
                f"- Priority: {item.get('rank_category', '')}; score {item.get('rank_score', '')}",
                f"- Date: {item.get('published', '')}",
                f"- Authors/Owner: {item.get('authors', '')}",
                f"- Link: {item.get('url', '')}",
                f"- Summary: {abstract}",
                "",
            ]
        )
    return lines


def run() -> int:
    config = load_config()
    init_project()
    papers_dir = Path(config["papers_dir"])
    reports_dir = Path(config["reports_dir"])
    paths = paper_paths(papers_dir)
    if not paths:
        print(f"No papers found in {papers_dir}. Add .pdf/.txt/.md files and run again.", file=sys.stderr)
        return 2

    texts: dict[Path, str] = {}
    for path in paths:
        try:
            texts[path] = read_paper(path, config)
        except Exception as exc:
            print(f"Skipped {path.name}: {exc}", file=sys.stderr)

    if not texts:
        print("No readable paper text found.", file=sys.stderr)
        return 2

    keywords = extract_keywords(texts, config)
    from_date = dt.date.today() - dt.timedelta(days=int(config["days_back"]))
    max_results = int(config["max_results_per_source"])

    items: list[dict[str, str]] = []
    errors: list[str] = []
    for name, search in enabled_searches(config):
        try:
            items.extend(search(keywords, max_results, from_date))
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    items = [
        item
        for item in dedupe_items(items)
        if within_date_window(item, from_date) and relevant_enough(item, keywords, config)
    ]
    items = sort_items(items, keywords)
    state = load_state()
    seen_ids = set(state.get("seen_ids", []))
    new_items = sort_new_items_like_all_items(
        [item for item in items if item.get("id") not in seen_ids],
        items,
    )
    state["seen_ids"] = sorted(seen_ids | {item.get("id", "") for item in items if item.get("id")})
    save_state(state)

    today = dt.date.today()
    report = render_report(today, items, new_items, keywords, config)
    if errors:
        report += "\n## Search errors\n\n" + "\n".join(f"- {error}" for error in errors) + "\n"

    reports_dir.mkdir(exist_ok=True)
    weekly_report = weekly_report_path(reports_dir, today)
    latest_report = reports_dir / "latest.md"
    update_weekly_report(weekly_report, today, report)
    latest_report.write_text(report, encoding="utf-8")

    print(f"Report written: {weekly_report}")
    print(f"Keywords: {', '.join(keywords)}")
    print(f"New items: {len(new_items)} / total items: {len(items)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract keywords from local papers and find recent work.")
    parser.add_argument("--init", action="store_true", help="Create papers/, reports/, and default state file.")
    args = parser.parse_args()
    if args.init:
        init_project()
        print("Project initialized.")
        return 0
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
