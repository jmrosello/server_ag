from __future__ import annotations

import datetime as dt
import html
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / ".codex" / "generate_server_structure_report.py"
OUTPUT = ROOT / "cleanup-plan.html"


def load_inventory_module():
    spec = importlib.util.spec_from_file_location("server_inventory", INVENTORY)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar generate_server_structure_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def h(value: object) -> str:
    return html.escape(str(value), quote=True)


def item(path: str, size: str, reason: str, action: str, group: str, site: str = "") -> dict[str, str]:
    return {
        "path": path,
        "site": site,
        "size": size,
        "reason": reason,
        "action": action,
        "group": group,
    }


def table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "<p class=\"muted\">Sin items.</p>"
    body = []
    for row in rows:
        body.append(
            "<tr>"
            f"<td><code>{h(row['path'])}</code></td>"
            f"<td>{h(row['site'])}</td>"
            f"<td>{h(row['size'])}</td>"
            f"<td>{h(row['reason'])}</td>"
            f"<td>{h(row['action'])}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Ruta</th><th>Sitio</th><th>Tamano aprox.</th>"
        "<th>Motivo</th><th>Accion recomendada</th></tr></thead><tbody>"
        + "\n".join(body)
        + "</tbody></table>"
    )


def main() -> None:
    inv = load_inventory_module()
    dirs, stats, files, _ext_by_dir, _errors = inv.scan_tree()
    installs = inv.detect_wp_installs(dirs, stats)
    dumps = inv.find_db_dumps()

    site_by_db = {str(site.get("db_name") or ""): site for site in installs}
    analyses = {}
    for db_name, site in site_by_db.items():
        if db_name in dumps:
            analyses[db_name] = inv.analyze_sql_dump(dumps[db_name], str(site.get("table_prefix") or ""))

    low: list[dict[str, str]] = []
    review: list[dict[str, str]] = []
    keep: list[dict[str, str]] = []

    def size_of(rel: str) -> str:
        path = ROOT / rel
        if path.is_file():
            return inv.fmt_bytes(path.stat().st_size)
        return inv.fmt_bytes(stats.get(rel.replace("\\", "/"), {}).get("size", 0))

    # Low-risk operational cleanup: not runtime source, not active plugin state.
    for rel in [
        "error_log",
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
    ]:
        if (ROOT / rel).exists():
            low.append(
                item(
                    rel,
                    size_of(rel),
                    "Archivo operativo, backup viejo o archivo publico innecesario para runtime.",
                    "Borrar despues de backup; conservar solo .htaccess actual y wp-config.php.",
                    "low",
                    "raiz",
                )
            )

    # Inactive plugin folders based on DB active_plugins.
    for site in installs:
        analysis = analyses.get(str(site.get("db_name") or ""), {"active_plugins": []})
        active_slugs = {plugin.split("/", 1)[0] for plugin in analysis.get("active_plugins", [])}
        site_rel = str(site["rel"])
        site_label = str(site.get("domain") or site_rel)
        protected = site_rel == "prode"
        for plugin in site["plugins"]:
            slug = str(plugin["slug"])
            if slug == "index.php" or slug in active_slugs:
                continue
            rel = f"wp-content/plugins/{slug}" if site_rel == "." else f"{site_rel}/wp-content/plugins/{slug}"
            size = inv.fmt_bytes(int(plugin["size"]))
            if protected:
                keep.append(
                    item(rel, size, "Prode esta protegido por AGENTS.md.", "No borrar salvo pedido explicito.", "keep", site_label)
                )
            elif slug in {"custom-post-type-ui"}:
                review.append(
                    item(
                        rel,
                        size,
                        "Plugin inactivo, pero puede haber definido tipos de contenido historicos.",
                        "Revisar posts/meta y exportar estructura antes de borrar.",
                        "review",
                        site_label,
                    )
                )
            else:
                low.append(
                    item(
                        rel,
                        size,
                        "Plugin instalado pero no activo en active_plugins de la DB.",
                        "Borrar carpeta del plugin despues de backup y prueba de carga del sitio.",
                        "low",
                        site_label,
                    )
                )

    # Wordfence/W3/cache/log artifacts: cache is usually disposable, but live WP may recreate it.
    for rel in [
        "grupoag/wp-content/wflogs",
        "liggett/wp-content/wflogs",
        "wp-content/updraft",
        "grupoag/wp-content/uploads/wpforms/cache",
        "liggett/wp-content/uploads/wpforms/cache",
    ]:
        if (ROOT / rel).exists():
            review.append(
                item(
                    rel,
                    size_of(rel),
                    "Logs, backups o cache. No son fuente de diseno, pero pueden estar ligados a plugins activos o evidencia historica.",
                    "Vaciar o archivar despues de verificar plugin, backups y formularios.",
                    "review",
                    "",
                )
            )

    # Deprecated or ambiguous top-level folders.
    for rel, reason, action in [
        (
            "cobreqargentina",
            "AGENTS.md dice que este sitio sera removido.",
            "Archivar y retirar routing/DNS antes de borrar de produccion.",
        ),
        (
            "textarargentina",
            "AGENTS.md dice que este sitio sera removido.",
            "Archivar y retirar routing/DNS antes de borrar de produccion.",
        ),
        (
            "ml",
            "Carpeta mas pesada; AGENTS.md la trata como store de assets/marketplace, no codigo.",
            "Inventariar imagenes usadas por AG/Liggett/catalogo antes de mover o borrar.",
        ),
        ("prode.old", "Carpeta antigua junto a prode protegido.", "Comparar contra prode activo y archivar si no esta ruteada."),
        ("textar", "Carpeta no mapeada como sitio activo.", "Confirmar que no hay dominio/addon apuntando antes de borrar."),
        ("tienda", "Carpeta no mapeada como sitio activo.", "Confirmar que no hay dominio/addon apuntando antes de borrar."),
        ("catalogo", "Carpeta no mapeada como sitio activo.", "Confirmar si quedo vacia o sin uso antes de borrar."),
        ("downloads", "Carpeta auxiliar no mapeada.", "Revisar enlaces publicos antes de borrar."),
        ("webmail", "Carpeta no mapeada; puede ser placeholder o residuo del hosting.", "Confirmar con cPanel/routing antes de borrar."),
        ("default.htm", "Archivo estatico viejo en raiz.", "Revisar si algun link directo lo usa; si no, borrar."),
        ("top.htm", "Archivo estatico viejo en raiz.", "Revisar si algun link directo lo usa; si no, borrar."),
        ("stock.html", "Archivo estatico viejo en raiz.", "Revisar si algun link directo lo usa; si no, borrar."),
        ("AG_Catalogo_2023.xlsx", "Documento grande en raiz publica.", "Mover fuera de public_html o confirmar si debe seguir descargable."),
        ("tablaaltura.pdf", "PDF en raiz publica.", "Mover a assets controlados o confirmar si debe seguir descargable."),
    ]:
        if (ROOT / rel).exists():
            review.append(item(rel, size_of(rel), reason, action, "review", ""))

    # WooCommerce DB tables and theme overrides: not active, but they are historical catalog data.
    ag_analysis = analyses.get("ag_new")
    if ag_analysis:
        wc_tables = sorted(ag_analysis.get("woocommerce_tables", []))
        if wc_tables:
            review.append(
                item(
                    "dbdumps/ag_new.sql :: tablas WooCommerce/WC",
                    f"{len(wc_tables)} tablas",
                    "WooCommerce no esta activo, pero las tablas pueden contener catalogo historico/productos.",
                    "Exportar muestra de productos/meta antes de purgar tablas en MySQL.",
                    "review",
                    "ag.com.ar",
                )
            )
    for rel in ["wp-content/themes/ag/inc/woocommerce.php", "wp-content/themes/ag/woocommerce"]:
        if (ROOT / rel).exists():
            review.append(
                item(
                    rel,
                    size_of(rel),
                    "Override/hook WooCommerce dentro del theme AG; no se usa con WooCommerce inactivo, pero es parte del theme actual.",
                    "Eliminar solo en refactor o despues de verificar que ninguna plantilla lo carga.",
                    "review",
                    "ag.com.ar",
                )
            )

    # Protected / keep list.
    for rel, site, reason in [
        (".htaccess", "raiz", "Reglas actuales de WordPress/routing."),
        (".user.ini", "raiz", "Configuracion PHP local."),
        ("php.ini", "raiz", "Configuracion PHP local."),
        ("web.config", "raiz", "Configuracion de servidor si aplica."),
        ("wp-config.php", "ag.com.ar", "Credenciales y DB runtime."),
        ("wp-admin", "ag.com.ar", "Core WordPress activo."),
        ("wp-includes", "ag.com.ar", "Core WordPress activo."),
        ("wp-content/themes/ag", "ag.com.ar", "Theme activo y fuente visual principal."),
        ("wp-content/uploads", "ag.com.ar", "Medios y assets publicos."),
        ("liggett", "liggett.com.ar", "Sitio a conservar; limpiar solo items puntuales."),
        ("grupoag", "grupoag.com.ar", "Sitio a conservar; requiere cambios de contenido, no borrado masivo."),
        ("prode", "prode.ag.com.ar", "Protegido explicitamente por AGENTS.md."),
        ("dbdumps/ag_new.sql", "ag.com.ar", "Fuente de contenido para auditoria/migracion."),
        ("dbdumps/ag_wp388.sql", "liggett.com.ar", "Fuente de contenido para auditoria/migracion."),
        ("dbdumps/ag_wp943.sql", "grupoag.com.ar", "Fuente de contenido para auditoria/migracion."),
        ("dbdumps/ag_wp684.sql", "prode.ag.com.ar", "DB de sitio protegido."),
        ("AGENTS.md", "workspace", "Reglas de trabajo actuales."),
        ("server-structure-report.html", "workspace", "Inventario fuente de verdad actual."),
    ]:
        if (ROOT / rel).exists():
            keep.append(item(rel, size_of(rel), reason, "No tocar en limpieza automatica.", "keep", site))

    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_doc = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Plan de limpieza Server AG</title>
  <style>
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; color: #172033; background: #f7f8fa; }}
    header {{ background: #111827; color: white; padding: 28px 36px; }}
    main {{ padding: 24px 36px 48px; }}
    section {{ background: white; border: 1px solid #d9dee7; border-radius: 8px; margin: 0 0 20px; padding: 20px; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 0 0 12px; font-size: 22px; }}
    h3 {{ margin: 18px 0 8px; }}
    p {{ line-height: 1.45; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid #d9dee7; padding: 8px; }}
    th {{ background: #f1f4f8; position: sticky; top: 0; }}
    code {{ background: #eef2f7; border-radius: 4px; padding: 2px 5px; }}
    .muted {{ color: #667085; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }}
    .summary div {{ border: 1px solid #d9dee7; border-radius: 6px; padding: 10px; background: #fbfcfe; }}
    .ok h2 {{ color: #17633a; }}
    .review h2 {{ color: #8a5a00; }}
    .keep h2 {{ color: #174ea6; }}
    ol li {{ margin: 0 0 8px; }}
  </style>
</head>
<body>
<header>
  <h1>Plan de limpieza Server AG</h1>
  <p>Generado: {h(generated)} · Basado en <code>AGENTS.md</code>, archivos locales, <code>server-structure-report.html</code> y dumps SQL.</p>
</header>
<main>
  <section>
    <h2>Criterio usado</h2>
    <p>La limpieza respeta que AG, Liggett y GrupoAG se conservan; <code>prode</code> no se modifica; Cobreq y Textar se consideran sitios a remover, pero primero deben archivarse y desligarse de dominios/routing. WooCommerce no aparece activo en DB, aunque existen archivos y tablas historicas en AG.</p>
    <div class="summary">
      <div><b>Borrable bajo riesgo</b><br>{len(low)} items</div>
      <div><b>Revisar antes de borrar</b><br>{len(review)} items</div>
      <div><b>No tocar</b><br>{len(keep)} items</div>
    </div>
  </section>

  <section class="ok">
    <h2>Borrable con bajo riesgo</h2>
    <p class="muted">Items que no figuran como runtime activo en DB o son logs/backups/artefactos publicos innecesarios. Igual: borrar primero en copia/staging y con backup.</p>
    {table(low)}
  </section>

  <section class="review">
    <h2>Revisar antes de borrar</h2>
    <p class="muted">Items que pueden contener contenido historico, assets utiles, routing, dominios, evidencia operativa o datos necesarios para migracion.</p>
    {table(review)}
  </section>

  <section class="keep">
    <h2>No tocar</h2>
    <p class="muted">Runtime activo, sitios protegidos, fuentes de verdad o archivos necesarios para auditar/migrar.</p>
    {table(keep)}
  </section>

  <section>
    <h2>Implementacion recomendada</h2>
    <ol>
      <li>Hacer backup completo en cPanel: archivos + todas las DB. Guardarlo fuera de <code>public_html</code>.</li>
      <li>Crear carpeta de cuarentena, por ejemplo <code>_archive_cleanup_2026-05-15</code>, y mover alli los items de bajo riesgo en vez de borrarlos directo.</li>
      <li>Probar carga de <code>ag.com.ar</code>, <code>liggett.com.ar</code>, <code>grupoag.com.ar</code> y <code>prode.ag.com.ar</code>.</li>
      <li>Revisar la segunda lista: dominios/addon domains, links publicos, tablas WooCommerce, assets en <code>ml</code> y referencias Cobreq/Textar en GrupoAG.</li>
      <li>Despues de 7 a 14 dias sin errores, borrar la cuarentena o descargarla como archivo historico.</li>
    </ol>
  </section>
</main>
</body>
</html>
"""
    OUTPUT.write_text(html_doc, encoding="utf-8")
    print(str(OUTPUT))


if __name__ == "__main__":
    main()
