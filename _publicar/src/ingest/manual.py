"""Registra en el manifest un archivo descargado manualmente (ENIA, CNE, SNI...).

Uso:
    python src/ingest/manual.py --source enia --dataset cuadros --year 2024 \
        --file "C:/ruta/cuadros_enia_2024.xlsx" --url "https://www.ine.gob.cl/..." \
        --license "Uso libre citando fuente" --notes "cuadros sector-region"

El archivo se copia a data/raw/<source>/<dataset>/<year>/ y se registra su sha256.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from common.manifest import find, read_manifest, sha256_file, upsert, utc_now
from common.paths import RAW, ensure_dirs


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, help="retc | enia | cne | sni ...")
    p.add_argument("--dataset", required=True, help="nombre del conjunto dentro de la fuente")
    p.add_argument("--year", required=True, help="año de referencia del archivo")
    p.add_argument("--file", required=True, type=Path, help="archivo ya descargado")
    p.add_argument("--url", required=True, help="URL de origen (página o archivo)")
    p.add_argument("--license", default="", help="licencia o condiciones de uso")
    p.add_argument("--resource-name", default="", help="nombre legible del recurso")
    p.add_argument("--notes", default="", help="observaciones de la descarga manual")
    p.add_argument("--force", action="store_true")
    args = p.parse_args(argv)

    ensure_dirs()
    src: Path = args.file.expanduser()
    if not src.exists():
        print(f"[error] no existe: {src}", file=sys.stderr)
        return 1

    dest_dir = RAW / args.source / args.dataset / str(args.year)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name

    digest = sha256_file(src)
    prev = find(read_manifest(), args.source, args.dataset, args.year)
    if dest.exists() and prev and prev["sha256"] != digest and not args.force:
        print(f"[error] ya existe {dest} con otro hash. Usa --force para reemplazar.", file=sys.stderr)
        return 1

    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)

    upsert(
        {
            "source": args.source,
            "dataset": args.dataset,
            "year": args.year,
            "resource_id": "",
            "resource_name": args.resource_name or src.name,
            "url": args.url,
            "format": dest.suffix.lstrip(".").upper(),
            "size_bytes": dest.stat().st_size,
            "last_modified": "",
            "sha256": digest,
            "downloaded_at": utc_now(),
            "license": args.license,
            "local_path": str(dest.relative_to(RAW.parent.parent)),
            "notes": args.notes,
        }
    )
    print(f"ok -> {dest}  sha256={digest[:12]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
