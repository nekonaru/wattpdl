# Contributing ke WattPDL

Makasih sudah tertarik bantu kembangin WattPDL! Panduan ini singkat aja biar gampang diikuti.

## Struktur Project

```
wattpdl.py    # entry point, orkestrasi alur program (main())
api.py        # komunikasi ke Wattpad public API (fetch info & teks chapter)
writers.py    # konversi teks & penulisan file .txt/.docx/.zip
cli.py        # tampilan terminal (rich), interaksi dengan user
tests/        # unit test (pytest)
```

Aturan sederhana: `api.py` tidak boleh tahu soal tampilan (`rich`), dan `writers.py` tidak boleh melakukan request jaringan. Kalau fitur baru butuh keduanya, taruh orkestrasinya di `wattpdl.py` atau `cli.py`.

## Setup Lokal

```bash
git clone https://github.com/nekonaru/wattpdl.git
cd wattpdl
pip install -r requirements.txt
pip install pytest ruff
```

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
