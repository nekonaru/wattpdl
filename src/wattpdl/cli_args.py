"""
Modul parsing argumen command line untuk mode non-interaktif.
Kalau --id/--user diisi, script jalan tanpa prompt sama sekali — cocok untuk
otomatisasi/scripting.
"""
import argparse

from . import __version__

MODE_HELP = (
    "1 = semua chapter jadi 1 file gabungan, "
    "2 = semua chapter terpisah dikemas .zip, "
    "3 = pilih beberapa chapter (perlu --chapters), "
    "4 = pilih 1 chapter saja (perlu --chapter)"
)

FORMAT_TO_CODE = {"txt": "1", "docx": "2", "epub": "3", "md": "4", "pdf": "5"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wattpdl",
        description=(
            "WattPDL — Wattpad Story Downloader. "
            "Jalankan tanpa argumen untuk mode interaktif, "
            "atau isi --id (atau --user) untuk mode non-interaktif/scripting."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--id", metavar="ID_ATAU_LINK",
        help="ID atau link cerita Wattpad. Mengisi ini mengaktifkan mode non-interaktif.",
    )
    parser.add_argument("--mode", choices=["1", "2", "3", "4"], help=MODE_HELP)
    parser.add_argument(
        "--format", choices=["txt", "docx", "epub", "md", "pdf"],
        help="Format file output. Default: dari config tersimpan, atau txt kalau belum ada.",
    )
    parser.add_argument(
        "--chapters", metavar="1,3,5-8",
        help="Nomor chapter yang diunduh untuk --mode 3, contoh: 1,3,5-8",
    )
    parser.add_argument(
        "--chapter", type=int, metavar="N",
        help="Nomor chapter yang diunduh untuk --mode 4",
    )
    parser.add_argument(
        "--output-dir", metavar="PATH",
        help="Folder penyimpanan. Default: dari config tersimpan, atau folder Downloads.",
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Lewati unduhan kalau file output tujuan sudah ada, alih-alih menimpanya.",
    )
    parser.add_argument(
        "--no-cover", action="store_true",
        help="Jangan sisipkan gambar sampul cerita ke file .docx/.epub/.pdf.",
    )
    parser.add_argument(
        "--include-images", action="store_true",
        help="Ikut unduh & sisipkan gambar inline di dalam chapter (bukan cuma cover) "
             "ke file .docx/.epub/.pdf. Menambah waktu unduh.",
    )
    parser.add_argument(
        "--workers", type=int, default=1, metavar="N",
        help="Jumlah chapter yang diunduh bersamaan (paralel). Default 1 (berurutan, "
             "paling aman). Naikkan (mis. 4) untuk mempercepat cerita panjang; jeda "
             "otomatis melambat sendiri kalau server mulai membatasi (rate-limit).",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Jangan pakai cache metadata cerita (~/.wattpdl/cache/), selalu ambil data terbaru.",
    )
    parser.add_argument(
        "--no-update-check", action="store_true",
        help="Jangan cek versi wattpdl terbaru di PyPI saat start.",
    )

    # --- unduh semua/cerita pilihan dari 1 penulis ---
    parser.add_argument(
        "--user", metavar="USERNAME",
        help="Unduh dari daftar cerita seorang penulis Wattpad, alih-alih 1 cerita by ID. "
             "Kombinasikan dengan --user-select.",
    )
    parser.add_argument(
        "--user-select", metavar="all|1,3,5", default="all",
        help="Cerita mana saja dari --user yang diunduh: 'all' (default) atau nomor "
             "seperti pada --chapters, mis. 1,3,5-8.",
    )

    # --- deteksi update chapter untuk cerita yang sudah pernah diunduh ---
    parser.add_argument(
        "--check-updates", action="store_true",
        help="Cek semua cerita yang pernah diunduh (~/.wattpdl/library.json) apakah ada "
             "chapter baru, tanpa perlu --id. Tidak mengunduh apa pun, cuma melaporkan.",
    )

    # --- mode watch: pantau cerita ongoing, auto-unduh ulang kalau ada chapter baru ---
    parser.add_argument(
        "--watch", action="store_true",
        help="Pantau --id terus-menerus, otomatis unduh ulang kalau ada chapter baru. "
             "Berhenti dengan Ctrl+C.",
    )
    parser.add_argument(
        "--watch-interval", type=int, default=1800, metavar="DETIK",
        help="Jeda antar pengecekan di mode --watch, dalam detik (default 1800 = 30 menit).",
    )
    parser.add_argument(
        "--watch-max-iterations", type=int, default=None, metavar="N",
        help=argparse.SUPPRESS,  # knob internal buat testing, sengaja tidak didokumentasikan ke user
    )

    return parser


def parse_args(argv=None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def validate_non_interactive_args(args: argparse.Namespace) -> None:
    """
    Validasi kombinasi argumen mode non-interaktif (dipakai setelah --id diisi).
    Raise ValueError dengan pesan yang jelas kalau ada argumen wajib yang kurang.
    """
    if not args.mode:
        raise ValueError("--mode wajib diisi kalau pakai --id (mode non-interaktif).")
    if args.mode == "3" and not args.chapters:
        raise ValueError("--chapters wajib diisi untuk --mode 3, contoh: --chapters 1,3,5-8")
    if args.mode == "4" and args.chapter is None:
        raise ValueError("--chapter wajib diisi untuk --mode 4, contoh: --chapter 5")
    if args.workers < 1:
        raise ValueError("--workers minimal 1.")
