from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUARANTINE = ROOT / "_archive_cleanup_20260515"
MANIFEST = ROOT / ".codex" / "post-cleanup-local-sync.json"


MOVED_ITEMS = [
    ".index.html.swp",
    ".htaccess.181215165729.orig",
    ".htaccess.181215173804.orig",
    ".htaccess.2",
    ".htaccess.andabien",
    ".htaccess.disabled",
    ".htaccess.old",
    "wp-config-sample.php",
    "readme.html",
    "license.txt",
    "licencia.txt",
    "wp-content/plugins/woocommerce",
    "wp-content/plugins/woocommerce-admin",
    "wp-content/plugins/yith-woocommerce-ajax-navigation",
    "wp-content/plugins/yith-woocommerce-catalog-mode",
    "wp-content/plugins/updraftplus",
    "wp-content/plugins/autoptimize",
    "wp-content/plugins/resmushit-image-optimizer",
    "grupoag/wp-content/plugins/post-duplicator",
    "liggett/wp-content/plugins/w3-total-cache",
    "cobreqargentina",
    "textarargentina",
    "prode.old",
    "catalogo",
    "tienda",
]


def safe_path(rel: str) -> Path:
    path = (ROOT / rel).resolve()
    if not str(path).startswith(str(ROOT.resolve())):
        raise RuntimeError(f"Unsafe path outside workspace: {rel}")
    return path


def move_to_quarantine(rel: str) -> dict[str, str]:
    src = safe_path(rel)
    dst = (QUARANTINE / rel).resolve()
    if not str(dst).startswith(str(QUARANTINE.resolve())):
        raise RuntimeError(f"Unsafe quarantine target: {rel}")
    if not src.exists():
        return {"path": rel, "status": "missing"}
    if dst.exists():
        return {"path": rel, "status": "already_quarantined"}
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return {"path": rel, "status": "moved"}


def main() -> None:
    QUARANTINE.mkdir(exist_ok=True)
    results = [move_to_quarantine(rel) for rel in MOVED_ITEMS]
    MANIFEST.write_text(json.dumps(results, indent=2), encoding="utf-8")
    for result in results:
        print(f"{result['status']}: {result['path']}")


if __name__ == "__main__":
    main()
