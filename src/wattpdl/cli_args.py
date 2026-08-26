"""
Modul parsing argumen command line untuk mode non-interaktif.
Kalau --id diisi, script jalan tanpa prompt sama sekali — cocok untuk
otomatisasi/scripting.
"""
import argparse

MODE_HELP = (
    "1 = semua chapter jadi 1 file gabungan, "
    "2 = semua chapter terpisah dikemas .zip, "
    "3 = pilih beberapa chapter (perlu --chapters), "
    "4 = pilih 1 chapter saja (perlu --chapter)"
)

FORMAT_TO_CODE = {"txt": "1", "docx": "2", "epub": "3", "md": "4"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wattpdl",
        description=(
            "WattPDL — Wattpad Story Downloader. "
            "Jalankan tanpa argumen untuk mode interaktif, "
            "atau isi --id untuk mode non-interaktif/scripting."
        ),
    )
    parser.add_argument(
        "--id", metavar="ID_ATAU_LINK",
        help="ID atau link cerita Wattpad. Mengisi ini mengaktifkan mode non-interaktif.",
    )
    parser.add_argument("--mode", choices=["1", "2", "3", "4"], help=MODE_HELP)
    parser.add_argument(
        "--format", choices=["txt", "docx", "epub", "md"],
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
        help="Jangan sisipkan gambar sampul cerita ke file .docx/.epub.",
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
