# Changelog

Semua perubahan penting project ini didokumentasikan di file ini. Formatnya mengikuti release notes; lihat [CHANGELOG.md](CHANGELOG.md) untuk versi English.

## v2.0.1

Audit dan penyempurnaan atas fitur yang ada. Tidak ada perintah baru.

### Peningkatan

- **Cek library lebih cepat.** `--check-updates` dan `--update-library` kini mengecek hingga empat cerita secara bersamaan (urutan tetap terjaga), tidak lagi menunggu satu per satu.
- **Lebih sedikit penulisan config.** Alur batch menulis preferensi sekali per sesi, bukan sekali per cerita.
- **Tidak ada request jaringan sebelum validasi argumen.** Perintah yang salah kini gagal langsung, tanpa cek update PyPI lebih dulu.
- **Ringkasan dry-run yang jujur.** Batch dry-run menampilkan "Simulation: N stories ready to download", bukan "downloaded".
- **Kebersihan test.** Test yang memanggil `run_download` langsung kini mengisolasi `config.json`; preferensi asli pemilik tidak lagi tersentuh oleh suite test.

## v2.0.0

Arsitektur, schema config, supply chain, dan akhirnya dukungan Python 3.9.

### Breaking changes

- **Python 3.9 tidak lagi didukung.** Minimal sekarang Python 3.10 (`requires-python >=3.10`; CI menguji 3.10 sampai 3.13). Python 3.9 mencapai akhir dukungan pada 2025.
- **Schema config v2.** `~/.wattpdl/config.json` kini memuat `"version": 2`. File config lama dimigrasikan otomatis saat dibaca; skrip manual yang menulis file itu sebaiknya menyertakan versi.

### Peningkatan

- **`app.py` dipecah menjadi paket `flows/`.** `common.py`, `download.py`, `single.py`, `batch.py`, `library.py`, dan `tooling.py` masing-masing menguasai satu bagian CLI; `app.py` kini facade tipis. Tidak ada perilaku perintah yang berubah. Coverage test 84%.
- **Supply chain.** Ditambahkan snapshot dependency dengan hash (`requirements.lock.txt`, dari `pip-compile --generate-hashes`) dan SBOM CycloneDX (`sbom.json`). Pre-commit sekarang menjalankan pemindai rahasia lokal untuk file yang di-stage.

## v1.12.0

Filter search, penemuan via JSON, riwayat unduhan, opsi PDF/EPUB, dan perbaikan endpoint penulis yang rusak.

### Fitur baru

- **Filter search.** `--search-status completed|ongoing`, `--search-min-chapters N`, `--search-sort votes|chapters|title`, dan `--search-language NAME` menyaring serta mengurutkan hasil di sisi klien (API search Wattpad mengabaikan parameter tersebut). `--search --json` mencetak hasil sebagai JSON.
- **Info penulis.** `--author-info USER` menampilkan cerita seorang penulis beserta total chapter tanpa mengunduh. `--author-info --json` mencetak JSON.
- **Riwayat unduhan.** Unduhan sukses tercatat di `~/.wattpdl/history.json`; `--history` dan `--history --json` menampilkannya. `--no-library` melewati pencatatan di library maupun riwayat.
- **Tampilan PDF.** `--pdf-pagesize A4|A5` dan `--pdf-font-size N` (6-24) mengatur PDF yang dihasilkan.
- **Metadata EPUB.** URL cerita sumber dan status Completed/Ongoing kini ditulis sebagai metadata Dublin Core.
- **Watch untuk scripting.** `--watch-notify-json` mencetak satu baris JSON per chapter baru; `--watch-max-iterations N` kini didokumentasikan dan tersedia.

### Perbaikan bug

- **Unduhan per penulis berfungsi lagi.** Endpoint Wattpad yang dipakai `--user` adalah `/users/{username}/stories/published`, yang mengembalikan 404 untuk semua penulis nyata. Sekarang `/users/{username}/stories`, diverifikasi langsung; `--user` dan `--author-info` memakainya.
- **`--author-info` tidak crash lagi** saat menerima 404 dari penulis yang dihapus atau private; pesan jelas ditampilkan.

