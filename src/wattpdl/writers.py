"""
Modul konversi teks dan penulisan file output.
Berisi semua fungsi yang mengubah teks chapter mentah menjadi file
.txt / .docx / .zip di disk. Tidak ada logika jaringan atau tampilan CLI di sini.
"""
import html
import pathlib
import re
import sys
import tempfile
import zipfile


def html_to_text(raw_html: str) -> str:
    """Konversi HTML Wattpad ke teks bersih."""
    text = re.sub(r"</p>",       "\n\n", raw_html, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>",  "\n",   text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>",   "",     text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}",    "\n\n", text)
    return text.strip()


def safe_filename(name: str, max_length: int = 100) -> str:
    """Buat nama file yang aman untuk semua sistem operasi.

    Judul cerita/chapter Wattpad kadang sangat panjang (umum untuk judul
    bergaya panjang/"clickbait"). Dipotong ke `max_length` supaya nama file
    akhir (yang di beberapa tempat menggabungkan judul cerita + judul chapter,
    lihat mode 4 di app.py) tidak melebihi batas panjang nama file sistem
    operasi (mis. 255 byte di Linux/macOS) dan menyebabkan OSError
    "File name too long" yang tidak tertangani saat menyimpan.
    """
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"[^\w\s\-]", "", name).strip()
    name = re.sub(r"\s+", "_", name)
    name = name[:max_length].rstrip("_")
    return name or "cerita_wattpad"


def check_docx_available(console=None) -> None:
    """Pastikan library python-docx terinstall sebelum dipakai."""
    try:
        import docx  # noqa: F401
    except ImportError:
        if console:
            console.print("\n[danger]❌  Library 'python-docx' belum terinstall.[/danger]")
            console.print("    [muted]Jalankan:[/muted] [accent]pip install python-docx[/accent]")
        else:
            print("Library 'python-docx' belum terinstall. Jalankan: pip install python-docx")
        sys.exit(1)


def check_epub_available(console=None) -> None:
    """Pastikan library EbookLib terinstall sebelum dipakai."""
    try:
        import ebooklib  # noqa: F401
    except ImportError:
        if console:
            console.print("\n[danger]❌  Library 'EbookLib' belum terinstall.[/danger]")
            console.print("    [muted]Jalankan:[/muted] [accent]pip install EbookLib[/accent]")
        else:
            print("Library 'EbookLib' belum terinstall. Jalankan: pip install EbookLib")
        sys.exit(1)


def write_combined_txt(path: pathlib.Path, title: str, author: str, story_id: str, results: list) -> None:
    """Tulis semua chapter yang diberikan ke satu file .txt."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n")
        f.write(f"oleh {author}\n")
        f.write(f"Sumber : https://www.wattpad.com/story/{story_id}\n")
        f.write(f"\n{'=' * 50}\n\n")
        for _, chapter_title, text in results:
            f.write(f"\n\n{'#' * 5} {chapter_title} {'#' * 5}\n\n")
            f.write(text)
            f.write("\n")


def write_combined_md(path: pathlib.Path, title: str, author: str, story_id: str, results: list,
                       meta: dict = None) -> None:
    """Tulis semua chapter yang diberikan ke satu file Markdown (.md)."""
    meta = meta or {}
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"**oleh** {author}\n\n")
        if meta.get("tags"):
            f.write(f"**Genre**: {', '.join(meta['tags'])}\n\n")
        if meta.get("description"):
            f.write(f"> {meta['description']}\n\n")
        f.write(f"Sumber: <https://www.wattpad.com/story/{story_id}>\n\n")
        f.write("---\n")
        for _, chapter_title, text in results:
            f.write(f"\n## {chapter_title}\n\n")
            for para in text.split("\n\n"):
                para = para.strip()
                if para:
                    f.write(f"{para}\n\n")


def write_separate_md_zip(path: pathlib.Path, title: str, author: str, story_id: str, results: list,
                           meta: dict = None) -> None:
    """Tulis tiap chapter sebagai file .md terpisah, dikemas dalam satu .zip."""
    meta = meta or {}
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        info_lines = [f"# {title}", "", f"**oleh** {author}"]
        if meta.get("tags"):
            info_lines.append(f"**Genre**: {', '.join(meta['tags'])}")
        if meta.get("description"):
            info_lines.append(f"\n> {meta['description']}")
        info_lines.append(f"\nSumber: <https://www.wattpad.com/story/{story_id}>")
        zf.writestr("000_info.md", "\n".join(info_lines) + "\n")
        for idx, chapter_title, text in results:
            fname = f"{idx:03d}_{safe_filename(chapter_title)}.md"
            body = "\n\n".join(p.strip() for p in text.split("\n\n") if p.strip())
            zf.writestr(fname, f"## {chapter_title}\n\n{body}\n")


def write_separate_zip(path: pathlib.Path, title: str, author: str, story_id: str, results: list) -> None:
    """Tulis tiap chapter sebagai file .txt terpisah, dikemas dalam satu .zip."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        info = (
            f"{title}\n"
            f"oleh {author}\n"
            f"Sumber : https://www.wattpad.com/story/{story_id}\n"
        )
        zf.writestr("000_info.txt", info)
        for idx, chapter_title, text in results:
            fname = f"{idx:03d}_{safe_filename(chapter_title)}.txt"
            zf.writestr(fname, f"{chapter_title}\n\n{text}\n")


