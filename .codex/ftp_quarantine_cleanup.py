from __future__ import annotations

import argparse
import ftplib
import os
import posixpath
import ssl
import sys
import time
from dataclasses import dataclass


DEFAULT_HOST = "ftp.anicetogomez.com.ar"
DEFAULT_PORT = 21
DEFAULT_REMOTE_ROOT = "/"


@dataclass(frozen=True)
class MoveItem:
    path: str
    reason: str


LOW_RISK_MOVES = [
    MoveItem("error_log", "large runtime log"),
    MoveItem(".index.html.swp", "editor swap file"),
    MoveItem(".htaccess.181215165729.orig", "old htaccess backup"),
    MoveItem(".htaccess.181215173804.orig", "old htaccess backup"),
    MoveItem(".htaccess.2", "old htaccess backup"),
    MoveItem(".htaccess.andabien", "old htaccess backup"),
    MoveItem(".htaccess.disabled", "old htaccess backup"),
    MoveItem(".htaccess.old", "old htaccess backup"),
    MoveItem("wp-config-sample.php", "sample config"),
    MoveItem("readme.html", "public WordPress readme"),
    MoveItem("license.txt", "public WordPress license"),
    MoveItem("licencia.txt", "public WordPress license"),
    MoveItem("wp-content/plugins/woocommerce", "inactive plugin in DB"),
    MoveItem("wp-content/plugins/woocommerce-admin", "inactive plugin in DB"),
    MoveItem("wp-content/plugins/yith-woocommerce-ajax-navigation", "inactive plugin in DB"),
    MoveItem("wp-content/plugins/yith-woocommerce-catalog-mode", "inactive plugin in DB"),
    MoveItem("wp-content/plugins/updraftplus", "inactive plugin in DB"),
    MoveItem("wp-content/plugins/autoptimize", "inactive plugin in DB"),
    MoveItem("wp-content/plugins/resmushit-image-optimizer", "inactive plugin in DB"),
    MoveItem("grupoag/wp-content/plugins/post-duplicator", "inactive plugin in DB"),
    MoveItem("liggett/wp-content/plugins/w3-total-cache", "inactive plugin in DB"),
]


NEVER_MOVE = {
    ".htaccess",
    ".user.ini",
    "php.ini",
    "web.config",
    "wp-config.php",
    "wp-admin",
    "wp-includes",
    "wp-content/themes/ag",
    "wp-content/uploads",
    "liggett",
    "grupoag",
    "prode",
}


class ExplicitFTPS(ftplib.FTP_TLS):
    def __init__(self, *args, insecure: bool = False, **kwargs):
        context = ssl.create_default_context()
        if insecure:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        super().__init__(*args, context=context, **kwargs)


def clean_remote_path(path: str) -> str:
    path = path.replace("\\", "/").strip("/")
    parts = []
    for part in path.split("/"):
        if not part or part == ".":
            continue
        if part == "..":
            raise ValueError(f"unsafe path contains '..': {path}")
        parts.append(part)
    return "/".join(parts)


def join_remote(*parts: str) -> str:
    cleaned = [p.strip("/") for p in parts if p and p.strip("/")]
    return "/" + posixpath.join(*cleaned) if cleaned else "/"


def ensure_dir(ftp: ftplib.FTP, path: str, dry_run: bool) -> None:
    path = path.strip("/")
    if not path:
        return
    current = ""
    for part in path.split("/"):
        current = f"{current}/{part}" if current else part
        try:
            ftp.mkd(current)
        except ftplib.error_perm as exc:
            message = str(exc)
            if not (message.startswith("550") or "exists" in message.lower()):
                raise
        if dry_run:
            print(f"DRY-RUN ensure dir: /{current}")


def exists(ftp: ftplib.FTP, path: str) -> bool:
    parent = posixpath.dirname(path.strip("/")) or "."
    name = posixpath.basename(path)
    try:
        entries = ftp.nlst(parent)
    except ftplib.all_errors:
        return False
    names = {posixpath.basename(entry.rstrip("/")) for entry in entries}
    return name in names


def main() -> int:
    parser = argparse.ArgumentParser(description="Move low-risk Server AG cleanup items to an FTP quarantine folder.")
    parser.add_argument("--host", default=os.getenv("FTP_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("FTP_PORT", DEFAULT_PORT)))
    parser.add_argument("--user", default=os.getenv("FTP_USER"))
    parser.add_argument("--password", default=os.getenv("FTP_PASS"))
    parser.add_argument("--remote-root", default=os.getenv("FTP_REMOTE_ROOT", DEFAULT_REMOTE_ROOT))
    parser.add_argument("--quarantine", default=os.getenv("FTP_QUARANTINE"))
    parser.add_argument("--apply", action="store_true", help="Actually move files. Omit for dry-run.")
    parser.add_argument("--insecure-tls", action="store_true", help="Disable certificate verification if the host certificate is invalid.")
    args = parser.parse_args()

    if not args.user or not args.password:
        print("Missing FTP_USER or FTP_PASS. Set them as environment variables.", file=sys.stderr)
        return 2

    remote_root = clean_remote_path(args.remote_root)
    quarantine_name = clean_remote_path(args.quarantine or f"_archive_cleanup_{time.strftime('%Y%m%d_%H%M%S')}")
    dry_run = not args.apply

    unsafe = [item.path for item in LOW_RISK_MOVES if item.path.strip("/") in NEVER_MOVE]
    if unsafe:
        print("Refusing to move protected paths: " + ", ".join(unsafe), file=sys.stderr)
        return 3

    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"{mode}: connecting to {args.host}:{args.port} as {args.user}")
    print(f"Remote root: /{remote_root}" if remote_root else "Remote root: /")
    print(f"Quarantine: /{quarantine_name}")

    ftp = ExplicitFTPS(insecure=args.insecure_tls)
    ftp.connect(args.host, args.port, timeout=45)
    ftp.login(args.user, args.password)
    ftp.prot_p()
    if remote_root:
        ftp.cwd("/" + remote_root)

    ensure_dir(ftp, quarantine_name, dry_run=False)

    moved = 0
    skipped = 0
    failed = 0
    for item in LOW_RISK_MOVES:
        source_rel = clean_remote_path(item.path)
        source = source_rel
        target = clean_remote_path(posixpath.join(quarantine_name, source_rel))
        if not exists(ftp, source):
            print(f"SKIP missing: /{source_rel}")
            skipped += 1
            continue
        ensure_dir(ftp, posixpath.dirname(target), dry_run=dry_run)
        print(f"{mode} move: /{source_rel} -> /{target}  ({item.reason})")
        if dry_run:
            continue
        try:
            ftp.rename(source, target)
            moved += 1
        except ftplib.all_errors as exc:
            failed += 1
            print(f"FAILED: /{source_rel}: {exc}", file=sys.stderr)

    ftp.quit()
    print(f"Done. moved={moved} skipped={skipped} failed={failed} dry_run={dry_run}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
