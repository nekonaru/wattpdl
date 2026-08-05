<div align="center">

```
                         ██╗    ██╗ █████╗ ████████╗████████╗██████╗ ██████╗ ██╗     
                         ██║    ██║██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔══██╗██║     
                         ██║ █╗ ██║███████║   ██║      ██║   ██████╔╝██║  ██║██║     
                         ██║███╗██║██╔══██║   ██║      ██║   ██╔═══╝ ██║  ██║██║     
                         ╚███╔███╔╝██║  ██║   ██║      ██║   ██║     ██████╔╝███████╗
                         ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝     ╚═════╝ ╚══════╝
```

### 📖 Wattpad Story Downloader
**Simpan cerita favoritmu jadi file `.txt` atau `.docx`, lengkap atau per chapter, secara offline.**

<br>

![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

</div>

## ✨ Tentang Project

**WattPDL** adalah script Python ringan yang mengunduh chapter dari cerita Wattpad pilihanmu, lalu menyimpannya sebagai file `.txt` atau dokumen Word `.docx` yang bersih dan rapi. Kamu bisa unduh seluruh cerita jadi satu file, semua chapter terpisah dalam satu `.zip`, atau cukup chapter tertentu yang kamu pilih sendiri. Tidak perlu login, tidak perlu API key, cukup link atau ID ceritanya.

> _"Karena cerita yang bagus layak dibaca kapan saja, bahkan tanpa internet."_

## 🎯 Fitur

| Fitur | Keterangan |
|-------|------------|
| 🎨 **Tampilan CLI rapi** | Panel, tabel info cerita, dan warna berkat library `rich` |
| 🧩 **4 mode unduh** | Semua jadi 1 file, semua terpisah dalam `.zip`, pilih beberapa chapter, atau cukup 1 chapter |
| 📄 **2 pilihan format** | Simpan sebagai `.txt` polos atau dokumen Word `.docx` |
| 📁 **Pilih folder simpan** | Default ke folder `Downloads` sistem, bisa dikustomisasi |
| 🔄 **Auto-retry** | Chapter gagal dicoba ulang hingga 3× sebelum dilewati |
| 📊 **Progress bar animasi** | Spinner, persentase, jumlah chapter, dan estimasi waktu tersisa |
| 📋 **Ringkasan akhir** | Panel laporan chapter yang gagal (jika ada) setelah selesai |
| 🗂 **Nama file aman** | Karakter ilegal otomatis dihapus dari nama file |
| 🔗 **Link sumber tersimpan** | URL cerita dicantumkan di header file hasil |
| ⚡ **Tanpa login** | Pakai endpoint publik Wattpad, jadi tidak butuh akun |

## 📦 Requirements

- **Python** 3.7 atau lebih baru
- **Koneksi internet**
- Library: `requests`, `rich`, `python-docx` (hanya perlu kalau mau simpan sebagai `.docx`)

### Belum pernah pakai terminal? Ikuti ini dulu

<details>
<summary><b>🪟 Cara buka terminal di Windows</b></summary>

1. Tekan tombol **Windows**, ketik `PowerShell`, lalu tekan **Enter**
2. Jendela hitam/biru akan terbuka. Itu tempat kamu mengetik perintah
3. Semua perintah `python ...` atau `pip ...` di panduan ini diketik di jendela itu, lalu tekan **Enter**

</details>

<details>
<summary><b>🍎 Cara buka terminal di macOS</b></summary>

1. Tekan **Cmd + Spasi**, ketik `Terminal`, lalu tekan **Enter**
2. Ketik perintah-perintah di panduan ini di situ, lalu tekan **Enter**

</details>

<details>
<summary><b>🐧 Cara buka terminal di Linux</b></summary>

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

## 🚀 Instalasi

**1. Ambil kode project ini**

Pilih salah satu cara:

<details>
<summary><b>Cara A: Punya Git terinstall</b></summary>

```bash
git clone https://github.com/nekonaru/wattpdl.git
cd wattpdl
```

</details>

<details>
<summary><b>Cara B: Tidak punya Git (paling gampang untuk pemula)</b></summary>

1. Buka halaman repository di GitHub
2. Klik tombol hijau **`Code`** → pilih **`Download ZIP`**
3. Ekstrak file ZIP yang terunduh ke folder pilihanmu
4. Di terminal, masuk ke folder hasil ekstrak, contoh:

```bash
cd Downloads/wattpdl-main
```

</details>

**2. Install dependency**
```bash
pip install requests rich python-docx
```

> Kalau `pip` tidak dikenali, coba:
> ```bash
> python -m pip install requests rich python-docx
> ```

> Kalau muncul error `externally-managed-environment` (biasanya di Linux):
> ```bash
> pip install requests rich python-docx --break-system-packages
> ```

> Cuma mau simpan sebagai `.txt` saja? `python-docx` boleh dilewati. Script tetap jalan normal untuk mode `.txt`, dan baru akan minta library ini kalau kamu pilih format `.docx` saat menjalankannya.

## 🖥️ Cara Pakai

**Jalankan script:**
```bash
python wattpdl.py
```

**Masukkan link atau ID cerita saat diminta:**
```
Link atau ID cerita Wattpad: https://www.wattpad.com/story/123456789-judul-cerita
```
atau cukup ID-nya:
```
Link atau ID cerita Wattpad: 123456789
```

**Pilih mode unduh:**
```
  1  Semua chapter → 1 file gabungan
  2  Semua chapter → file terpisah per chapter, dikemas .zip
  3  Pilih beberapa chapter → 1 file gabungan
  4  Pilih 1 chapter saja

Pilih mode [1/2/3/4] (1):
```

- **Mode 1**: cara paling umum, seluruh cerita jadi satu file rapi dari chapter pertama sampai terakhir
- **Mode 2**: cocok kalau mau baca per chapter terpisah, hasilnya satu `.zip` berisi file per chapter
- **Mode 3**: muncul daftar semua judul chapter bernomor, lalu ketik nomor yang mau diunduh, bisa gabung koma dan rentang, contoh: `1,3,5-8`
- **Mode 4**: muncul daftar semua judul chapter, ketik satu nomor untuk unduh chapter itu saja

**Pilih format file:**
```
  1  Teks polos (.txt)
  2  Dokumen Word (.docx)

Pilih format file [1/2] (1):
```

**Pilih folder penyimpanan:**
```
Folder default: C:\Users\user\Downloads
Tekan Enter untuk pakai folder itu, atau ketik path lain:
```
Tekan **Enter** untuk simpan di `Downloads`, atau ketik path kustom seperti:
- Windows: `D:\Cerita\Wattpad`
- Linux/macOS: `/home/user/cerita`

**Tunggu proses selesai:**
```
⠋ Chapter 24...              ████████████████░░░░░░░░░░░░░░  53.3%  24/45  0:00:12  sisa 0:00:11
```

**Done! 🎉**
```
╔══════ 🎉 Berhasil!  Semua chapter tersimpan ══════╗
║ 📁 File tersimpan di   C:\Users\user\Downloads\Judul_Cerita.txt ║
║ ✅ Berhasil            45/45                                    ║
║ ⏱️  Waktu total         2m 18d                                   ║
╚═══════════════════════════════════════════════════╝
```

## 📂 Struktur Output

Nama dan bentuk file yang dihasilkan tergantung mode & format yang kamu pilih:

| Mode | Format `.txt` | Format `.docx` |
|------|----------------|-----------------|
| 1 - Semua, gabungan | `Judul_Cerita.txt` | `Judul_Cerita.docx` |
| 2 - Semua, terpisah | `Judul_Cerita.zip` (isi: `.txt` per chapter) | `Judul_Cerita.zip` (isi: `.docx` per chapter) |
| 3 - Beberapa chapter | `Judul_Cerita_pilihan.txt` | `Judul_Cerita_pilihan.docx` |
| 4 - Satu chapter | `Judul_Cerita_Ch003_Nama_Chapter.txt` | `Judul_Cerita_Ch003_Nama_Chapter.docx` |

**Isi file gabungan (mode 1 & 3):** judul cerita, penulis, dan sumber di bagian atas, lalu tiap chapter dipisah dengan penanda `#####`.

```
Judul Cerita
oleh Nama Penulis
Sumber : https://www.wattpad.com/story/123456789

==================================================

##### Judul Chapter 1 #####

Isi teks chapter 1...

##### Judul Chapter 2 #####

Isi teks chapter 2...
```

Di versi `.docx`, judul cerita jadi heading utama dan tiap chapter otomatis jadi Heading 1 dengan halaman baru, tinggal buka di Word atau Google Docs dan langsung enak dibaca.

**Isi zip (mode 2):** satu file per chapter, bernomor urut sesuai posisi di cerita, plus `000_info.txt`/`000_info.docx` berisi judul, penulis, dan sumber. Ekstensi file di dalam zip mengikuti format yang dipilih saat menjalankan script (`.txt` atau `.docx`):

```
Judul_Cerita.zip
├── 000_info.txt
├── 001_Judul_Chapter_1.txt
├── 002_Judul_Chapter_2.txt
└── ...
```

## 🗺️ Default Folder per OS

| Sistem Operasi | Folder Default |
|----------------|----------------|
| 🪟 Windows | `C:\Users\<namauser>\Downloads` |
| 🍎 macOS | `/Users/<namauser>/Downloads` |
| 🐧 Linux | `/home/<namauser>/Downloads` |

## ⚠️ Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `ModuleNotFoundError: No module named 'requests'` | Jalankan `pip install requests` |
| `ModuleNotFoundError: No module named 'rich'` | Jalankan `pip install rich` |
| `Library 'python-docx' belum terinstall` | Jalankan `pip install python-docx` (cuma dibutuhkan kalau memilih format `.docx`) |
| Error `404` / "Tidak ada chapter ditemukan" | Pastikan ID/link benar & cerita tidak di-private |
| Folder tidak bisa dibuat | Cek path valid & kamu punya izin tulis di sana |
| Proses macet di satu chapter | Cek koneksi internet, jalankan ulang, progress akan lanjut |

## 📝 Catatan Penting

- ID cerita adalah angka di URL Wattpad, tepat setelah `/story/`
- Script memakai endpoint publik, tidak butuh login atau API key
- Jeda **0.5 detik** antar chapter sudah diatur untuk menghindari rate limit server, jangan dihapus
- Script ini hanya untuk membaca cerita milik sendiri atau cerita publik secara offline. Hormati hak cipta penulis

## 🛠️ Dibuat dengan

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/-Requests-FF6B6B?style=flat-square)
![Rich](https://img.shields.io/badge/-Rich-FAE742?style=flat-square)
![python--docx](https://img.shields.io/badge/-python--docx-2B579A?style=flat-square)
![Wattpad API](https://img.shields.io/badge/-Wattpad%20Public%20API-FF6122?style=flat-square)

## ❓ FAQ

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

Ada jeda 0.5 detik antar chapter (sengaja, biar tidak membebani server Wattpad). Untuk cerita ratusan chapter, wajar kalau prosesnya makan waktu beberapa menit.

</details>

<details>
<summary><b>Mode dan format mana yang sebaiknya dipilih?</b></summary>

- Mau baca dari awal sampai akhir kayak buku → **Mode 1**, format `.txt` atau `.docx` sama-sama enak
- Mau tiap chapter jadi file sendiri-sendiri → **Mode 2**
- Cuma butuh beberapa chapter tertentu (misal lagi ulang baca bagian tertentu) → **Mode 3**
- Cuma penasaran satu chapter → **Mode 4**
- Mau edit atau print rapi pakai Word → pilih format **`.docx`**
- Mau file kecil dan simpel, atau mau dibaca di aplikasi e-reader/notes → pilih format **`.txt`**

</details>

## 👤 Author

<div align="center">

| [![Nicolas Dwi Dharma](https://github.com/github.png?size=100)](https://github.com/nekonaru) |
|:---:|
| **Nicolas Dwi Dharma** |
| [github.com/nekonaru](https://github.com/nekonaru) |

</div>

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

<div align="center">

Made with by **Nicolas Dwi Dharma**

*Star ⭐ repo ini kalau project ini membantumu!*

</div>