## v1.11.0

Beberapa format sekaligus, laporan unduhan, tooling CLI, dan audit yang menaikkan coverage test.

### Fitur baru

- **Beberapa format dari satu unduhan.** `--format txt,epub` atau `--format all` menulis semua output dari chapter yang sama. Pada mode 2, tiap format mendapat zip tersendiri.
- **Laporan unduhan.** `--report PATH.json` atau `.csv` mencatat ID cerita, judul, mode, format, jumlah chapter, waktu, dan path output untuk semua unduhan dalam satu sesi.
- **Perintah preferensi.** `--config` menampilkan preferensi tersimpan; `--config-set file_format=epub` mengubah salah satu.
- **Doctor.** `--doctor` mengecek dependency, folder data, preferensi, dan konektivitas API Wattpad dalam satu perintah.
- **Shell completion.** `--completion bash|zsh|fish|powershell` mencetak script completion untuk flag wattpdl.
- **Quiet / verbose.** `--quiet` menekan output normal untuk cron; `--verbose` mencetak opsi yang aktif.

### Peningkatan

- **File output atomik.** Writer sekarang menulis ke file sementara di folder tujuan lalu memindahkannya saat sukses, jadi crash tidak menyisakan file setengah jadi.
- **Coverage test naik** dari 69% menjadi 82% (307 test), dengan batas minimum 80% di CI.

## v1.10.0

Batch unduhan dari file dan nama file custom, plus audit round.

### Fitur baru

- **Batch dari file.** `--file PATH` mengunduh semua cerita di file, satu ID atau link per baris (`#` untuk komentar), dalam mode 1 atau 2. Cerita yang gagal dilewati dan dilaporkan di akhir, tidak menghentikan yang lain.
- **Nama file custom.** `--filename "Seri Saya - Buku 1"` mengganti nama dasar file output untuk unduhan satu cerita (`--id`).

### Perbaikan bug

- **Judul panjang multibyte tidak lagi melebihi batas nama file.** `safe_filename` sekarang membatasi berdasarkan byte UTF-8 (100 byte, bukan 100 karakter), jadi judul CJK dan karakter multibyte lain tidak akan melebihi batas 255 byte di Linux/macOS.
- **Batch tidak lagi berhenti saat cerita dihapus atau di-private.** `--user` sekarang melewati cerita yang tidak bisa diambil (dengan warning) dan lanjut ke yang lain, seperti yang sudah dilakukan `--update-library`. Ringkasan kegagalan ditampilkan di akhir.
- **Disk penuh atau read-only tidak lagi gagal di tengah chapter.** Penulisan progress resume sekarang best-effort; chapter tetap dihitung berhasil diunduh.
- **Preferensi tersimpan dengan format file tidak dikenal jatuh kembali ke `txt`** alih-alih diteruskan apa adanya.
- **Connection pooling HTTP sekarang sesuai worker maksimum** (50, bukan 10), sehingga `--workers` besar tetap memakai ulang koneksi.

## v1.9.0

Hasil search sekarang ditampilkan per halaman, 10 cerita per halaman.

### Fitur baru

- **Search paging.** Hasil `--search` ditampilkan 10 per halaman; ketik `n` untuk halaman berikutnya dan `p` untuk halaman sebelumnya. Nomor indeks global untuk semua halaman, jadi cerita #13 selalu dipilih dengan mengetik `13` di halaman mana pun, dan `--select` memakai nomor global yang sama di mode non-interaktif.
- **`--search-limit N`** mengatur berapa banyak hasil yang diambil (default 40, maksimal 100). Query yang sangat populer tidak lagi terhenti di 10 teratas.

## v1.8.1

### Perbaikan bug

- **--output-dir sekarang berlaku di mode interaktif.** Menekan Enter pada prompt folder simpan menyimpan ke folder yang diberikan lewat `--output-dir`; sebelumnya flag ini diabaikan diam-diam di mode interaktif dan folder default dari config tersimpan yang dipakai.

## v1.8.0

Cari cerita Wattpad dan unduh fanfic berdasarkan indeks.

