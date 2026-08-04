<div align="center">

```
 ██╗    ██╗ █████╗ ████████╗████████╗██████╗ ██╗      ██████╗ ██╗
 ██║    ██║██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██║     ██╔═══██╗██║
 ██║ █╗ ██║███████║   ██║      ██║   ██████╔╝██║     ██║   ██║██║
 ██║███╗██║██╔══██║   ██║      ██║   ██╔═══╝ ██║     ██║   ██║╚═╝
 ╚███╔███╔╝██║  ██║   ██║      ██║   ██║     ███████╗╚██████╔╝██╗
  ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝     ╚══════╝ ╚═════╝ ╚═╝
```

### 📖 Wattpad Story Downloader
**Simpan semua chapter favoritmu jadi satu file `.txt` — offline, rapi, selamanya.**

<br>

![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

</div>

---

## ✨ Tentang Project

**WattPDL** adalah script Python ringan yang mengunduh seluruh chapter dari cerita Wattpad pilihanmu — dari chapter pertama sampai tamat — lalu menggabungkannya jadi satu file `.txt` yang bersih dan rapi. Tidak perlu login, tidak perlu API key, cukup link atau ID ceritanya.

> _"Karena cerita yang bagus layak dibaca kapan saja, bahkan tanpa internet."_

---

## 🎯 Fitur

| Fitur | Keterangan |
|-------|------------|
| 📁 **Pilih folder simpan** | Default ke folder `Downloads` sistem, bisa dikustomisasi |
| 🔄 **Auto-retry** | Chapter gagal dicoba ulang hingga 3× sebelum dilewati |
| 📊 **Progress bar** | Tampil persentase & nomor chapter yang sedang diunduh |
| 📋 **Ringkasan akhir** | Laporan chapter yang gagal (jika ada) setelah selesai |
| 🗂 **Nama file aman** | Karakter ilegal otomatis dihapus dari nama file |
| 🔗 **Link sumber tersimpan** | URL cerita dicantumkan di header file hasil |
| ⚡ **Tanpa login** | Pakai endpoint publik Wattpad — tidak butuh akun |

---

## 📦 Requirements

- **Python** 3.7 atau lebih baru
- **Koneksi internet**
- Library: `requests`

Cek Python sudah terinstall:
```bash
python --version
# atau
python3 --version
```

---

## 🚀 Instalasi

**1. Clone repository ini**
```bash
git clone https://github.com/nekonaru/wattpdl.git
cd wattpdl
```

**2. Install dependency**
```bash
pip install requests
```

> Kalau muncul error `externally-managed-environment` (biasanya di Linux):
> ```bash
> pip install requests --break-system-packages
> ```

---

## 🖥️ Cara Pakai

**Jalankan script:**
```bash
python download_wattpad.py
```

**Masukkan link atau ID cerita saat diminta:**
```
Masukkan link atau ID cerita Wattpad: https://www.wattpad.com/story/123456789-judul-cerita
```
atau cukup ID-nya:
```
Masukkan link atau ID cerita Wattpad: 123456789
```

**Pilih folder penyimpanan:**
```
📁 Folder default penyimpanan: C:\Users\user\Downloads
   Tekan Enter untuk memakai folder itu,
   atau ketik path lain: 
```
Tekan **Enter** untuk simpan di `Downloads`, atau ketik path kustom seperti:
- Windows: `D:\Cerita\Wattpad`
- Linux/macOS: `/home/user/cerita`

**Tunggu proses selesai:**
```
[████████████████░░░░░░░░░░░░░░]  53.3%  (24/45)  Chapter 24...
```

**Done! 🎉**
```
✅ Semua chapter tersimpan di:
   C:\Users\user\Downloads\Judul_Cerita.txt
```

---

## 📂 Struktur Output

File `.txt` yang dihasilkan punya format seperti ini:

```
Judul Cerita
oleh Nama Penulis
Sumber : https://www.wattpad.com/story/123456789

══════════════════════════════════════════════════

##### Judul Chapter 1 #####

Isi teks chapter 1...


##### Judul Chapter 2 #####

Isi teks chapter 2...
```

---

## 🗺️ Default Folder per OS

| Sistem Operasi | Folder Default |
|----------------|----------------|
| 🪟 Windows | `C:\Users\<namauser>\Downloads` |
| 🍎 macOS | `/Users/<namauser>/Downloads` |
| 🐧 Linux | `/home/<namauser>/Downloads` |

---

## ⚠️ Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `ModuleNotFoundError: No module named 'requests'` | Jalankan `pip install requests` |
| Error `404` / "Tidak ada chapter ditemukan" | Pastikan ID/link benar & cerita tidak di-private |
| Folder tidak bisa dibuat | Cek path valid & kamu punya izin tulis di sana |
| Proses macet di satu chapter | Cek koneksi internet, jalankan ulang — progress akan lanjut |

---

## 📝 Catatan Penting

- ID cerita adalah angka di URL Wattpad, tepat setelah `/story/`
- Script memakai endpoint publik — tidak butuh login atau API key
- Jeda **0.5 detik** antar chapter sudah diatur untuk menghindari rate limit server — jangan dihapus
- Script ini hanya untuk membaca cerita milik sendiri atau cerita publik secara offline. Hormati hak cipta penulis

---

## 🛠️ Dibuat dengan

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/-Requests-FF6B6B?style=flat-square)
![Wattpad API](https://img.shields.io/badge/-Wattpad%20Public%20API-FF6122?style=flat-square)

---

## 👤 Author

<div align="center">

| [![Nicolas Dwi Dharma](https://github.com/github.png?size=100)](https://github.com/nekonaru) |
|:---:|
| **Nicolas Dwi Dharma** |
| [github.com/nekonaru](https://github.com/nekonaru) |

</div>

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

Made with ☕ and 📖 by **Nicolas Dwi Dharma**

*Star ⭐ repo ini kalau project ini membantumu!*

</div>