def _write_paragraphs(doc, text: str) -> None:
    """Tulis teks chapter ke dokumen Word, menjaga jeda antar paragraf."""
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        p = doc.add_paragraph()
        lines = para.split("\n")
        for i, line in enumerate(lines):
            if i > 0:
                p.add_run().add_break()
            p.add_run(line)


def _insert_docx_cover(doc, cover_bytes: bytes) -> None:
    """Sisipkan gambar sampul di awal dokumen Word. Gagal decode/insert tidak boleh
    menggagalkan seluruh proses penulisan file — cover cuma pemanis."""
    import io

    from docx.shared import Inches

    try:
        doc.add_picture(io.BytesIO(cover_bytes), width=Inches(4))
    except Exception:
        pass


def write_combined_docx(path: pathlib.Path, title: str, author: str, story_id: str, results: list,
                         meta: dict = None, cover_bytes: bytes = None) -> None:
    """Tulis semua chapter yang diberikan ke satu file .docx."""
    from docx import Document

    meta = meta or {}
    doc = Document()
    if cover_bytes:
        _insert_docx_cover(doc, cover_bytes)
    doc.add_heading(title, level=0)
    doc.add_paragraph(f"oleh {author}")
    if meta.get("tags"):
        doc.add_paragraph(f"Genre: {', '.join(meta['tags'])}")
    if meta.get("description"):
        doc.add_paragraph(meta["description"])
    doc.add_paragraph(f"Sumber : https://www.wattpad.com/story/{story_id}")

    for _, chapter_title, text in results:
        doc.add_page_break()
        doc.add_heading(chapter_title, level=1)
        _write_paragraphs(doc, text)

    doc.save(str(path))


def write_separate_docx_zip(path: pathlib.Path, title: str, author: str, story_id: str, results: list,
                             meta: dict = None, cover_bytes: bytes = None) -> None:
    """Tulis tiap chapter sebagai file .docx terpisah, dikemas dalam satu .zip."""
    from docx import Document

    meta = meta or {}
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)

        info_doc = Document()
        if cover_bytes:
            _insert_docx_cover(info_doc, cover_bytes)
        info_doc.add_heading(title, level=0)
        info_doc.add_paragraph(f"oleh {author}")
        if meta.get("tags"):
            info_doc.add_paragraph(f"Genre: {', '.join(meta['tags'])}")
        if meta.get("description"):
            info_doc.add_paragraph(meta["description"])
        info_doc.add_paragraph(f"Sumber : https://www.wattpad.com/story/{story_id}")
        info_file = tmp_path / "000_info.docx"
        info_doc.save(str(info_file))

        chapter_files = [info_file]
        for idx, chapter_title, text in results:
            d = Document()
            d.add_heading(chapter_title, level=1)
            _write_paragraphs(d, text)
            fname = tmp_path / f"{idx:03d}_{safe_filename(chapter_title)}.docx"
            d.save(str(fname))
            chapter_files.append(fname)

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in chapter_files:
                zf.write(f, arcname=f.name)


def _text_to_epub_html(text: str) -> str:
    """Ubah teks chapter (paragraf dipisah \\n\\n, baris dipisah \\n) jadi HTML aman untuk EPUB."""
    paragraphs = []
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        lines = [html.escape(line) for line in para.split("\n")]
        paragraphs.append(f"<p>{'<br/>'.join(lines)}</p>")
    return "\n".join(paragraphs)


def _build_epub_book(title: str, author: str, story_id: str, identifier_suffix: str = None,
                      meta: dict = None):
    """
    Buat objek EpubBook kosong dengan metadata standar wattpdl.
    identifier_suffix: opsional, dipakai untuk membuat identifier EPUB unik per file
    (mis. per chapter) — tanpa ini, semua EPUB dari cerita yang sama akan punya
    identifier persis sama, yang melanggar spec EPUB dan bisa bikin sebagian
    e-reader (Calibre, Kobo) bentrok/menimpa entri satu sama lain.
    meta: dict opsional {"description", "tags", "create_date"} — kalau diisi,
    ditambahkan sebagai metadata Dublin Core standar (description, subject, date)
    supaya kelihatan di info buku pada e-reader yang mendukungnya.
    """
    from ebooklib import epub

    identifier = f"wattpdl-{story_id}" if identifier_suffix is None else f"wattpdl-{story_id}-{identifier_suffix}"
    book = epub.EpubBook()
    book.set_identifier(identifier)
    book.set_title(title)
    book.set_language("id")
    book.add_author(author)

    meta = meta or {}
    if meta.get("description"):
        book.add_metadata("DC", "description", meta["description"])
    for tag in meta.get("tags") or []:
        book.add_metadata("DC", "subject", tag)
    if meta.get("create_date"):
        book.add_metadata("DC", "date", str(meta["create_date"]))

    return book, epub