### Fitur baru

- **Cari cerita.** `--search "<query>"` menampilkan cerita yang cocok dengan diberi nomor (judul, penulis, jumlah chapter, status) memakai search publik Wattpad. Tanpa `--select`, kamu ditanya indeks mana yang diunduh (bisa rentang seperti `1-8,10`, atau `all`). Untuk scripting, langsung isi: `--search "query" --select 1-8,10 --mode 1`. Hanya mode 1 dan 2, seperti `--user`.

## v1.7.0

Library management, info cerita, dan HTTP tuning untuk power user, plus security hardening.

### Fitur baru

- **Library management.** `--library` menampilkan semua cerita yang tercatat pernah diunduh penuh; `--library-forget <id>` berhenti memantau satu cerita.
- **`--update-library`.** Unduh ulang semua cerita tercatat yang punya chapter baru di Wattpad dengan satu perintah; progress resume disimpan, jadi hanya chapter baru yang diunduh.
- **`--check-updates` dan `--library --json`.** Keduanya bisa mencetak JSON machine-readable untuk scripting dan otomatisasi.
- **`wattpdl --info --id <id>`.** Menampilkan detail cerita (penulis, jumlah chapter, status, genre, deskripsi) tanpa mengunduh.
- **`--retries N` dan `--timeout N`.** Mengatur jumlah retry HTTP per chapter (default 3, maksimal 10) dan timeout setiap request HTTP (default 20 detik).
- **`--dry-run`.** Simulasi unduhan: menampilkan file tujuan, berapa chapter dipilih, dan berapa yang dipakai ulang dari resume cache, tanpa menulis apa pun.

### Perbaikan bug

- **Console Windows lama tidak crash lagi.** Stdout dan stderr dikonfigurasi ulang ke UTF-8 saat start dengan fallback lossy; sebelumnya banner dan step marker memicu UnicodeEncodeError di console cp1252.
- **Gambar inline tidak bisa menjangkau jaringan internal.** Unduhan dari host yang bukan global routeable (loopback, range privat, link-local termasuk endpoint metadata cloud, CGNAT) ditolak, scheme wajib http/https, dan gambar dibatasi 25 MB.
- **File cache rusak tidak crash lagi.** Loader library, progress, config, metadata-cache, dan update-check sekarang mewajibkan JSON object di top-level dan memperlakukan selain itu sebagai kosong.
- **Validasi argumen lebih ketat.** `--user` hanya menerima username Wattpad yang valid, `--watch-interval` minimal 1 detik, `--retries` maksimal 10, dan `--json` ditolak di luar `--library`/`--check-updates`.

### Peningkatan

- **CI/CD diperketat.** GitHub Actions di-pin ke commit SHA, permission token dikurangi ke `contents: read` (publish hanya memegang `id-token: write`), pip-audit ditambahkan ke CI, coverage floor 65%, Dependabot untuk pip dan GitHub Actions, branch protection di `main` dengan required checks, dan matrix test berjalan di Python 3.9 sampai 3.12.

## v1.6.0

Connection pooling untuk unduhan lebih cepat, Pillow kini dependency resmi, dan pembersihan internal.

### Peningkatan

- **Connection pooling.** Request HTTP sekarang memakai ulang koneksi TCP/TLS per thread alih-alih handshake baru tiap chapter, mempercepat unduhan panjang, terutama dengan `--workers`.
- **Pillow kini dependency resmi.** Sebelumnya dipakai untuk pemrosesan gambar PDF tapi hanya datang transitive lewat reportlab; `pip install wattpdl` sekarang menjaminnya.
- **Error chapter lebih jelas.** Chapter yang sudah dihapus atau dibatasi (404/403 saat fetch teksnya) sekarang menampilkan pesan sejelas error level cerita.
- **Pembersihan internal.** Shared HTTP session, helper yang diduplikasi diringkas, dan modul dirapikan. Perilaku command line tidak berubah.

### Perbaikan bug

- **Install di Python 3.9 tidak lagi menarik reportlab yang rusak.** reportlab 5 menyatakan mendukung Python 3.9 di metadata-nya tapi gagal import di 3.9; install di Python 3.9 sekarang di-pin ke reportlab 4.x.

