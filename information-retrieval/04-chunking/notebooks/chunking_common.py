from dataclasses import dataclass
import re
import unicodedata
from textwrap import fill


@dataclass(frozen=True)
class PageMetadata:
    book_title: str
    edition: str
    chapter: str
    section: str
    page_start: int
    page_end: int


@dataclass(frozen=True)
class SourcePage:
    metadata: PageMetadata
    text: str


@dataclass(frozen=True)
class SearchResult:
    score: int
    matches: tuple[str, ...]
    item: dict


STOPWORDS = {"a", "as", "com", "como", "de", "do", "dos", "em", "o", "os", "um", "uma"}


def parse_frontmatter(markdown: str) -> SourcePage:
    lines = markdown.splitlines()

    if not lines or lines[0] != "---":
        raise ValueError("A fonte precisa começar com um frontmatter delimitado por ---.")

    try:
        closing_marker = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("O frontmatter não tem um delimitador de fechamento.") from error

    values = {}
    for line in lines[1:closing_marker]:
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Linha inválida no frontmatter: {line}")

        value = value.strip().strip('"')
        values[key.strip()] = int(value) if value.isdigit() else value

    metadata = PageMetadata(
        book_title=values["book_title"],
        edition=values["edition"],
        chapter=values["chapter"],
        section=values["section"],
        page_start=values["page_start"],
        page_end=values["page_end"],
    )
    body = "\n".join(lines[closing_marker + 1:]).strip()
    return SourcePage(metadata=metadata, text=body)


def compact_preview(text: str, width: int = 72, max_chars: int = 180) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    was_truncated = len(normalized) > max_chars
    preview = normalized[:max_chars].rstrip()
    suffix = "..." if was_truncated else ""
    return fill(preview + suffix, width=width)


def normalize_terms(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.findall(r"[a-z0-9]+", normalized)


def tokenize_terms(text: str) -> list[str]:
    return [term for term in normalize_terms(text) if term not in STOPWORDS and len(term) >= 4]


def search(query: str, items: list[dict]) -> list[SearchResult]:
    query_terms = set(tokenize_terms(query))
    results = []

    for item in items:
        item_terms = tokenize_terms(item["text"])
        matches = tuple(sorted(query_terms.intersection(item_terms)))
        score = sum(item_terms.count(term) for term in matches)
        results.append(SearchResult(score=score, matches=matches, item=item))

    return sorted(results, key=lambda result: result.score, reverse=True)


def print_search_summary(query: str, results: list[SearchResult]) -> None:
    print(f"query: {query}")
    print("resultados por contagem simples de termos:")
    print("posição | chunk                  | score | termos")
    print("--------|------------------------|-------|----------------")

    for position, result in enumerate(results, start=1):
        item_id = result.item["metadata"]["chunk_id"]
        matches = ", ".join(result.matches) if result.matches else "nenhum"
        print(f"{position:>7} | {item_id:<22} | {result.score:>5} | {matches}")

    top_score = results[0].score
    top_results = [result for result in results if result.score == top_score]
    top_ids = ", ".join(result.item["metadata"]["chunk_id"] for result in top_results)
    print(f"\nmaior score simplificado: {top_score}")
    print(f"candidato(s) no topo: {top_ids}")
    print("prévia do primeiro candidato no topo:")
    print(compact_preview(top_results[0].item["text"], width=72))
