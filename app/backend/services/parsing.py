import re
from pathlib import Path

SUPPORTED = {".pdf", ".txt", ".md", ".docx"}


class UnsupportedFile(ValueError):
    pass


def parse(path: str) -> list[tuple[str, str]]:
    """Return [(section_label, text)] segments."""
    ext = Path(path).suffix.lower()
    if ext not in SUPPORTED:
        raise UnsupportedFile(f"Unsupported file type '{ext}'. Allowed: {sorted(SUPPORTED)}")
    if ext == ".pdf":
        import fitz
        with fitz.open(path) as pdf:
            return [(f"Page {i + 1}", p.get_text()) for i, p in enumerate(pdf) if p.get_text().strip()]
    if ext == ".docx":
        import docx
        segs, title, buf = [], "Document", []
        for p in docx.Document(path).paragraphs:
            if p.style.name.lower().startswith("heading"):
                if buf: segs.append((title, "\n".join(buf)))
                title, buf = p.text.strip() or title, []
            elif p.text.strip():
                buf.append(p.text)
        if buf: segs.append((title, "\n".join(buf)))
        return segs
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    if ext == ".txt":
        return [("Document", text)]
    segs, title, buf = [], "Introduction", []  # markdown: split on headings
    for line in text.splitlines():
        m = re.match(r"^#{1,4}\s+(.*)", line)
        if m:
            if "".join(buf).strip(): segs.append((title, "\n".join(buf)))
            title, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    if "".join(buf).strip(): segs.append((title, "\n".join(buf)))
    return segs