## v1.5.0

WattPDL sekarang tampil dalam English secara default dan hadir dengan dokumentasi bilingual English dan Indonesia.

### Fitur baru

- **CLI dalam English dan Indonesia.** Menu, prompt, tabel, progress, warning, pesan error, dan `--help` sekarang bisa diterjemahkan sepenuhnya lewat `--ui-lang en|id`. English menjadi default baru, dan pilihannya diingat.
- **Cara lain mengatur bahasa.** Environment variable `WATTPDL_LANG` dan nilai `ui_lang` di `~/.wattpdl/config.json`. Prioritas: `--ui-lang`, lalu `WATTPDL_LANG`, lalu config, lalu `en`.
- **Dokumentasi dua bahasa.** `README.md` dan `CONTRIBUTING.md` sekarang berbahasa Inggris, dengan versi Indonesia di `README.id.md` dan `CONTRIBUTING.id.md`.

### Breaking changes

- **Bahasa tampilan default sekarang English.** Jalankan `wattpdl --ui-lang id` sekali untuk kembali ke tampilan Indonesia; setelah itu pilihannya diingat.
- **Label di dalam file hasil sekarang berbahasa Inggris.** `oleh` jadi `by`, dan `Sumber` jadi `Source:` di file `.txt`, `.md`, `.docx`, `.epub`, dan `.pdf`. File yang sudah kamu unduh sebelumnya tidak berubah.
- **Nama file default berubah.** Mode 3 sekarang menghasilkan `Story_Title_selected.<ext>` (dulu `_pilihan`), dan judul kosong jatuh ke `wattpad_story` (dulu `cerita_wattpad`). Kalau kamu memakai `--skip-existing` dengan mode 3, cerita itu akan terunduh sekali lagi dengan nama baru.

### Peningkatan

- **Modul i18n baru.** `i18n.py` adalah kamus murni tanpa dependency, dan semua teks yang tampil ke pengguna sekarang lewat `t("key")`; ada test yang memastikan kedua bahasa selalu punya key dan placeholder yang sama.
- **Dokumentasi disinkronkan dengan kode.** Kelima format (`.txt`, `.docx`, `.epub`, `.md`, `.pdf`), tabel argumen lengkap, dan struktur output (termasuk `.pdf`) sekarang terdokumentasi dengan akurat.
- **Komentar dan docstring di kode diterjemahkan ke bahasa Inggris**, dan em dash dihapus dari kode maupun dokumen.
- **21 test baru** untuk penentuan bahasa, terjemahan, dan pesan error yang diterjemahkan, total sekarang **154 test**, semua lolos di Python 3.9 sampai 3.12.

## v1.4.0

Unduhan paralel, rate-limit adaptif, format PDF, gambar inline, unduh per penulis, deteksi chapter baru, dan mode watch.

### Fitur baru

