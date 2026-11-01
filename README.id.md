<div align="center">
  <h1>WattPDL: Pengunduh Cerita Wattpad</h1>
  <p><b>Simpan cerita favoritmu sebagai file <code>.txt</code>, <code>.docx</code>, <code>.epub</code>, <code>.md</code>, atau <code>.pdf</code>,<br/>
  utuh atau bab per bab, untuk dibaca offline.</b></p>

  <a href="https://pypi.org/project/wattpdl/"><img src="https://img.shields.io/pypi/v/wattpdl?style=flat-square&color=blue" alt="PyPI" /></a>
  <a href="https://github.com/nekonaru/wattpdl/actions/workflows/tests.yml"><img src="https://github.com/nekonaru/wattpdl/actions/workflows/tests.yml/badge.svg" alt="Tests" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status" />
</div>

<br />

[English](https://github.com/nekonaru/wattpdl/blob/main/README.md) | **Bahasa Indonesia**

> [!CAUTION]
> Skrip ini hanya untuk membaca ceritamu sendiri atau cerita publik secara offline. Hormati hak cipta para penulis. Jangan menyebarluaskan atau menjual cerita orang lain.

---

## Daftar Isi

- [Tentang](#tentang)
- [Fitur](#fitur)
- [Persyaratan](#persyaratan)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Resume Otomatis](#resume-otomatis)
- [Preferensi Tersimpan](#preferensi-tersimpan)
- [Bahasa Tampilan](#bahasa-tampilan)
- [Mode Non-Interaktif (Skrip/Otomasi)](#mode-non-interaktif-skripotomasi)
- [Struktur Output](#struktur-output)
- [Folder Default per OS](#folder-default-per-os)
- [Pemecahan Masalah](#pemecahan-masalah)
- [Catatan Penting](#catatan-penting)
- [Dibangun Dengan](#dibangun-dengan)
- [Struktur Proyek](#struktur-proyek)
- [Pengujian](#pengujian)
- [Continuous Integration](#continuous-integration)
- [Kontribusi](#kontribusi)
- [FAQ](#faq)
- [Penulis](#penulis)
- [Lisensi](#lisensi)

---

## Tentang

**WattPDL** adalah skrip Python ringan yang mengunduh bab-bab dari cerita Wattpad pilihanmu dan menyimpannya sebagai file `.txt` polos yang bersih dan rapi, dokumen Word `.docx`, ebook `.epub`, file Markdown `.md`, atau `.pdf`. Kamu bisa mengunduh seluruh cerita dalam satu file, setiap bab terpisah dalam satu `.zip`, atau hanya bab yang kamu pilih, lengkap dengan sampul cerita yang otomatis disematkan di `.docx`/`.epub`/`.pdf`. Tanpa login, tanpa API key, cukup link atau ID cerita.

> _"Karena cerita yang bagus layak dibaca kapan saja, bahkan tanpa internet."_

---

## Fitur

### Pengunduhan

| Fitur | Deskripsi |
|-------|-----------|
| **4 mode unduh** | Semua dalam 1 file, semua terpisah dalam `.zip`, pilih beberapa bab, atau hanya 1 bab |
| **5 format file** | Simpan sebagai `.txt` polos, Word `.docx`, ebook `.epub`, Markdown `.md`, atau `.pdf` |
| **Tanpa login** | Memakai endpoint publik Wattpad, jadi tidak perlu akun |
| **Unduh berdasarkan penulis** | `--user <username>` mengunduh semua atau sebagian cerita dari satu penulis sekaligus |
| **Pilih folder simpan** | Default ke folder `Downloads` sistem, bisa diubah |
| **Lewati file yang sudah ada** | Lewati unduhan jika file output sudah ada di folder tujuan, sehingga tidak ada yang tertimpa tanpa sengaja |
| **Nama file aman** | Karakter terlarang dihapus dari nama file secara otomatis |

### Isi Output

| Fitur | Deskripsi |
|-------|-----------|
| **Sampul otomatis** | Sampul cerita disematkan di file `.docx`/`.epub`/`.pdf` (bisa dimatikan dengan `--no-cover`) |
| **Gambar inline** | Opsional (`--include-images`) mengunduh & menyematkan gambar di dalam teks bab, bukan hanya sampul. Gambar yang sangat tinggi (webtoon/komik strip) dipotong ke beberapa halaman PDF agar tetap terbaca |
| **Metadata EPUB lengkap** | Genre/tag, deskripsi cerita, dan tanggal terbit disimpan sebagai metadata buku |
| **Link sumber tersimpan** | URL cerita disertakan di bagian header file hasil |
| **`--lang`** | Mengatur kode bahasa metadata EPUB (default `id`) untuk cerita dalam bahasa lain |

### Keandalan dan Kecepatan

| Fitur | Deskripsi |
|-------|-----------|
| **Coba ulang otomatis** | Bab yang gagal dicoba ulang hingga 3 kali sebelum dilewati |
| **Resume otomatis** | Jika proses berhenti di tengah jalan, jalankan cerita yang sama lagi: bab yang sudah berhasil tidak diunduh ulang |
| **Unduh paralel** | `--workers N` mengunduh beberapa bab sekaligus, mempercepat cerita panjang secara signifikan |
| **Rate limit adaptif** | Jeda antar bab melambat otomatis saat Wattpad mulai membatasi permintaan (429/503), lalu perlahan dipercepat lagi |
| **Cache metadata** | Info cerita di-cache sebentar sehingga percobaan berulang dalam waktu singkat tidak selalu mengenai API |
| **Pesan error spesifik** | Pesan berbeda untuk cerita yang dihapus (404) dan yang privat/dibatasi (403) |

### Antarmuka

| Fitur | Deskripsi |
|-------|-----------|
| **Tampilan CLI rapi** | Panel, tabel info cerita, dan warna berkat library `rich` |
| **Antarmuka Inggris dan Indonesia** | CLI berbahasa Inggris secara default; ganti dengan `--ui-lang id` (menu, pesan, dan `--help`) |
| **Progress bar animasi** | Spinner, persentase, jumlah bab, dan perkiraan sisa waktu |
| **Ringkasan akhir** | Panel laporan yang mencantumkan bab yang gagal (jika ada) saat selesai |
| **Mengingat preferensi** | Folder simpan, format file, dan bahasa terakhir dipakai lagi di sesi berikutnya |

### Otomasi dan Pembaruan

| Fitur | Deskripsi |
|-------|-----------|
| **Mode non-interaktif** | Jalankan dengan argumen command line untuk skrip/otomasi, tanpa pertanyaan yang harus dijawab |
| **Deteksi bab baru** | `--check-updates` melaporkan cerita ongoing mana yang sudah punya bab baru |
| **Mode watch** | `--watch` memantau 1 cerita terus-menerus dan mengunduh ulang begitu bab baru muncul |
| **Cek pembaruan wattpdl** | Memberi tahu otomatis saat versi wattpdl yang lebih baru ada di PyPI |

---

## Persyaratan

| Dependensi | Versi Minimum | Catatan |
|------------|---------------|---------|
| **Python** | 3.9 | Wajib |
| **Koneksi internet** | apa saja | Wajib |
| **Library** | lihat catatan | `requests`, `rich`, `python-docx`, `EbookLib`, `reportlab`, terinstal otomatis bersama `wattpdl`, tidak perlu instal manual |

### Belum pernah memakai terminal? Mulai dari sini

<details>
<summary><b>Cara membuka terminal di Windows</b></summary>

1. Tekan tombol **Windows**, ketik `PowerShell`, lalu tekan **Enter**
2. Jendela hitam/biru akan terbuka. Di situlah kamu mengetik perintah
3. Setiap perintah `python ...` atau `pip ...` di panduan ini diketik di jendela itu, diikuti **Enter**

</details>

<details>
<summary><b>Cara membuka terminal di macOS</b></summary>

1. Tekan **Cmd + Space**, ketik `Terminal`, lalu tekan **Enter**
2. Ketik perintah dari panduan ini di sana, diikuti **Enter**

</details>

<details>
<summary><b>Cara membuka terminal di Linux</b></summary>

Tekan **Ctrl + Alt + T**, atau cari aplikasi "Terminal" di menu aplikasimu.

</details>

### Belum punya Python?

1. Buka [python.org/downloads](https://www.python.org/downloads/) dan unduh versi terbaru
2. **Khusus Windows**: saat instalasi, centang kotak **"Add Python to PATH"** di layar pertama sebelum menekan Install
3. Setelah terinstal, buka terminal (lihat panduan di atas) dan cek dengan:

```bash
python --version
# atau
python3 --version
```

Jika nomor versi muncul (misalnya `Python 3.12.1`), kamu sudah siap.

> [!WARNING]
> Di Windows, jika kotak **"Add Python to PATH"** terlewat saat instalasi, perintah `python` tidak akan dikenali nantinya.

---

## Instalasi

### Opsi A: Instal dari PyPI (paling mudah)

```bash
pip install wattpdl
```

> [!TIP]
> Jika `pip` tidak dikenali, coba `python -m pip install wattpdl`.

> [!NOTE]
> Jika muncul error `externally-managed-environment` (biasanya di Linux), jalankan:
> ```bash
> pip install wattpdl --break-system-packages
> ```

Setelah terinstal, perintah `wattpdl` bisa dijalankan dari terminal mana pun. Lanjut ke [Penggunaan](#penggunaan).

### Opsi B: Instal dari source (untuk pengembangan / membaca atau mengubah kode)

#### 1. Ambil kode proyek

<details>
<summary><b>Saya sudah menginstal Git</b></summary>

```bash
git clone https://github.com/nekonaru/wattpdl.git
cd wattpdl
```

</details>

<details>
<summary><b>Saya belum punya Git</b></summary>

1. Buka halaman repositori di GitHub
2. Klik tombol hijau **`Code`**, lalu pilih **`Download ZIP`**
3. Ekstrak file ZIP yang diunduh ke folder pilihanmu
4. Di terminal, masuk ke folder hasil ekstrak, contohnya:

```bash
cd Downloads/wattpdl-main
```

</details>

#### 2. Instal dalam mode "editable"

```bash
pip install -e .
```

> [!NOTE]
> Sama seperti Opsi A, tambahkan `--break-system-packages` di akhir jika muncul error `externally-managed-environment`.

Ini juga mendaftarkan perintah `wattpdl`, tetapi kodenya dimuat langsung dari folder ini, sehingga ideal jika kamu ingin mengubah kode dan langsung melihat hasilnya tanpa instal ulang.

### Opsi C: Arch Linux (AUR)

Pengguna Arch Linux bisa menginstalnya dari AUR. Paket ini dikelola komunitas oleh [@Vaishnav-Sabari-Girish](https://github.com/Vaishnav-Sabari-Girish): [`wattpdl` di AUR](https://aur.archlinux.org/packages/wattpdl).

```bash
# Memakai yay
yay -S wattpdl

# Memakai paru
paru -S wattpdl
```

> [!NOTE]
> Paket AUR dikelola terpisah, jadi versi baru bisa muncul di sana sedikit setelah rilis PyPI.

---

## Penggunaan

> [!NOTE]
> Contoh tampilan di bawah memakai bahasa default CLI (English). Gunakan `--ui-lang id` untuk tampilan berbahasa Indonesia.

**Jalankan:**

```bash
wattpdl
```

> [!NOTE]
> Jika kamu menginstal dari source tanpa `pip install -e .`, jalankan dengan `python -m wattpdl` dari dalam folder `src/`. Meski begitu, instalasi editable di atas lebih disarankan.

**Masukkan link atau ID cerita saat diminta:**

```
Wattpad story link or ID: https://www.wattpad.com/story/123456789-story-title
```

atau cukup ID-nya:

```
Wattpad story link or ID: 123456789
```

**Pilih mode unduh:**

```
  1  All chapters → 1 combined file
  2  All chapters → separate file per chapter, packed as .zip
  3  Select several chapters → 1 combined file
  4  Select 1 chapter only

Select mode [1/2/3/4] (1):
```

| Mode | Deskripsi |
|------|-----------|
| **Mode 1** | Cara paling umum, seluruh cerita sebagai satu file rapi dari bab pertama sampai terakhir |
| **Mode 2** | Cocok jika kamu ingin membaca bab per bab, menghasilkan satu `.zip` berisi satu file per bab |
| **Mode 3** | Daftar bernomor semua judul bab muncul, lalu ketik nomor yang kamu mau dengan kombinasi koma dan rentang, contoh: `1,3,5-8` |
| **Mode 4** | Daftar semua judul bab muncul, ketik satu nomor untuk mengunduh bab itu saja |

**Pilih format file:**

```
  1  Plain text (.txt)
  2  Word document (.docx)
  3  Ebook (.epub)
  4  Markdown (.md)
  5  PDF (.pdf)

Select file format [1/2/3/4/5] (1):
```

**Pilih folder simpan:**

```
Default folder: C:\Users\user\Downloads
Press Enter to use that folder, or type another path:
```

Tekan **Enter** untuk menyimpan di `Downloads`, atau ketik path kustom seperti:
- Windows: `D:\Stories\Wattpad`
- Linux/macOS: `/home/user/stories`

**Tunggu sampai selesai:**

```
⠋ Chapter 24...              ████████████████░░░░░░░░░░░░░░  53.3%  24/45  0:00:12  left 0:00:11
```

**Selesai!**

```
╔═════════════ Success!  All chapters saved ══════════════╗
║ File saved to   C:\Users\user\Downloads\Story_Title.txt ║
║ Succeeded       45/45                                   ║
║ Total time      2m 18s                                  ║
╚═════════════════════════════════════════════════════════╝
```

---

## Resume Otomatis

Jika unduhan berhenti di tengah jalan (koneksi putus, terminal ditutup, laptop dimatikan), setiap bab yang **sudah berhasil** tersimpan otomatis di `~/.wattpdl/progress/<story_id>.json`.

Jalankan lagi dengan cerita yang sama (ID/link yang sama), dan WattPDL akan:
- Melewati bab yang sudah berhasil (diambil dari cache, tidak diunduh ulang)
- Mengunduh hanya bab yang belum berhasil atau sebelumnya gagal

File progress dihapus otomatis setelah semua bab selesai diunduh dalam satu sesi. Untuk memaksa unduhan dari awal, hapus folder `~/.wattpdl/progress/` secara manual.

> [!NOTE]
> **Tidak sama dengan `--skip-existing`:** resume di atas bekerja di tingkat *bab* (melanjutkan unduhan yang berhenti di tengah). `--skip-existing` bekerja di tingkat *file output*: jika file akhir (misalnya `Story_Title.epub`) sudah ada di folder tujuan, seluruh unduhan dilewati sepenuhnya, berguna bersama `cron`/Task Scheduler agar cerita yang sudah diunduh tidak diunduh lagi.

---

## Preferensi Tersimpan

Folder simpan, format file, dan bahasa tampilan terakhir yang kamu pilih disimpan otomatis di `~/.wattpdl/config.json` dan dipakai sebagai default di sesi berikutnya, jadi tidak perlu mengisinya setiap kali menjalankan skrip.

---

## Bahasa Tampilan

Tampilan CLI (menu, prompt, pesan error, dan teks `--help`) tersedia dalam **English** (default) dan **Indonesia**.

```bash
wattpdl --ui-lang id              # Indonesia, pilihan ini diingat untuk run berikutnya
wattpdl --ui-lang en              # kembali ke English
WATTPDL_LANG=id wattpdl           # lewat environment variable
```

Urutan prioritas: `--ui-lang` → env `WATTPDL_LANG` → `ui_lang` di `~/.wattpdl/config.json` → default `en`.

> [!IMPORTANT]
> `--ui-lang` hanya mengubah tampilan CLI. Jangan tertukar dengan `--lang`, yang mengatur kode bahasa di metadata EPUB.

---

## Mode Non-Interaktif (Skrip/Otomasi)

Selain mode tanya-jawab, WattPDL juga bisa dijalankan lewat argumen command line, sangat cocok untuk penjadwalan (cron/Task Scheduler) atau dipanggil dari skrip lain.

```bash
wattpdl --id 398440633 --mode 1 --format docx
```

### Argumen yang tersedia

| Argumen | Deskripsi |
|---|---|
| `--id` | ID atau link cerita Wattpad. Menyetel ini mengaktifkan mode non-interaktif. |
| `--mode {1,2,3,4}` | 1 = semua dalam 1 file, 2 = semua terpisah dalam `.zip`, 3 = pilih beberapa bab, 4 = pilih 1 bab |
| `--format {txt,docx,epub,md,pdf}` | Format file output. Default: dari config tersimpan, atau `txt` |
| `--chapters` | Nomor bab untuk `--mode 3`, contoh: `1,3,5-8` |
| `--chapter` | Nomor bab untuk `--mode 4`, contoh: `5` |
| `--output-dir` | Folder simpan kustom. Default: dari config tersimpan, atau folder `Downloads` |
| `--skip-existing` | Lewati unduhan jika file output tujuan sudah ada, alih-alih menimpanya |
| `--no-cover` | Jangan sematkan gambar sampul cerita di file `.docx`/`.epub`/`.pdf` |
| `--include-images` | Unduh & sematkan juga gambar inline di dalam bab (menambah waktu unduh) |
| `--workers N` | Jumlah bab yang diunduh bersamaan (default 1) |
| `--no-cache` | Jangan pakai cache metadata cerita, selalu ambil data terbaru |
| `--lang` | Kode bahasa ISO 639-1 untuk metadata EPUB (default `id`) |
| `--ui-lang {id,en}` | Bahasa tampilan CLI (default `en`, diingat setelah dipilih) |
| `--user` / `--user-select` | Unduh dari daftar cerita seorang penulis, opsional memilih cerita mana saja |
| `--check-updates` | Laporkan cerita terunduh mana yang punya bab baru |
| `--watch` / `--watch-interval` | Pantau sebuah cerita dan unduh ulang saat bab baru muncul (interval cek default 1800 detik) |
| `--no-update-check` | Jangan cek versi wattpdl terbaru di PyPI saat startup |
| `--version` | Tampilkan versi wattpdl |

### Contoh lainnya

```bash
# Unduh semua bab sebagai file terpisah dalam .zip
wattpdl --id 398440633 --mode 2 --format txt

# Unduh hanya bab 1, 3, dan 5-8 sebagai 1 file gabungan
wattpdl --id 398440633 --mode 3 --chapters 1,3,5-8 --format docx

# Unduh hanya bab 10, simpan ke folder kustom
wattpdl --id 398440633 --mode 4 --chapter 10 --output-dir "D:\Wattpad Stories"

# Unduh semua bab sebagai 1 ebook .epub
wattpdl --id 398440633 --mode 1 --format epub

# Unduh sebagai Markdown, lewati jika file sudah ada (bagus untuk penjadwalan)
wattpdl --id 398440633 --mode 1 --format md --skip-existing

# Tampilkan semua opsi
wattpdl --help
```

---

## Struktur Output

Nama dan bentuk file yang dihasilkan bergantung pada mode & format yang kamu pilih:

| Mode | Format `.txt` | Format `.docx` | Format `.epub` | Format `.md` | Format `.pdf` |
|------|----------------|-----------------|------------------|---------------|---------------|
| 1 - Semua, digabung | `Story_Title.txt` | `Story_Title.docx` | `Story_Title.epub` | `Story_Title.md` | `Story_Title.pdf` |
| 2 - Semua, terpisah | `Story_Title.zip` (berisi: satu `.txt` per bab) | `Story_Title.zip` (berisi: satu `.docx` per bab) | `Story_Title.zip` (berisi: satu `.epub` per bab) | `Story_Title.zip` (berisi: satu `.md` per bab) | `Story_Title.zip` (berisi: satu `.pdf` per bab) |
| 3 - Beberapa bab | `Story_Title_selected.txt` | `Story_Title_selected.docx` | `Story_Title_selected.epub` | `Story_Title_selected.md` | `Story_Title_selected.pdf` |
| 4 - Satu bab | `Story_Title_Ch003_Chapter_Name.txt` | `Story_Title_Ch003_Chapter_Name.docx` | `Story_Title_Ch003_Chapter_Name.epub` | `Story_Title_Ch003_Chapter_Name.md` | `Story_Title_Ch003_Chapter_Name.pdf` |

### Isi file gabungan (mode 1 dan 3)

Judul cerita, penulis, dan sumber di bagian atas, lalu setiap bab dipisahkan dengan penanda `#####`.

```
Story Title
by Author Name
Source: https://www.wattpad.com/story/123456789

==================================================

##### Chapter 1 Title #####

Text of chapter 1...

##### Chapter 2 Title #####

Text of chapter 2...
```

### Detail format

| Format | Detail |
|--------|--------|
| `.docx` | Judul cerita menjadi heading utama dan setiap bab otomatis menjadi Heading 1 di halaman baru, sehingga langsung nyaman dibaca di Word atau Google Docs. |
| `.epub` | Cerita menjadi ebook standar dengan daftar isi otomatis per bab, siap dibuka di aplikasi pembaca ebook favoritmu (Google Play Books, Apple Books, Calibre, dan lainnya). |
| `.md` | Cerita ditulis dengan heading Markdown standar (`#` untuk judul, `##` per bab), yang enak dibuka di editor mana pun atau dirender langsung di GitHub/Obsidian/Notion. |

Jika cerita punya sampul, gambarnya disematkan otomatis di halaman/paragraf pertama file `.docx`/`.epub`/`.pdf` (kecuali dijalankan dengan `--no-cover`). Genre/tag, deskripsi, dan tanggal terbit cerita juga disimpan sebagai metadata resmi di file `.epub`, yang biasanya ditampilkan di halaman detail buku pada aplikasi pembaca ebook.

### Isi zip (mode 2)

Satu file per bab, bernomor sesuai posisinya di cerita, plus `000_info.txt`/`000_info.md`/`000_info.docx`/`000_info.epub`/`000_info.pdf` (sesuai format) berisi judul, penulis, dan sumber. Ekstensi file di dalam zip mengikuti format yang kamu pilih saat menjalankan skrip:

```
Story_Title.zip
├── 000_info.txt
├── 001_Chapter_1_Title.txt
├── 002_Chapter_2_Title.txt
└── ...
```

---

## Folder Default per OS

| Sistem Operasi | Folder Default |
|----------------|----------------|
| Windows | `C:\Users\<username>\Downloads` |
| macOS | `/Users/<username>/Downloads` |
| Linux | `/home/<username>/Downloads` |

---

## Pemecahan Masalah

| Masalah | Solusi |
|---------|--------|
| `ModuleNotFoundError: No module named 'requests'` | Jalankan `pip install requests` |
| `ModuleNotFoundError: No module named 'rich'` | Jalankan `pip install rich` |
| `Library 'python-docx' is not installed` | Jalankan `pip install python-docx` (hanya perlu jika memilih format `.docx`) |
| `Library 'EbookLib' is not installed` | Jalankan `pip install EbookLib` (hanya perlu jika memilih format `.epub`) |
| `Library 'reportlab' is not installed` | Jalankan `pip install reportlab` (hanya perlu jika memilih format `.pdf`) |
| Error `404` / "No chapters found" | Pastikan ID/link benar & ceritanya tidak privat |
| Folder tidak bisa dibuat | Periksa bahwa path valid & kamu punya izin tulis di sana |
| Proses macet di satu bab | Periksa koneksi internetmu dan jalankan lagi, progress akan dilanjutkan |

---

## Catatan Penting

- ID cerita adalah angka di URL Wattpad, tepat setelah `/story/`
- Skrip memakai endpoint publik, tanpa login atau API key
- Jeda **0,5 detik** antar bab diatur untuk menghindari rate limit server, mohon jangan dihapus
- Skrip ini hanya untuk membaca ceritamu sendiri atau cerita publik secara offline. Hormati hak cipta para penulis

---

## Dibangun Dengan

<div align="center">

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/-Requests-FF6B6B?style=flat-square)
![Rich](https://img.shields.io/badge/-Rich-FAE742?style=flat-square)
![python--docx](https://img.shields.io/badge/-python--docx-2B579A?style=flat-square)
![Wattpad API](https://img.shields.io/badge/-Wattpad%20Public%20API-FF6122?style=flat-square)

</div>

---

## Struktur Proyek

```
wattpdl/
├── src/
│   └── wattpdl/
│       ├── __init__.py       # metadata paket (__version__)
│       ├── __main__.py       # entry point untuk `python -m wattpdl`
│       ├── app.py            # orkestrasi alur program (main())
│       ├── api.py            # komunikasi dengan API publik Wattpad
│       ├── writers.py        # konversi teks & penulisan file .txt/.docx/.epub/.md/.pdf/.zip
│       ├── cli.py            # tampilan terminal (rich), interaksi pengguna
│       ├── cli_args.py       # parsing argumen untuk mode non-interaktif
│       ├── config.py         # menyimpan preferensi pengguna (folder simpan, format, bahasa)
│       ├── i18n.py           # terjemahan tampilan CLI (en/id)
│       └── progress.py       # cache progress unduhan untuk fitur resume
├── requirements.txt          # daftar dependensi (untuk referensi manual)
├── pyproject.toml            # metadata paket + konfigurasi build + ruff
├── tests/
│   ├── __init__.py
│   └── test_wattpdl.py       # unit test (pytest)
├── .github/
│   └── workflows/
│       ├── tests.yml         # CI: tes otomatis, lint, & cek build
│       └── publish.yml       # publikasi otomatis ke PyPI saat ada rilis baru
├── CONTRIBUTING.md           # panduan kontribusi (Inggris)
├── CONTRIBUTING.id.md        # panduan kontribusi (Indonesia)
├── LICENSE
├── README.md                 # dokumentasi utama (Inggris)
└── README.id.md              # dokumentasi (Indonesia)
```

### Prinsip pemisahan modul

| Modul | Prinsip |
|-------|---------|
| `api.py` | Tidak tahu apa-apa soal tampilan (`rich`), murni mengambil data |
| `writers.py` | Tidak melakukan request jaringan, murni mengonversi & menulis file |
| `cli.py` | Semua interaksi pengguna & tampilan progress bar |
| `cli_args.py` | Parsing & validasi argumen command line, tanpa logika bisnis |
| `i18n.py` | Kamus teks tampilan (Inggris/Indonesia), murni data, tidak tahu apa-apa soal `rich` atau jaringan |
| `config.py` / `progress.py` | Baca/tulis file JSON di `~/.wattpdl/`, tidak tahu apa-apa soal CLI atau jaringan |
| `app.py` | Menyatukan semuanya, tanpa logika bisnis sendiri (dipanggil lewat perintah `wattpdl` setelah instalasi) |

---

## Pengujian

Ada unit test untuk fungsi inti (parsing ID cerita, validasi nama file, parsing pilihan bab, konversi HTML ke teks, config, progress/resume, parsing argumen CLI, terjemahan, dan lainnya).

```bash
pip install -e .[dev]
pytest tests/ -v
ruff check .
```

---

## Continuous Integration

| Workflow | Fungsi |
|----------|--------|
| `tests.yml` | Tes otomatis, lint, & cek build |
| `publish.yml` | Publikasi otomatis ke PyPI saat ada rilis baru |

---

## Kontribusi

Ingin membantu menyempurnakan WattPDL? Baca [`CONTRIBUTING.id.md`](https://github.com/nekonaru/wattpdl/blob/main/CONTRIBUTING.id.md) untuk struktur proyek dan alur kontribusi.

---

## FAQ

<details>
<summary><b>Apakah ini legal / aman dipakai?</b></summary>

Skrip ini memakai endpoint publik Wattpad yang sama seperti saat kamu membaca cerita di browser, jadi tidak meretas apa pun. Tetapi pakailah dengan bertanggung jawab: unduh untuk bacaan pribadi/offline, dan hormati hak cipta para penulis. Jangan menyebarluaskan atau menjual cerita orang lain.

</details>

<details>
<summary><b>Apakah saya perlu akun Wattpad?</b></summary>

Tidak. Sama sekali tidak perlu login atau API key.

</details>

<details>
<summary><b>Bisakah mengunduh cerita privat / yang sudah dihapus?</b></summary>

Tidak. Skrip hanya bisa mengakses cerita yang bersifat publik.

</details>

<details>
<summary><b>Kenapa lama sekali?</b></summary>

Ada jeda 0,5 detik antar bab (sengaja, agar server Wattpad tidak kelebihan beban). Untuk cerita dengan ratusan bab, wajar jika prosesnya memakan beberapa menit. Kamu bisa mempercepatnya dengan `--workers`.

</details>

<details>
<summary><b>Mode dan format mana yang sebaiknya dipilih?</b></summary>

- Ingin membaca dari awal sampai akhir seperti buku: **Mode 1**, format `.epub` paling nyaman di aplikasi ebook
- Ingin setiap bab sebagai file sendiri: **Mode 2**
- Hanya butuh beberapa bab tertentu (misalnya membaca ulang bagian tertentu): **Mode 3**
- Hanya penasaran dengan satu bab: **Mode 4**
- Ingin membaca santai di ponsel/tablet dengan aplikasi ebook (Google Play Books, Apple Books, dll.): pilih format **`.epub`**
- Ingin mengedit atau mencetak dengan rapi lewat Word: pilih format **`.docx`**
- Ingin file kecil dan sederhana, atau membacanya di e-reader/aplikasi catatan: pilih format **`.txt`**

</details>

---

## Penulis

<div align="center">

| [![Nicolas Dwi Dharma](https://github.com/github.png?size=100)](https://github.com/nekonaru) |
|:---:|
| **Nicolas Dwi Dharma** |
| [github.com/nekonaru](https://github.com/nekonaru) |

</div>

---

## Lisensi

Didistribusikan di bawah **Lisensi MIT**. Lihat [`LICENSE`](https://github.com/nekonaru/wattpdl/blob/main/LICENSE) untuk informasi lebih lanjut.
