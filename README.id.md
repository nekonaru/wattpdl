<div align="center">
  <img src="assets/logo.png" alt="WattPDL logo" width="120" />
  <h1>WattPDL: Wattpad Story Downloader</h1>
  <p><b>Simpan cerita Wattpad sebagai file .txt, .docx, .epub, .md, atau .pdf untuk dibaca offline,<br/>
  utuh atau per chapter, tanpa login dan tanpa API key.</b></p>

  <a href="https://github.com/nekonaru/wattpdl/releases"><img src="https://img.shields.io/github/v/release/nekonaru/wattpdl?style=flat-square&color=blue" alt="Release" /></a>
  <a href="https://github.com/nekonaru/wattpdl/actions/workflows/tests.yml"><img src="https://github.com/nekonaru/wattpdl/actions/workflows/tests.yml/badge.svg" alt="CI" /></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status" />
</div>

<br />

[English](README.md) | **Bahasa Indonesia**

> [!NOTE]
> WattPDL hanya untuk membaca cerita milik sendiri atau cerita publik secara offline. Hormati hak cipta penulis: jangan sebar ulang atau jual cerita yang sudah diunduh.

---

## Daftar Isi

- [Tentang](#tentang)
- [Fitur](#fitur)
- [Kebutuhan](#kebutuhan)
- [Instalasi](#instalasi)
- [Cara Pakai](#cara-pakai)
- [Bahasa Tampilan](#bahasa-tampilan)
- [Sumber Data](#sumber-data)
- [Struktur Project](#struktur-project)
- [Pengembangan](#pengembangan)
- [Testing](#testing)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Author](#author)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Tentang

**WattPDL** adalah script Python ringan yang mengunduh chapter dari cerita Wattpad pilihanmu, lalu menyimpannya sebagai file `.txt` polos, dokumen Word `.docx`, ebook `.epub`, Markdown `.md`, atau `.pdf` yang bersih dan rapi. Kamu bisa unduh seluruh cerita jadi satu file, semua chapter terpisah dalam satu `.zip`, atau cukup chapter tertentu yang kamu pilih sendiri, lengkap dengan cover cerita yang otomatis disisipkan ke `.docx`/`.epub`/`.pdf`. Tidak perlu login, tidak perlu API key, cukup link atau ID ceritanya.

> _"Karena cerita yang bagus layak dibaca kapan saja, bahkan tanpa internet."_

---

## Fitur

### Mode Unduh

| Fitur | Keterangan |
|-------|------------|
| **4 mode unduh** | Semua jadi 1 file, semua terpisah dalam `.zip`, pilih beberapa chapter, atau cukup 1 chapter |
| **Unduh per penulis** | `--user <username>` mengunduh semua/cerita pilihan dari satu penulis sekaligus |
| **Mode non-interaktif** | Bisa dijalankan lewat argumen command line untuk scripting/otomatisasi, tanpa perlu jawab prompt |
| **Resume otomatis** | Kalau proses terhenti di tengah jalan, jalankan ulang cerita yang sama, chapter yang sudah berhasil tidak diunduh ulang |
| **Skip file yang sudah ada** | Lewati unduhan kalau file output sudah ada di folder tujuan, tidak menimpa tanpa sengaja |

### Format dan Output

| Fitur | Keterangan |
|-------|------------|
| **5 pilihan format** | Simpan sebagai `.txt` polos, dokumen Word `.docx`, ebook `.epub`, Markdown `.md`, atau `.pdf` |
| **Cover otomatis** | Gambar sampul cerita disisipkan ke file `.docx`/`.epub`/`.pdf` (bisa dimatikan lewat `--no-cover`) |
| **Gambar inline** | Opsional (`--include-images`) ikut unduh & sisipkan gambar di dalam teks chapter, bukan cuma cover. Gambar yang sangat tinggi (strip webtoon/komik) dipotong per halaman PDF supaya tetap terbaca |
| **Metadata EPUB lengkap** | Genre/tag, deskripsi cerita, dan tanggal terbit ikut tersimpan sebagai metadata buku |
| **`--lang`** | Set kode bahasa metadata EPUB (default `id`) untuk cerita berbahasa lain |
| **Link sumber tersimpan** | URL cerita dicantumkan di header file hasil |
| **Nama file aman** | Karakter ilegal otomatis dihapus dari nama file |
| **Pilih folder simpan** | Default ke folder `Downloads` sistem, bisa dikustomisasi |

### Keandalan dan Performa

| Fitur | Keterangan |
|-------|------------|
| **Tanpa login** | Pakai endpoint publik Wattpad, jadi tidak butuh akun |
| **Auto-retry** | Chapter gagal dicoba ulang hingga 3x sebelum dilewati |
| **Unduh paralel** | `--workers N` mengunduh beberapa chapter sekaligus, mempercepat cerita panjang secara signifikan |
| **Rate-limit adaptif** | Jeda antar chapter otomatis melambat kalau Wattpad mulai membatasi (429/503), lalu pelan-pelan cepat lagi |
| **Cache metadata** | Info cerita di-cache singkat supaya percobaan berulang dalam waktu dekat tidak selalu hit API |
| **Pesan error spesifik** | Bedakan pesan untuk cerita dihapus (404) vs private/dibatasi (403) |

### Otomatisasi

| Fitur | Keterangan |
|-------|------------|
| **Deteksi chapter baru** | `--check-updates` melaporkan cerita ongoing mana saja yang sudah punya chapter baru |
| **Mode watch** | `--watch` memantau 1 cerita terus-menerus, otomatis unduh ulang begitu ada chapter baru |
| **Cek update wattpdl** | Beri tahu otomatis kalau ada versi wattpdl lebih baru di PyPI |

### Antarmuka dan Pengalaman

| Fitur | Keterangan |
|-------|------------|
| **Tampilan CLI rapi** | Panel, tabel info cerita, dan warna berkat library `rich` |
| **English dan Indonesian UI** | Tampilan CLI (menu, pesan, dan `--help`) dalam English (default) dan Bahasa Indonesia; ganti dengan `--ui-lang id` atau `--ui-lang en` |
| **Progress bar animasi** | Spinner, persentase, jumlah chapter, dan estimasi waktu tersisa |
| **Ringkasan akhir** | Panel laporan chapter yang gagal (jika ada) setelah selesai |
| **Ingat preferensi** | Folder simpan, format file, dan bahasa tampilan terakhir otomatis dipakai lagi di sesi berikutnya |

---

## Kebutuhan

| Dependency | Minimal Versi | Catatan |
|------------|---------------|---------|
| **Python** | 3.9 | Runtime; Windows, macOS, atau Linux |
| **Koneksi internet** | - | Dibutuhkan untuk mengakses public API Wattpad |
| **requests** | 2.31 | HTTP client |
| **rich** | 13.7 | Tampilan terminal |
| **python-docx** | 1.1 | Output `.docx` |
| **EbookLib** | 0.18 | Output `.epub` |
| **reportlab** | 4.0 | Output `.pdf` |
| **pillow** | 10.0 | Pemrosesan gambar untuk output `.pdf` |

Library-library ini otomatis terinstall bareng `wattpdl`, tidak perlu diinstall manual.

> [!TIP]
> Kalau kamu cuma mau pakai wattpdl, tidak perlu install library-nya manual. `pip install wattpdl` menarik semuanya.

### Belum pernah pakai terminal? Mulai di sini

<details>
<summary><b>Cara buka terminal di Windows</b></summary>

1. Tekan tombol **Windows**, ketik `PowerShell`, lalu tekan **Enter**
2. Jendela hitam/biru akan terbuka. Itu tempat kamu mengetik perintah
3. Semua perintah `python ...` atau `pip ...` di panduan ini diketik di jendela itu, lalu tekan **Enter**

</details>

<details>
<summary><b>Cara buka terminal di macOS</b></summary>

1. Tekan **Cmd + Spasi**, ketik `Terminal`, lalu tekan **Enter**
2. Ketik perintah-perintah di panduan ini di situ, lalu tekan **Enter**

</details>

<details>
<summary><b>Cara buka terminal di Linux</b></summary>

Tekan **Ctrl + Alt + T**, atau cari aplikasi "Terminal" di menu aplikasi.

</details>

### Belum punya Python?

1. Buka [python.org/downloads](https://www.python.org/downloads/) dan unduh versi terbaru
2. **Khusus Windows**: saat instalasi, centang dulu kotak **"Add Python to PATH"** di layar pertama sebelum klik Install. Kalau ini kelewat, perintah `python` nanti tidak akan dikenali
3. Setelah selesai install, buka terminal (lihat panduan di atas) lalu cek dengan:

```bash
python --version
# atau
python3 --version
```

Kalau muncul angka versi (misal `Python 3.12.1`), berarti sudah siap.

---

## Instalasi

### Cara A: Install dari PyPI (paling gampang)

1. Buka terminal (lihat [Belum pernah pakai terminal? Mulai di sini](#belum-pernah-pakai-terminal-mulai-di-sini))
2. Install wattpdl:

```bash
pip install wattpdl
```

3. Verifikasi hasil install:

```bash
wattpdl --version
```

> Kalau `pip` tidak dikenali, coba:
> ```bash
> python -m pip install wattpdl
> ```

> Kalau muncul error `externally-managed-environment` (biasanya di Linux):
> ```bash
> pip install wattpdl --break-system-packages
> ```

Setelah terinstall, command `wattpdl` langsung bisa dipakai dari terminal mana saja, lanjut ke bagian [Cara Pakai](#cara-pakai).

### Cara B: Install dari source (untuk development / mau lihat/ubah kode)

#### 1. Ambil kode project ini

<details>
<summary><b>Punya Git terinstall</b></summary>

```bash
git clone https://github.com/nekonaru/wattpdl.git
cd wattpdl
```

</details>

<details>
<summary><b>Tidak punya Git</b></summary>

1. Buka halaman repository di GitHub
2. Klik tombol hijau **`Code`**, pilih **`Download ZIP`**
3. Ekstrak file ZIP yang terunduh ke folder pilihanmu
4. Di terminal, masuk ke folder hasil ekstrak, contoh:

```bash
cd Downloads/wattpdl-main
```

</details>

#### 2. Install dependency dan verifikasi

```bash
pip install -e .
wattpdl --version
```

> Sama seperti Cara A, tambahkan `--break-system-packages` di akhir kalau muncul error `externally-managed-environment`.

Ini juga mendaftarkan command `wattpdl`, tapi mengambil kodenya langsung dari folder ini, cocok kalau kamu mau modifikasi kode dan langsung lihat hasilnya tanpa install ulang.

#### 3. Jalankan test

```bash
pip install -e .[dev]
pytest tests/ -v
ruff check .
```

### Cara C: Arch Linux (AUR)

Pengguna Arch Linux bisa memasangnya dari AUR. Paketnya dirawat oleh komunitas, yaitu [@Vaishnav-Sabari-Girish](https://github.com/Vaishnav-Sabari-Girish): [`wattpdl` di AUR](https://aur.archlinux.org/packages/wattpdl).

```bash
# Pakai yay
yay -S wattpdl

# Pakai paru
paru -S wattpdl
```

> Paket AUR dirawat terpisah, jadi versi barunya bisa muncul di sana sedikit setelah rilis PyPI.

---

## Cara Pakai

### Pertama kali menjalankan

1. Jalankan:

```bash
wattpdl
```

Tampilan CLI default-nya **English**. Kalau kamu mau Bahasa Indonesia, jalankan `wattpdl --ui-lang id` sekali, pilihannya akan diingat untuk sesi berikutnya (lihat [Bahasa Tampilan](#bahasa-tampilan)). Contoh tampilan di bawah memakai Bahasa Indonesia.

2. Masukkan link atau ID cerita saat diminta:

```
Link atau ID cerita Wattpad: https://www.wattpad.com/story/123456789-judul-cerita
```

atau cukup ID-nya:

```
Link atau ID cerita Wattpad: 123456789
```

ID cerita adalah angka di URL Wattpad, tepat setelah `/story/`.

3. Pilih mode unduh:

```
  1  Semua chapter -> 1 file gabungan
  2  Semua chapter -> file terpisah per chapter, dikemas .zip
  3  Pilih beberapa chapter -> 1 file gabungan
  4  Pilih 1 chapter saja

Pilih mode [1/2/3/4] (1):
```

- **Mode 1**: cara paling umum, seluruh cerita jadi satu file rapi dari chapter pertama sampai terakhir
- **Mode 2**: cocok kalau mau baca per chapter terpisah, hasilnya satu `.zip` berisi file per chapter
- **Mode 3**: muncul daftar semua judul chapter bernomor, lalu ketik nomor yang mau diunduh, bisa gabung koma dan rentang, contoh: `1,3,5-8`
- **Mode 4**: muncul daftar semua judul chapter, ketik satu nomor untuk unduh chapter itu saja

4. Pilih format file:

```
  1  Teks polos (.txt)
  2  Dokumen Word (.docx)
  3  Ebook (.epub)
  4  Markdown (.md)
  5  PDF (.pdf)

Pilih format file [1/2/3/4/5] (1):
```

5. Pilih folder penyimpanan:

```
Folder default: C:\Users\user\Downloads
Tekan Enter untuk pakai folder itu, atau ketik path lain:
```

Tekan **Enter** untuk simpan di `Downloads`, atau ketik path kustom seperti:

- Windows: `D:\Cerita\Wattpad`
- Linux/macOS: `/home/user/cerita`

6. Tunggu proses selesai:

```
⠋ Chapter 24...              ████████████████░░░░░░░░░░░░░░  53.3%  24/45  0:00:12  sisa 0:00:11
```

7. Setelah selesai, muncul panel ringkasan berisi path file yang tersimpan dan jumlah chapter yang berhasil (misal `45/45`). Kalau ada chapter yang gagal, panel itu mendaftarnya.

> [!NOTE]
> Kalau kamu install dari source tanpa `pip install -e .`, jalankan lewat `python -m wattpdl` dari dalam folder `src/`. Tapi cara Editable Install di atas lebih direkomendasikan.

### Pemakaian sehari-hari

- Unduh satu cerita penuh sebagai satu `.epub` untuk cara baca paling nyaman di aplikasi ebook
- Unduh cerita panjang dengan Mode 2 supaya bisa baca per chapter, atau pakai `--workers` untuk mempercepatnya
- Jadwalkan `--mode 1 --skip-existing` dengan cron atau Task Scheduler untuk cerita ongoing yang sering diunduh ulang
- Pakai `--check-updates` untuk lihat cerita ongoing yang sudah diunduh mana saja yang punya chapter baru
- Pakai `--watch` untuk unduh ulang otomatis begitu ada chapter baru

### Struktur output

Nama dan bentuk file yang dihasilkan tergantung mode & format yang kamu pilih:

| Mode | Format `.txt` | Format `.docx` | Format `.epub` | Format `.md` | Format `.pdf` |
|------|----------------|-----------------|------------------|---------------|---------------|
| 1 - Semua, gabungan | `Judul_Cerita.txt` | `Judul_Cerita.docx` | `Judul_Cerita.epub` | `Judul_Cerita.md` | `Judul_Cerita.pdf` |
| 2 - Semua, terpisah | `Judul_Cerita.zip` (isi: `.txt` per chapter) | `Judul_Cerita.zip` (isi: `.docx` per chapter) | `Judul_Cerita.zip` (isi: `.epub` per chapter) | `Judul_Cerita.zip` (isi: `.md` per chapter) | `Judul_Cerita.zip` (isi: `.pdf` per chapter) |
| 3 - Beberapa chapter | `Judul_Cerita_selected.txt` | `Judul_Cerita_selected.docx` | `Judul_Cerita_selected.epub` | `Judul_Cerita_selected.md` | `Judul_Cerita_selected.pdf` |
| 4 - Satu chapter | `Judul_Cerita_Ch003_Nama_Chapter.txt` | `Judul_Cerita_Ch003_Nama_Chapter.docx` | `Judul_Cerita_Ch003_Nama_Chapter.epub` | `Judul_Cerita_Ch003_Nama_Chapter.md` | `Judul_Cerita_Ch003_Nama_Chapter.pdf` |

**Isi file gabungan (mode 1 & 3):** judul cerita, penulis, dan sumber di bagian atas, lalu tiap chapter dipisah dengan penanda `#####`.

```
Judul Cerita
by Nama Penulis
Source: https://www.wattpad.com/story/123456789

==================================================

##### Judul Chapter 1 #####

Isi teks chapter 1...

##### Judul Chapter 2 #####

Isi teks chapter 2...
```

Di versi `.docx`, judul cerita jadi heading utama dan tiap chapter otomatis jadi Heading 1 dengan halaman baru, tinggal buka di Word atau Google Docs dan langsung enak dibaca.

Di versi `.epub`, cerita jadi ebook standar dengan daftar isi (table of contents) otomatis per chapter, tinggal buka di aplikasi pembaca ebook favoritmu (Google Play Books, Apple Books, Calibre, dll).

Di versi `.md`, cerita ditulis pakai heading Markdown standar (`#` untuk judul, `##` per chapter), enak dibuka di editor apa pun atau di-render langsung di GitHub/Obsidian/Notion.

Kalau cerita punya cover, gambarnya otomatis disisipkan di halaman/paragraf pertama file `.docx`/`.epub`/`.pdf` (kecuali dijalankan dengan `--no-cover`). Genre/tag, deskripsi, dan tanggal terbit cerita juga ikut tersimpan sebagai metadata resmi di file `.epub`, biasa muncul di halaman detail buku pada aplikasi pembaca ebook.

**Isi zip (mode 2):** satu file per chapter, bernomor urut sesuai posisi di cerita, plus `000_info.txt`/`000_info.md`/`000_info.docx`/`000_info.epub`/`000_info.pdf` (sesuai format) berisi judul, penulis, dan sumber. Ekstensi file di dalam zip mengikuti format yang dipilih saat menjalankan script:

```
Judul_Cerita.zip
├── 000_info.txt
├── 001_Judul_Chapter_1.txt
├── 002_Judul_Chapter_2.txt
└── ...
```

### Folder simpan default per OS

| Sistem Operasi | Folder Default |
|----------------|----------------|
| Windows | `C:\Users\<namauser>\Downloads` |
| macOS | `/Users/<namauser>/Downloads` |
| Linux | `/home/<namauser>/Downloads` |

### Resume otomatis

Kalau proses unduh terhenti di tengah jalan (koneksi putus, terminal ditutup, laptop mati), setiap chapter yang **sudah berhasil** diunduh tersimpan otomatis di `~/.wattpdl/progress/<id_cerita>.json`.

Jalankan lagi dengan cerita yang sama (ID/link sama), dan WattPDL akan:

- Melewati chapter yang sudah berhasil (dipakai dari cache, tidak fetch ulang)
- Hanya mengunduh chapter yang belum berhasil / gagal sebelumnya

File progress otomatis dihapus setelah semua chapter berhasil diunduh dalam satu sesi. Kalau mau paksa unduh ulang dari awal, hapus manual folder `~/.wattpdl/progress/`.

> **Beda dengan `--skip-existing`:** resume di atas bekerja di level *chapter* (melanjutkan unduhan yang terhenti di tengah jalan). Sedangkan `--skip-existing` bekerja di level *file output*, kalau file akhirnya (misal `Judul_Cerita.epub`) sudah ada di folder tujuan, seluruh proses unduh dilewati sama sekali, cocok dipakai bareng `cron`/Task Scheduler supaya tidak mengunduh ulang cerita yang sudah pernah selesai diunduh.

### Preferensi tersimpan

Folder simpan, format file, dan bahasa tampilan terakhir yang kamu pilih otomatis tersimpan di `~/.wattpdl/config.json`, dan dipakai lagi sebagai default di sesi berikutnya, gak perlu isi ulang tiap kali jalanin script.

### Mode non-interaktif (scripting/otomatisasi)

Selain mode tanya-jawab, WattPDL juga bisa dijalankan lewat argumen command line, cocok buat dijadwalkan (cron/Task Scheduler) atau dipanggil dari script lain.

```bash
wattpdl --id 398440633 --mode 1 --format docx
```

**Argumen yang tersedia:**

| Argumen | Keterangan |
|---|---|
| `--id` | ID atau link cerita Wattpad. Mengisi ini mengaktifkan mode non-interaktif. |
| `--mode {1,2,3,4}` | 1 = semua jadi 1 file, 2 = semua terpisah `.zip`, 3 = pilih beberapa chapter, 4 = pilih 1 chapter |
| `--format {txt,docx,epub,md,pdf}` | Format file output. Default: dari config tersimpan, atau `txt` |
| `--chapters` | Nomor chapter untuk `--mode 3`, contoh: `1,3,5-8` |
| `--chapter` | Nomor chapter untuk `--mode 4`, contoh: `5` |
| `--output-dir` | Folder penyimpanan custom. Default: dari config tersimpan, atau folder `Downloads` |
| `--skip-existing` | Lewati unduhan kalau file output tujuan sudah ada, alih-alih menimpanya |
| `--no-cover` | Jangan sisipkan gambar sampul cerita ke file `.docx`/`.epub`/`.pdf` |
| `--include-images` | Ikut unduh & sisipkan gambar inline di dalam chapter (menambah waktu unduh) |
| `--workers N` | Jumlah chapter yang diunduh bersamaan (default 1) |
| `--no-cache` | Jangan pakai cache metadata cerita, selalu ambil data terbaru |
| `--lang` | Kode bahasa ISO 639-1 untuk metadata EPUB (default `id`) |
| `--ui-lang {id,en}` | Bahasa tampilan CLI (default `en`, diingat setelah dipilih) |
| `--user` / `--user-select` | Unduh dari daftar cerita seorang penulis, bisa memilih cerita tertentu |
| `--check-updates` | Laporkan cerita yang sudah diunduh dan punya chapter baru |
| `--watch` / `--watch-interval` | Pantau satu cerita dan unduh ulang kalau ada chapter baru (jeda cek default 1800 detik) |
| `--no-update-check` | Jangan cek versi wattpdl terbaru di PyPI saat start |
| `--version` | Tampilkan versi wattpdl |

**Contoh lain:**

```bash
# Unduh semua chapter sebagai .zip terpisah
wattpdl --id 398440633 --mode 2 --format txt

# Unduh chapter 1, 3, dan 5-8 saja, jadi 1 file gabungan
wattpdl --id 398440633 --mode 3 --chapters 1,3,5-8 --format docx

# Unduh chapter 10 saja, simpan ke folder custom
wattpdl --id 398440633 --mode 4 --chapter 10 --output-dir "D:\Cerita Wattpad"

# Unduh semua chapter jadi 1 ebook .epub
wattpdl --id 398440633 --mode 1 --format epub

# Unduh sebagai Markdown, lewati kalau filenya sudah ada (cocok untuk dijadwalkan)
wattpdl --id 398440633 --mode 1 --format md --skip-existing

# Lihat semua opsi
wattpdl --help
```

---

## Bahasa Tampilan

Tampilan CLI (menu, prompt, pesan error, dan teks `--help`) tersedia dalam **English** (default) dan **Bahasa Indonesia**.

1. Ganti bahasa tampilan sekali saja:

```bash
wattpdl --ui-lang id              # Bahasa Indonesia, pilihan ini diingat untuk sesi berikutnya
wattpdl --ui-lang en              # kembali ke English
```

2. Atau atur lewat environment variable:

```bash
WATTPDL_LANG=id wattpdl
```

Urutan prioritas: `--ui-lang` -> env `WATTPDL_LANG` -> `ui_lang` di `~/.wattpdl/config.json` -> default `en`.

> `--ui-lang` hanya mengubah tampilan CLI. Jangan tertukar dengan `--lang`, yang mengatur kode bahasa metadata file EPUB.

---

## Sumber Data

WattPDL hanya memakai endpoint publik. Tidak perlu login atau API key.

| Tujuan | Sumber |
|--------|--------|
| Metadata cerita (judul, penulis, daftar chapter, genre, deskripsi, tanggal terbit) | Wattpad public API v3 (`wattpad.com/api/v3`) |
| Teks chapter | Endpoint teks cerita publik Wattpad (`wattpad.com/apiv2/storytext`) |
| Daftar cerita per penulis (`--user`) | Wattpad public API v3 (`wattpad.com/api/v3/users/{username}/stories/published`) |
| Cek update wattpdl | PyPI JSON API (`pypi.org/pypi/wattpdl/json`) |

> [!NOTE]
> Ini endpoint publik, sama seperti yang dipakai browser kamu saat baca cerita di wattpad.com. Aksesnya hanya baca, dan tidak ada akun atau cookie yang dikirim.

---

## Struktur Project

```
wattpdl/
├── assets/
│   └── logo.png             # logo project, dipakai di README
├── src/
│   └── wattpdl/
│       ├── __init__.py       # metadata package (__version__)
│       ├── __main__.py       # entry untuk `python -m wattpdl`
│       ├── app.py            # orkestrasi alur program (main())
│       ├── api.py            # komunikasi ke Wattpad public API
│       ├── writers.py        # konversi teks & penulisan file .txt/.docx/.epub/.md/.pdf/.zip
│       ├── cli.py            # tampilan terminal (rich), interaksi dengan user
│       ├── cli_args.py       # parsing argumen untuk mode non-interaktif
│       ├── config.py         # simpan preferensi user (folder simpan, format, bahasa)
│       ├── i18n.py           # terjemahan tampilan CLI (en/id)
│       ├── library.py        # library lokal cerita yang sudah diunduh (dipakai --check-updates)
│       ├── metacache.py      # cache singkat metadata cerita
│       ├── updater.py        # cek update wattpdl di PyPI
│       └── progress.py       # cache progress unduhan untuk fitur resume
├── requirements.txt          # daftar dependency (untuk referensi manual)
├── pyproject.toml            # metadata package + build config + ruff
├── tests/
│   ├── __init__.py
│   └── test_wattpdl.py       # unit test (pytest)
├── .github/
│   └── workflows/
│       ├── tests.yml         # CI: test, lint, & build check otomatis
│       └── publish.yml       # auto-publish ke PyPI saat rilis baru
├── CHANGELOG.md              # riwayat versi (English)
├── CHANGELOG.id.md           # riwayat versi (Bahasa Indonesia)
├── CONTRIBUTING.md           # panduan kontribusi (English)
├── CONTRIBUTING.id.md        # panduan kontribusi (Bahasa Indonesia)
├── SECURITY.md               # kebijakan pelaporan kerentanan
├── LICENSE
├── README.md                 # dokumentasi utama (English)
└── README.id.md              # dokumentasi (Bahasa Indonesia)
```

**Prinsip pemisahan modul:**

- `api.py`: tidak tahu apa-apa soal tampilan (`rich`), murni fetch data
- `writers.py`: tidak melakukan request jaringan, murni konversi & tulis file
- `cli.py`: semua interaksi dengan user & tampilan progress bar
- `cli_args.py`: parsing & validasi argumen command line, tidak ada logika bisnis
- `i18n.py`: kamus teks tampilan (English/Indonesia), murni data, tidak tahu soal `rich` atau jaringan
- `config.py` / `progress.py`: baca-tulis file JSON di `~/.wattpdl/`, tidak tahu soal CLI atau jaringan
- `app.py`: menyatukan semuanya, tanpa logika bisnis sendiri (dipanggil lewat command `wattpdl` setelah install)

---

## Pengembangan

Dibuat dengan Python, `requests`, `rich`, `python-docx`, `EbookLib`, `reportlab`, dan `pillow`.

### Menambahkan string baru yang tampil ke pengguna

1. Tambahkan string English dan Indonesian berdampingan di `src/wattpdl/i18n.py`
2. Pakai `t("key_milikmu")` di kode, jangan pernah pakai string mentah langsung
3. Jalankan test; test suite mengecek kedua bahasa selalu punya key dan placeholder yang sama

### Menjaga dokumentasi tetap sinkron

1. Update `README.md` dulu, baru `README.id.md`, dalam satu commit
2. Pakai urutan section, tabel, dan callout yang persis sama di kedua file
3. Kalau rilis mengubah perilaku yang tampil ke pengguna, update `CHANGELOG.md` dan `CHANGELOG.id.md` juga

Mau bantu kembangin WattPDL? Baca [`CONTRIBUTING.id.md`](CONTRIBUTING.id.md) untuk struktur project dan alur kontribusi.

---

## Testing

Ada unit test untuk fungsi-fungsi inti (parsing ID cerita, validasi nama file, parsing pilihan chapter, konversi HTML ke teks, config, progress/resume, parsing argumen CLI, terjemahan, dan lainnya).

```bash
pip install -e .[dev]
pytest tests/ -v
ruff check .
```

| Check | Requirement |
|-------|-------------|
| `pytest tests/ -v` | Harus lolos seluruh suite |
| `ruff check .` | Harus melaporkan nol issue |

Aturan lint ada di `pyproject.toml` di bagian `[tool.ruff]` (line-length 110, target Python 3.9).

---

## Continuous Integration

| Workflow | Purpose |
|----------|---------|
| `tests.yml` | ruff lint, pytest di Python 3.9-3.12, dan package build dengan `twine check` di setiap push ke `main`, pull request ke `main`, dan push tag `v*` |
| `publish.yml` | build dan publish ke PyPI lewat trusted publishing (OIDC) setiap GitHub Release dipublish |

Lint, test, dan build check harus hijau sebelum setiap push. Publish ke PyPI hanya terjadi lewat GitHub Release yang dipublish.

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `ModuleNotFoundError: No module named 'requests'` | Jalankan `pip install requests` |
| `ModuleNotFoundError: No module named 'rich'` | Jalankan `pip install rich` |
| `Library 'python-docx' is not installed` | Jalankan `pip install python-docx` (hanya dibutuhkan kalau memilih format `.docx`) |
| `Library 'EbookLib' is not installed` | Jalankan `pip install EbookLib` (hanya dibutuhkan kalau memilih format `.epub`) |
| `Library 'reportlab' is not installed` | Jalankan `pip install reportlab` (hanya dibutuhkan kalau memilih format `.pdf`) |
| `ModuleNotFoundError: No module named 'PIL'` | Jalankan `pip install pillow` (hanya dibutuhkan kalau memilih format `.pdf`) |
| Error `404` / "Tidak ada chapter ditemukan" | Pastikan ID/link benar & cerita tidak di-private |
| Folder tidak bisa dibuat | Cek path valid & kamu punya izin tulis di sana |
| Proses macet di satu chapter | Cek koneksi internet, jalankan ulang, progress akan lanjut |

---

## FAQ

<details>
<summary><b>Apakah ini legal / aman dipakai?</b></summary>

Script ini memakai endpoint publik Wattpad yang sama seperti saat kamu baca cerita lewat browser, jadi tidak meng-hack apa pun. Tapi gunakan secara bertanggung jawab: unduh untuk bacaan pribadi/offline, dan hormati hak cipta penulis. Jangan sebar ulang atau jual isi cerita orang lain.

</details>

<details>
<summary><b>Apakah butuh akun Wattpad?</b></summary>

Tidak. Tidak perlu login atau API key sama sekali.

</details>

<details>
<summary><b>Cerita private / dihapus, bisa diunduh?</b></summary>

Tidak. Script hanya bisa mengakses cerita yang memang publik.

</details>

<details>
<summary><b>Prosesnya lama, kenapa?</b></summary>

Ada jeda 0.5 detik antar chapter (sengaja, biar tidak membebani server Wattpad). Untuk cerita ratusan chapter, wajar kalau prosesnya makan waktu beberapa menit. Kamu bisa mempercepatnya dengan `--workers`.

</details>

<details>
<summary><b>Mode dan format mana yang sebaiknya dipilih?</b></summary>

- Mau baca dari awal sampai akhir kayak buku: **Mode 1**, format `.epub` paling enak dibaca di aplikasi ebook
- Mau tiap chapter jadi file sendiri-sendiri: **Mode 2**
- Cuma butuh beberapa chapter tertentu (misal lagi ulang baca bagian tertentu): **Mode 3**
- Cuma penasaran satu chapter: **Mode 4**
- Mau baca santai di HP/tablet pakai aplikasi ebook (Google Play Books, Apple Books, dll): pilih format **`.epub`**
- Mau edit atau print rapi pakai Word: pilih format **`.docx`**
- Mau file kecil dan simpel, atau mau dibaca di aplikasi e-reader/notes: pilih format **`.txt`**

</details>

---

## Author

<div align="center">

| [![Nicolas Dwi Dharma](https://github.com/nekonaru.png?size=100)](https://github.com/nekonaru) |
|:---:|
| **Nicolas Dwi Dharma** |
| [github.com/nekonaru](https://github.com/nekonaru) |

</div>

---

## Disclaimer

WattPDL adalah project open-source independen dan tidak berafilasi dengan atau didukung oleh Wattpad. Project ini membaca data cerita yang publik lewat endpoint publik Wattpad, hanya untuk bacaan offline pribadi. Hormati hak cipta penulis: jangan sebar ulang, unggah, atau jual cerita yang sudah diunduh.

---

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