- **Unduh paralel.** `--workers N` mengunduh beberapa chapter sekaligus, mempercepat cerita panjang secara signifikan. Default tetap 1, berurutan dan paling aman.
- **Rate-limit adaptif.** Jeda antar chapter otomatis melambat kalau Wattpad mulai membatasi request (429) atau server sibuk (503), lalu pelan-pelan cepat lagi. Makin terasa manfaatnya kalau dipakai bareng `--workers`.
- **Format PDF.** Format kelima, `.pdf` (pakai `reportlab`). Cover dan gambar inline juga didukung di PDF.
- **Gambar inline.** `--include-images` ikut unduh & sisipkan gambar di dalam teks chapter (bukan cuma cover) ke `.docx`, `.epub`, dan `.pdf`. Gambar yang sangat tinggi (strip webtoon/komik) dipotong per halaman PDF supaya tetap terbaca.
- **Unduh per penulis.** `--user <username>` menampilkan semua cerita seorang penulis dan bisa unduh semuanya (`--user-select all`) atau pilih beberapa (`--user-select 1,3,5-8`).
- **Deteksi chapter baru.** `--check-updates` mengecek semua cerita yang pernah diunduh penuh (tercatat otomatis di `~/.wattpdl/library.json`) dan melaporkan mana saja yang sudah punya chapter baru.
- **Mode watch.** `--watch` memantau 1 cerita terus-menerus (interval lewat `--watch-interval`, default 1800 detik) dan otomatis unduh ulang begitu ada chapter baru. Cocok buat cerita ongoing favorit. Berhenti dengan Ctrl+C.
- **Cache metadata singkat.** Info cerita di-cache 5 menit, jadi menjalankan wattpdl berkali-kali untuk cerita yang sama tidak selalu hit API. Matikan dengan `--no-cache`.
- **Cek update wattpdl otomatis.** Kasih tahu di awal kalau ada versi wattpdl lebih baru di PyPI (cek maksimal sekali sehari, tidak pernah mengganggu proses utama kalau gagal). Matikan dengan `--no-update-check`.
- **Pesan error lebih spesifik.** Cerita dihapus atau ID salah (404) dibedakan dari cerita private atau dibatasi (403).
- **`--version`.** Menampilkan versi wattpdl yang terinstall langsung dari terminal.

### Peningkatan

- **Progress store.** Progress dibaca sekali per sesi dan disimpan di memori, bukan baca-tulis file tiap chapter (sebelumnya O(n kuadrat)); thread-safe untuk unduhan paralel.
- **43 test baru** untuk semua fitur di atas (rate limiter, PDF, gambar inline, `--user`, `--check-updates`, `--watch`, cache, updater), total sekarang **127 test**, semua lolos.
- **Diverifikasi lewat instalasi bersih** di virtualenv baru, bukan cuma environment development, memastikan tidak ada dependency yang kelewatan.

## v1.3.0

Mode non-interaktif, resume otomatis, dan pilih chapter spesifik.

### Fitur baru

- **Mode non-interaktif.** Isi `--id` dan wattpdl langsung jalan tanpa prompt sama sekali, cocok dipanggil dari cron job, script lain, atau CI. Kalau `--id` kosong, tetap jalan interaktif seperti biasa.
- **Resume otomatis.** Kalau proses unduh terhenti di tengah jalan (koneksi putus, terminal ditutup, laptop mati), proses selanjutnya dengan cerita yang sama melanjutkan dari chapter terakhir yang berhasil, bukan mengulang dari awal. Progress disimpan per cerita di `~/.wattpdl/progress/`.
- **Pilih chapter spesifik.** Dua mode baru: `--mode 3` untuk pilih beberapa chapter sekaligus (`--chapters 1,3,5-8`) digabung jadi 1 file, dan `--mode 4` untuk unduh cuma 1 chapter (`--chapter 5`).
- **Dukungan format `.md`.** Format keempat, `.md`; format yang tersedia sekarang `.txt`, `.docx`, `.epub`, `.md`.
- **Preferensi tersimpan.** Folder simpan & format terakhir otomatis diingat di `~/.wattpdl/config.json`, jadi tidak perlu diisi ulang tiap kali (bisa di-override kapan saja lewat `--output-dir`/`--format`).
- **`--skip-existing`.** Lewati file yang sudah ada alih-alih menimpanya, berguna buat unduh massal terjadwal.
- **`--no-cover`.** Opsi untuk mematikan penyisipan cover ke `.docx`/`.epub` kalau tidak perlu.

### Perbaikan bug

- **Crash di Python 3.9.** Anotasi tipe `bytes | None` (sintaks Python 3.10+) dipakai tanpa sadar padahal project mendukung Python 3.9+; diganti ke `Optional[bytes]`.
- **CLI hang kalau salah ketik rentang chapter.** `--chapters 1-500000000` (atau typo kelebihan nol) sekarang dipangkas ke jumlah chapter asli sebelum diiterasi.
- **Crash "File name too long".** Mode 4 menggabungkan judul cerita dan judul chapter jadi satu nama file, yang bisa melebihi batas OS dan crash di detik terakhir; nama file sekarang dipotong ke panjang aman dengan penanganan error yang rapi.
- **Nama file bentrok dengan reserved device Windows.** Judul chapter yang cuma satu kata seperti `Con`, `Aux`, `Nul`, atau `Com1` otomatis diberi prefix supaya bisa disimpan di Windows.

