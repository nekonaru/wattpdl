# Contributing ke WattPDL

Makasih sudah tertarik bantu kembangin WattPDL! Panduan ini singkat aja biar gampang diikuti.

## Struktur Project

```
src/wattpdl/
├── __init__.py   # metadata package (__version__)
├── __main__.py   # entry untuk `python -m wattpdl`
├── app.py        # orkestrasi alur program (main())
├── api.py        # komunikasi ke Wattpad public API (fetch info & teks chapter)
├── writers.py    # konversi teks & penulisan file .txt/.docx/.epub/.zip
├── cli.py        # tampilan terminal (rich), interaksi dengan user
├── cli_args.py   # parsing & validasi argumen command line (mode non-interaktif)
├── config.py     # simpan preferensi user (folder simpan, format) di ~/.wattpdl/config.json
└── progress.py   # cache chapter yang berhasil diunduh, untuk fitur resume
tests/            # unit test (pytest)
```

Aturan sederhana:
- `api.py` tidak boleh tahu soal tampilan (`rich`)
- `writers.py` tidak boleh melakukan request jaringan
- `config.py` dan `progress.py` tidak boleh tahu soal CLI, `rich`, atau jaringan — murni baca-tulis JSON
- `cli_args.py` tidak boleh punya logika bisnis, hanya parsing & validasi argumen
- Import antar modul di dalam package pakai relative import (`from . import api`, bukan `import api`)

Kalau fitur baru butuh gabungan beberapa modul, taruh orkestrasinya di `app.py`.

## Setup Lokal

```bash
git clone https://github.com/nekonaru/wattpdl.git
cd wattpdl
pip install -e .[dev]
```

`pip install -e .[dev]` menginstall project dalam mode "editable" (perubahan kode langsung kepakai tanpa install ulang) sekaligus dependency development (`pytest`, `ruff`, `build`, `twine`). Setelah ini, command `wattpdl` di terminal akan menjalankan kode dari folder ini.

## Sebelum Membuat Pull Request

1. **Jalankan test** — pastikan semua lolos:
   ```bash
   pytest tests/ -v
   ```
2. **Jalankan linter** — pastikan tidak ada warning:
   ```bash
   ruff check .
   ```
3. Kalau menambah fungsi baru yang bisa dites tanpa koneksi internet (parsing, formatting, validasi), tambahkan unit test-nya di `tests/test_wattpdl.py`.
4. Update `README.md` kalau ada perubahan cara pakai atau fitur baru.

## Alur Kontribusi

1. Fork repo ini
2. Buat branch baru: `git checkout -b fitur/nama-fitur-kamu`
3. Commit perubahan dengan pesan yang jelas (`feat: ...`, `fix: ...`, `docs: ...`, `test: ...`)
4. Push ke fork kamu, lalu buka Pull Request ke branch `main`
5. Tunggu GitHub Actions (test + lint) selesai jalan dan hijau semua

## Melaporkan Bug

Buka [Issue baru](https://github.com/nekonaru/wattpdl/issues/new) dan sertakan:
- Versi Python yang dipakai
- Command/langkah yang dijalankan
- Pesan error lengkap (kalau ada)
- ID atau link cerita yang dipakai (kalau bug-nya spesifik ke cerita tertentu, tapi pastikan cerita itu publik)

## Proses Release (untuk maintainer)

1. Update nomor versi di **dua tempat** (harus sama):
   - `src/wattpdl/__init__.py` → `__version__ = "x.y.z"`
   - `pyproject.toml` → `version = "x.y.z"`
2. Commit perubahan versi, push ke `main`
3. Buat **GitHub Release** baru dengan tag `vx.y.z`
4. Publish release → workflow `.github/workflows/publish.yml` otomatis jalan, build package, dan upload ke PyPI lewat Trusted Publishing
5. Cek `https://pypi.org/project/wattpdl/` — versi baru harusnya muncul dalam beberapa menit

Trusted Publishing perlu didaftarkan sekali di halaman pengaturan project PyPI (Publishing → Add a new publisher) sebelum workflow ini bisa jalan. Lihat [docs.pypi.org/trusted-publishers](https://docs.pypi.org/trusted-publishers/).