def _set_epub_cover(book, epub, cover_bytes: bytes) -> None:
    """Sisipkan gambar sampul ke EpubBook. Gagal insert tidak boleh menggagalkan
    seluruh proses penulisan file — cover cuma pemanis."""
    if not cover_bytes:
        return
    try:
        book.set_cover("cover.jpg", cover_bytes)
    except Exception:
        pass


def write_combined_epub(path: pathlib.Path, title: str, author: str, story_id: str, results: list,
                         meta: dict = None, cover_bytes: bytes = None) -> None:
    """Tulis semua chapter yang diberikan ke satu file .epub (satu buku, banyak bab)."""
    meta = meta or {}
    book, epub = _build_epub_book(title, author, story_id, meta=meta)
    _set_epub_cover(book, epub, cover_bytes)

    intro_body = (
        f"<h1>{html.escape(title)}</h1>"
        f"<p>oleh {html.escape(author)}</p>"
    )
    if meta.get("tags"):
        intro_body += f"<p>Genre: {html.escape(', '.join(meta['tags']))}</p>"
    if meta.get("description"):
        intro_body += f"<p>{html.escape(meta['description'])}</p>"
    intro_body += f"<p>Sumber: https://www.wattpad.com/story/{story_id}</p>"

    intro = epub.EpubHtml(title="Info", file_name="000_info.xhtml", lang="id")
    intro.content = intro_body
    book.add_item(intro)

    epub_chapters = [intro]
    for idx, chapter_title, text in results:
        c = epub.EpubHtml(title=chapter_title, file_name=f"chap_{idx:03d}.xhtml", lang="id")
        c.content = f"<h1>{html.escape(chapter_title)}</h1>{_text_to_epub_html(text)}"
        book.add_item(c)
        epub_chapters.append(c)

    book.toc = tuple(epub_chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + epub_chapters

    epub.write_epub(str(path), book)


def write_separate_epub_zip(path: pathlib.Path, title: str, author: str, story_id: str, results: list,
                             meta: dict = None, cover_bytes: bytes = None) -> None:
    """Tulis tiap chapter sebagai file .epub terpisah (satu bab per buku), dikemas dalam satu .zip."""
    meta = meta or {}
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)

        info_book, epub = _build_epub_book(title, author, story_id, identifier_suffix="info", meta=meta)
        _set_epub_cover(info_book, epub, cover_bytes)

        info_body = (
            f"<h1>{html.escape(title)}</h1>"
            f"<p>oleh {html.escape(author)}</p>"
        )
        if meta.get("tags"):
            info_body += f"<p>Genre: {html.escape(', '.join(meta['tags']))}</p>"
        if meta.get("description"):
            info_body += f"<p>{html.escape(meta['description'])}</p>"
        info_body += f"<p>Sumber: https://www.wattpad.com/story/{story_id}</p>"

        info_page = epub.EpubHtml(title="Info", file_name="info.xhtml", lang="id")
        info_page.content = info_body
        info_book.add_item(info_page)
        info_book.toc = (info_page,)
        info_book.add_item(epub.EpubNcx())
        info_book.add_item(epub.EpubNav())
        info_book.spine = ["nav", info_page]
        info_file = tmp_path / "000_info.epub"
        epub.write_epub(str(info_file), info_book)

        chapter_files = [info_file]
        for idx, chapter_title, text in results:
            chap_book, _ = _build_epub_book(
                f"{title} - {chapter_title}", author, story_id, identifier_suffix=f"ch{idx}"
            )
            page = epub.EpubHtml(title=chapter_title, file_name="chapter.xhtml", lang="id")
            page.content = f"<h1>{html.escape(chapter_title)}</h1>{_text_to_epub_html(text)}"
            chap_book.add_item(page)
            chap_book.toc = (page,)
            chap_book.add_item(epub.EpubNcx())
            chap_book.add_item(epub.EpubNav())
            chap_book.spine = ["nav", page]
            fname = tmp_path / f"{idx:03d}_{safe_filename(chapter_title)}.epub"
            epub.write_epub(str(fname), chap_book)
            chapter_files.append(fname)

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in chapter_files:
                zf.write(f, arcname=f.name)