### Peningkatan

- **Test regresi untuk keempat fix di atas**, total sekarang **82 test**, semua lolos di Python 3.9 sampai 3.12.

## v1.2.1

Perbaikan bug hasil audit menyeluruh, plus pembersihan struktur project.

### Perbaikan bug

- **Koneksi gagal jadi traceback mentah.** Error jaringan (putus/timeout) sekarang tampil sebagai pesan error yang jelas.
- **Identifier EPUB duplikat.** Mode zip-per-chapter dulu menghasilkan semua file EPUB dengan identifier yang sama persis (melanggar spec EPUB, bisa bikin Calibre/Kobo bentrok); sekarang tiap file punya identifier unik.
- **Chapter kosong tanpa peringatan.** Retry chapter dengan `retries=0` dulu diam-diam menyimpan chapter kosong; sekarang langsung dikasih error yang jelas.
- **Crash saat folder simpan gagal dibuat.** Fallback ke folder default sekarang ditangani juga kalau ternyata ikut gagal (misal home directory read-only).
- **Link chapter Wattpad tidak dikenali.** Link per-chapter (format mobile/share) sekarang dikasih pesan spesifik ("ini link chapter, bukan link cerita").

### Peningkatan

- **Hapus 7 file legacy** di root repo (`api.py`, `cli.py`, `writers.py`, dll), sisa dari sebelum direstruktur ke `src/wattpdl/`.
- **README dirapikan.** ASCII art banner dihapus.
- **8 test baru** meng-cover kelima fix di atas, total **62 test**, semua lolos di Python 3.9 sampai 3.12.
- **CI matrix tidak lagi fail-fast**, supaya semua versi Python jalan sampai selesai walau salah satu gagal.

## v1.2.0

Dukungan format EPUB.

### Fitur baru

- **Format EPUB.** Unduh cerita langsung jadi ebook, lengkap dengan daftar isi (table of contents) otomatis per chapter. Tinggal buka di Google Play Books, Apple Books, Calibre, atau aplikasi e-reader favoritmu.

Semua mode unduh (gabungan, terpisah/zip, pilih beberapa chapter, satu chapter) sekarang mendukung tiga format: `.txt`, `.docx`, dan `.epub`.

## v1.1.0

Resume, config tersimpan, mode non-interaktif, dan rilis pertama di PyPI.

### Fitur baru

- **Resume otomatis.** Chapter yang sudah berhasil diunduh tidak diunduh ulang kalau proses terhenti di tengah jalan.
- **Config tersimpan.** Folder simpan & format file terakhir otomatis dipakai lagi di sesi berikutnya.
- **Mode non-interaktif.** Bisa dijalankan lewat argumen command line untuk scripting/otomatisasi.
- **Tersedia di PyPI.** `pip install wattpdl`, lalu jalankan `wattpdl` dari terminal mana saja.

### Peningkatan

- **src layout.** Kode direstruktur ke `src/wattpdl/` (standar packaging Python) supaya bisa di-publish ke PyPI.

## v1.0.0

Rilis pertama WattPDL, Wattpad Story Downloader.

### Fitur baru

- **4 mode unduh.** Semua jadi 1 file, semua terpisah (`.zip`), pilih beberapa chapter, atau 1 chapter saja.
- **2 format output.** `.txt` polos atau `.docx`.
- **Progress bar interaktif** dengan persentase dan estimasi waktu tersisa.
- **Auto-retry.** Chapter yang gagal dicoba ulang hingga 3x sebelum dilewati.
- **Tanpa login.** Endpoint publik Wattpad, tidak butuh akun.

### Peningkatan

- **Modular.** Dipecah jadi `api.py`, `writers.py`, dan `cli.py` biar lebih mudah dikembangkan.
- **Kualitas.** 29 unit test (pytest), linting otomatis via `ruff`, dan CI (GitHub Actions) jalan di tiap push/PR.
