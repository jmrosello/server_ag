from __future__ import annotations

import datetime as dt
import html
import os
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "server-structure-report.html"
DB_DUMP_DIRS = [ROOT / "dbdumps", ROOT / "db-dumps"]

SKIP_DIR_NAMES = {".git", ".codex", "dbdumps", "db-dumps"}
SKIP_DIR_PREFIXES = ("_archive_cleanup_",)

ACTIVE_SITES = {
    ".": "ag.com.ar",
    "liggett": "liggett.com.ar",
    "grupoag": "grupoag.com.ar",
    "prode": "prode.ag.com.ar",
}

EXPECTED_ACTIVE_DIRS = set(ACTIVE_SITES.keys())
PROTECTED_ROOT_DIRS = {
    "ml": "intocable / assets otra app",
    "downloads": "intocable",
    "webmail": "intocable",
}

MEDIA_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".avif",
    ".ico",
    ".mp4",
    ".mov",
    ".webm",
    ".pdf",
}

CODE_EXTS = {".php", ".js", ".css", ".html", ".htm", ".json", ".xml", ".txt", ".ini", ".config"}
WP_OPTION_NAMES = {
    "siteurl",
    "home",
    "blogname",
    "template",
    "stylesheet",
    "current_theme",
    "active_plugins",
    "woocommerce_db_version",
    "woocommerce_version",
    "woocommerce_queue_flush_rewrite_rules",
}


def rel_for(path: Path) -> str:
    if path == ROOT:
        return "."
    return path.relative_to(ROOT).as_posix()


def path_for(rel: str) -> Path:
    return ROOT if rel == "." else ROOT / rel


def parent_rels(rel: str) -> list[str]:
    if rel == ".":
        return ["."]
    parts = rel.split("/")
    parents = ["."]
    for i in range(1, len(parts)):
        parents.append("/".join(parts[:i]))
    parents.append(rel)
    return parents


def fmt_bytes(size: int | float) -> str:
    size = float(size or 0)
    units = ["B", "KB", "MB", "GB", "TB"]
    unit = 0
    while size >= 1024 and unit < len(units) - 1:
        size /= 1024
        unit += 1
    if unit == 0:
        return f"{int(size)} {units[unit]}"
    return f"{size:.2f} {units[unit]}"


def h(value: object) -> str:
    return html.escape(str(value), quote=True)


def read_text_sample(path: Path, limit: int = 64_000) -> str:
    try:
        with path.open("rb") as f:
            data = f.read(limit)
        return data.decode("utf-8", errors="ignore")
    except OSError:
        return ""


def parse_wp_define(text: str, name: str) -> str:
    pattern = re.compile(
        r"define\s*\(\s*['\"]" + re.escape(name) + r"['\"]\s*,\s*['\"]([^'\"]*)['\"]\s*\)",
        re.I,
    )
    match = pattern.search(text)
    return match.group(1) if match else ""


def parse_table_prefix(text: str) -> str:
    match = re.search(r"\$table_prefix\s*=\s*['\"]([^'\"]+)['\"]\s*;", text)
    return match.group(1) if match else ""


def sql_unescape(value: str) -> str:
    replacements = {
        r"\\": "\\",
        r"\'": "'",
        r"\"": '"',
        r"\n": "\n",
        r"\r": "\r",
        r"\t": "\t",
        r"\0": "\0",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    return value


def split_sql_tuple(tuple_text: str) -> list[str]:
    values: list[str] = []
    current: list[str] = []
    in_string = False
    escape = False
    for char in tuple_text:
        if in_string:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == "'":
                in_string = False
            continue
        if char == "'":
            in_string = True
            current.append(char)
        elif char == ",":
            values.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    values.append("".join(current).strip())
    return values


def iter_sql_tuples(values_sql: str):
    depth = 0
    start = None
    in_string = False
    escape = False
    for index, char in enumerate(values_sql):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == "'":
                in_string = False
            continue
        if char == "'":
            in_string = True
        elif char == "(":
            if depth == 0:
                start = index + 1
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0 and start is not None:
                yield values_sql[start:index]
                start = None


def sql_value(value: str) -> str:
    value = value.strip()
    if value.upper() == "NULL":
        return ""
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        return sql_unescape(value[1:-1])
    return value


def extract_active_plugins(value: str) -> list[str]:
    if not value:
        return []
    plugins = re.findall(r's:\d+:"([^"]+\.php)"', value)
    if plugins:
        return plugins
    plugins = re.findall(r'"([^"]+\.php)"', value)
    return plugins


def count_insert_rows(values_sql: str) -> int:
    return sum(1 for _ in iter_sql_tuples(values_sql))


def find_db_dumps() -> dict[str, Path]:
    dumps: dict[str, Path] = {}
    for folder in DB_DUMP_DIRS:
        if not folder.exists():
            continue
        for path in folder.glob("*.sql"):
            dumps[path.stem] = path
    return dumps


def analyze_sql_dump(path: Path, expected_prefix: str = "") -> dict[str, object]:
    dump = {
        "path": rel_for(path),
        "size": path.stat().st_size,
        "tables": Counter(),
        "table_bytes": Counter(),
        "options": {},
        "active_plugins": [],
        "woocommerce_tables": [],
        "table_prefix_candidates": Counter(),
        "errors": [],
    }
    current_insert_table = ""
    statement_parts: list[str] = []

    def handle_insert(statement: str, table: str) -> None:
        values_match = re.search(r"\bVALUES\b", statement, re.I)
        if not values_match:
            return
        values_sql = statement[values_match.end() :].rstrip().rstrip(";")
        row_count = count_insert_rows(values_sql)
        dump["tables"][table] += row_count
        dump["table_bytes"][table] += len(statement.encode("utf-8", errors="ignore"))
        if table.endswith("_options") and (not expected_prefix or table == f"{expected_prefix}options"):
            for tuple_text in iter_sql_tuples(values_sql):
                fields = split_sql_tuple(tuple_text)
                if len(fields) < 3:
                    continue
                option_name = sql_value(fields[1])
                if option_name not in WP_OPTION_NAMES:
                    continue
                dump["options"][option_name] = sql_value(fields[2])

    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                create_match = re.search(r"CREATE TABLE\s+`([^`]+)`", line)
                if create_match:
                    table = create_match.group(1)
                    prefix_match = re.match(r"(.+?)(options|posts|postmeta|users|usermeta|terms|termmeta|term_taxonomy|term_relationships|comments|commentmeta)$", table)
                    if prefix_match:
                        dump["table_prefix_candidates"][prefix_match.group(1)] += 1
                    if "woocommerce" in table.lower() or table.lower().startswith((expected_prefix + "wc_").lower()):
                        dump["woocommerce_tables"].append(table)

                insert_match = re.match(r"INSERT INTO\s+`([^`]+)`", line)
                if insert_match and not statement_parts:
                    current_insert_table = insert_match.group(1)
                    statement_parts = [line]
                    if line.rstrip().endswith(";"):
                        handle_insert("".join(statement_parts), current_insert_table)
                        statement_parts = []
                        current_insert_table = ""
                elif statement_parts:
                    statement_parts.append(line)
                    if line.rstrip().endswith(";"):
                        handle_insert("".join(statement_parts), current_insert_table)
                        statement_parts = []
                        current_insert_table = ""
    except OSError as exc:
        dump["errors"].append(str(exc))

    options = dump["options"]
    dump["active_plugins"] = extract_active_plugins(str(options.get("active_plugins", "")))
    return dump


def redact(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return value[:2] + ("*" * max(3, len(value) - 4)) + value[-2:]


def parse_header_value(text: str, key: str) -> str:
    match = re.search(r"^\s*" + re.escape(key) + r"\s*:\s*(.+?)\s*$", text, re.I | re.M)
    return match.group(1).strip() if match else ""


def find_plugin_name(plugin_path: Path) -> str:
    if plugin_path.is_file() and plugin_path.suffix.lower() == ".php":
        return parse_header_value(read_text_sample(plugin_path, 16_000), "Plugin Name")
    if not plugin_path.is_dir():
        return ""
    php_files = list(plugin_path.glob("*.php"))[:50]
    for candidate in php_files:
        name = parse_header_value(read_text_sample(candidate, 16_000), "Plugin Name")
        if name:
            return name
    return ""


def find_theme_name(theme_path: Path) -> str:
    style = theme_path / "style.css"
    if style.exists():
        return parse_header_value(read_text_sample(style, 16_000), "Theme Name")
    return ""


def parse_wp_version(site_path: Path) -> str:
    version_file = site_path / "wp-includes" / "version.php"
    if not version_file.exists():
        return ""
    text = read_text_sample(version_file, 16_000)
    match = re.search(r"\$wp_version\s*=\s*['\"]([^'\"]+)['\"]", text)
    return match.group(1) if match else ""


def scan_tree() -> tuple[
    set[str],
    dict[str, dict[str, int]],
    list[dict[str, object]],
    dict[str, Counter],
    list[str],
]:
    dirs: set[str] = {"."}
    stats: dict[str, dict[str, int]] = defaultdict(lambda: {"size": 0, "files": 0, "dirs": 0})
    files: list[dict[str, object]] = []
    ext_by_dir: dict[str, Counter] = defaultdict(Counter)
    errors: list[str] = []

    for current, dirnames, filenames in os.walk(ROOT):
        current_path = Path(current)
        dirnames[:] = sorted(
            [d for d in dirnames if d not in SKIP_DIR_NAMES and not d.startswith(SKIP_DIR_PREFIXES)],
            key=str.lower,
        )
        filenames = sorted(filenames, key=str.lower)

        current_rel = rel_for(current_path)
        dirs.add(current_rel)
        stats[current_rel]["dirs"] += len(dirnames)

        for d in dirnames:
            dirs.add(rel_for(current_path / d))

        for filename in filenames:
            path = current_path / filename
            if path.resolve() == OUTPUT.resolve():
                continue
            rel = rel_for(path)
            try:
                st = path.stat()
            except OSError as exc:
                errors.append(f"{rel}: {exc}")
                continue

            ext = path.suffix.lower() or "[no extension]"
            files.append(
                {
                    "rel": rel,
                    "name": filename,
                    "parent": current_rel,
                    "size": st.st_size,
                    "mtime": dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                    "ext": ext,
                }
            )
            for parent in parent_rels(current_rel):
                stats[parent]["size"] += st.st_size
                stats[parent]["files"] += 1
            top = current_rel.split("/")[0] if current_rel != "." else "."
            ext_by_dir[top][ext] += 1

    return dirs, stats, files, ext_by_dir, errors


def detect_wp_installs(dirs: set[str], stats: dict[str, dict[str, int]]) -> list[dict[str, object]]:
    installs: list[dict[str, object]] = []
    for rel in sorted(dirs, key=lambda x: (x.count("/"), x.lower())):
        site_path = path_for(rel)
        if not (site_path / "wp-config.php").exists():
            continue

        config = read_text_sample(site_path / "wp-config.php")
        plugins_dir = site_path / "wp-content" / "plugins"
        themes_dir = site_path / "wp-content" / "themes"
        uploads_dir = site_path / "wp-content" / "uploads"

        plugins = []
        if plugins_dir.exists():
            for child in sorted(plugins_dir.iterdir(), key=lambda p: p.name.lower()):
                if child.name.startswith("."):
                    continue
                child_rel = rel_for(child)
                plugins.append(
                    {
                        "slug": child.name,
                        "name": find_plugin_name(child),
                        "size": stats.get(child_rel, {}).get("size", child.stat().st_size if child.is_file() else 0),
                        "files": stats.get(child_rel, {}).get("files", 1 if child.is_file() else 0),
                    }
                )

        themes = []
        if themes_dir.exists():
            for child in sorted([p for p in themes_dir.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
                child_rel = rel_for(child)
                themes.append(
                    {
                        "slug": child.name,
                        "name": find_theme_name(child),
                        "size": stats.get(child_rel, {}).get("size", 0),
                        "files": stats.get(child_rel, {}).get("files", 0),
                    }
                )

        upload_breakdown = []
        if uploads_dir.exists():
            for child in sorted(uploads_dir.iterdir(), key=lambda p: p.name.lower()):
                child_rel = rel_for(child)
                upload_breakdown.append(
                    {
                        "name": child.name,
                        "size": stats.get(child_rel, {}).get("size", child.stat().st_size if child.is_file() else 0),
                        "files": stats.get(child_rel, {}).get("files", 1 if child.is_file() else 0),
                    }
                )

        installs.append(
            {
                "rel": rel,
                "domain": ACTIVE_SITES.get(rel, ""),
                "size": stats.get(rel, {}).get("size", 0),
                "files": stats.get(rel, {}).get("files", 0),
                "version": parse_wp_version(site_path),
                "db_name": parse_wp_define(config, "DB_NAME"),
                "db_user": redact(parse_wp_define(config, "DB_USER")),
                "db_host": parse_wp_define(config, "DB_HOST"),
                "table_prefix": parse_table_prefix(config),
                "plugins": plugins,
                "themes": themes,
                "uploads": upload_breakdown,
            }
        )
    return installs


def row(cols: list[object]) -> str:
    return "<tr>" + "".join(f"<td>{h(col)}</td>" for col in cols) + "</tr>"


def table(headers: list[str], rows: list[list[object]], empty: str = "Sin datos") -> str:
    if not rows:
        return f"<p class=\"muted\">{h(empty)}</p>"
    body = "\n".join(row(r) for r in rows)
    head = "".join(f"<th>{h(x)}</th>" for x in headers)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def render_tree(dirs: set[str], files: list[dict[str, object]], stats: dict[str, dict[str, int]]) -> str:
    child_dirs: dict[str, list[str]] = defaultdict(list)
    child_files: dict[str, list[dict[str, object]]] = defaultdict(list)
    for d in dirs:
        if d == ".":
            continue
        parent = "." if "/" not in d else d.rsplit("/", 1)[0]
        child_dirs[parent].append(d)
    for f in files:
        child_files[str(f["parent"])].append(f)
    for key in child_dirs:
        child_dirs[key].sort(key=str.lower)
    for key in child_files:
        child_files[key].sort(key=lambda x: str(x["name"]).lower())

    def rec(rel: str) -> str:
        label = "public_html / raiz" if rel == "." else rel.rsplit("/", 1)[-1]
        st = stats.get(rel, {})
        parts = [
            "<details open>" if rel == "." else "<details>",
            "<summary>",
            f"<span class=\"folder\">{h(label)}</span>",
            f"<span class=\"meta\">{fmt_bytes(st.get('size', 0))} · {st.get('files', 0)} archivos</span>",
            "</summary>",
        ]
        for child in child_dirs.get(rel, []):
            parts.append(rec(child))
        if child_files.get(rel):
            parts.append("<ul>")
            for f in child_files[rel]:
                parts.append(
                    "<li>"
                    f"<span class=\"file\">{h(f['name'])}</span>"
                    f"<span class=\"meta\">{fmt_bytes(int(f['size']))} · {h(f['mtime'])}</span>"
                    "</li>"
                )
            parts.append("</ul>")
        parts.append("</details>")
        return "\n".join(parts)

    return rec(".")


def render_site_section(site: dict[str, object]) -> str:
    plugins = sorted(site["plugins"], key=lambda x: int(x["size"]), reverse=True)
    themes = sorted(site["themes"], key=lambda x: int(x["size"]), reverse=True)
    uploads = sorted(site["uploads"], key=lambda x: int(x["size"]), reverse=True)
    wc = [p for p in plugins if "woocommerce" in str(p["slug"]).lower() or str(p["slug"]).lower().startswith("wc-")]

    plugin_rows = [
        [p["slug"], p["name"] or "-", fmt_bytes(int(p["size"])), p["files"], "WooCommerce/revisar" if p in wc else ""]
        for p in plugins
    ]
    theme_rows = [[t["slug"], t["name"] or "-", fmt_bytes(int(t["size"])), t["files"]] for t in themes]
    upload_rows = [[u["name"], fmt_bytes(int(u["size"])), u["files"]] for u in uploads[:80]]

    return f"""
    <section class="site">
      <h2>{h(site['domain'] or site['rel'])}</h2>
      <div class="grid">
        <div><b>Carpeta</b><br><code>{h(site['rel'])}</code></div>
        <div><b>Tamano</b><br>{fmt_bytes(int(site['size']))}</div>
        <div><b>Archivos</b><br>{h(site['files'])}</div>
        <div><b>WordPress</b><br>{h(site['version'] or 'no detectado')}</div>
        <div><b>DB</b><br><code>{h(site['db_name'] or '-')}</code></div>
        <div><b>Prefijo</b><br><code>{h(site['table_prefix'] or '-')}</code></div>
      </div>
      <h3>Plugins</h3>
      {table(['slug', 'nombre detectado', 'tamano', 'archivos', 'nota'], plugin_rows)}
      <h3>Temas</h3>
      {table(['slug', 'nombre detectado', 'tamano', 'archivos'], theme_rows)}
      <h3>Uploads / medios por carpeta</h3>
      {table(['carpeta', 'tamano', 'archivos'], upload_rows)}
    </section>
    """


def render_db_section(installs: list[dict[str, object]], db_analyses: dict[str, dict[str, object]], dumps: dict[str, Path]) -> str:
    dump_rows = []
    for name, path in sorted(dumps.items()):
        analysis = db_analyses.get(name)
        mapped = [str(site["domain"] or site["rel"]) for site in installs if site.get("db_name") == name]
        dump_rows.append(
            [
                name,
                rel_for(path),
                fmt_bytes(path.stat().st_size),
                ", ".join(mapped) or "sin wp-config mapeado",
                len(analysis["tables"]) if analysis else "-",
                len(analysis["woocommerce_tables"]) if analysis else "-",
            ]
        )

    site_rows = []
    plugin_rows = []
    table_rows = []
    woo_rows = []
    for site in installs:
        db_name = str(site.get("db_name") or "")
        analysis = db_analyses.get(db_name)
        if not analysis:
            site_rows.append([site["domain"] or site["rel"], db_name or "-", "NO", "-", "-", "-", "-", "-"])
            continue
        options = analysis["options"]
        active_plugins = analysis["active_plugins"]
        active_plugin_slugs = {p.split("/", 1)[0] for p in active_plugins}
        installed_plugins = {str(p["slug"]) for p in site["plugins"]}
        installed_woo = any("woocommerce" in str(p["slug"]).lower() or str(p["slug"]).lower().startswith("wc-") for p in site["plugins"])
        active_woo = any("woocommerce" in p.lower() or p.lower().startswith("wc-") for p in active_plugins)
        prefix_candidates = analysis["table_prefix_candidates"].most_common(3)
        prefix_label = ", ".join(f"{prefix} ({count})" for prefix, count in prefix_candidates)
        missing_active_files = sorted(active_plugin_slugs - installed_plugins)

        site_rows.append(
            [
                site["domain"] or site["rel"],
                db_name,
                "SI",
                options.get("home") or options.get("siteurl") or "-",
                options.get("blogname") or "-",
                options.get("stylesheet") or options.get("template") or "-",
                len(active_plugins),
                "activo" if active_woo else ("solo archivos/tablas" if installed_woo or analysis["woocommerce_tables"] else "no"),
            ]
        )

        for plugin in active_plugins:
            plugin_rows.append([site["domain"] or site["rel"], plugin, "OK" if plugin.split("/", 1)[0] in installed_plugins else "archivo no encontrado"])
        for missing in missing_active_files:
            plugin_rows.append([site["domain"] or site["rel"], f"{missing}/...", "activo en DB pero carpeta no encontrada"])

        for table_name, rows in analysis["tables"].most_common(25):
            table_rows.append(
                [
                    site["domain"] or site["rel"],
                    table_name,
                    rows,
                    fmt_bytes(analysis["table_bytes"].get(table_name, 0)),
                ]
            )

        if installed_woo or active_woo or analysis["woocommerce_tables"] or options.get("woocommerce_db_version"):
            woo_rows.append(
                [
                    site["domain"] or site["rel"],
                    "SI" if installed_woo else "NO",
                    "SI" if active_woo else "NO",
                    len(analysis["woocommerce_tables"]),
                    options.get("woocommerce_db_version") or options.get("woocommerce_version") or "-",
                    prefix_label or "-",
                ]
            )

    unmapped_dumps = [name for name in dumps if name not in {str(site.get("db_name") or "") for site in installs}]
    unmapped_rows = [[name, rel_for(dumps[name]), fmt_bytes(dumps[name].stat().st_size)] for name in sorted(unmapped_dumps)]

    return f"""
    <section>
      <h2>Bases de datos SQL</h2>
      <p class="muted">Analisis directo de exports <code>.sql</code>, sin importar datos a MySQL. Se leen opciones WordPress, plugins activos, tablas y rastros WooCommerce.</p>
      <h3>Dumps detectados</h3>
      {table(['DB / dump', 'archivo', 'tamano', 'sitio mapeado', 'tablas con inserts', 'tablas WooCommerce/WC'], dump_rows)}
      <h3>Sitios cruzados con DB</h3>
      {table(['sitio', 'DB', 'dump encontrado', 'URL home/siteurl', 'blogname', 'tema activo', 'plugins activos', 'WooCommerce'], site_rows)}
      <h3>Plugins activos segun DB</h3>
      {table(['sitio', 'plugin activo', 'estado archivo'], plugin_rows)}
      <h3>Tablas con mas filas por sitio</h3>
      {table(['sitio', 'tabla', 'filas en INSERT', 'bytes estimados dump'], table_rows)}
      <h3>WooCommerce: archivos vs DB</h3>
      {table(['sitio', 'plugin instalado en archivos', 'activo en DB', 'tablas WC/WooCommerce', 'version/opcion WC', 'prefijos detectados'], woo_rows, 'No se detectaron rastros WooCommerce relevantes en DB o archivos')}
      <h3>Dumps sin sitio WordPress mapeado</h3>
      {table(['DB / dump', 'archivo', 'tamano'], unmapped_rows, 'Todos los dumps SQL estan mapeados a un wp-config.php')}
    </section>
    """


def main() -> None:
    dirs, stats, files, ext_by_dir, errors = scan_tree()
    installs = detect_wp_installs(dirs, stats)
    dumps = find_db_dumps()
    db_analyses = {}
    for site in installs:
        db_name = str(site.get("db_name") or "")
        if db_name and db_name in dumps and db_name not in db_analyses:
            db_analyses[db_name] = analyze_sql_dump(dumps[db_name], str(site.get("table_prefix") or ""))
    for db_name, path in dumps.items():
        if db_name not in db_analyses and db_name != "information_schema":
            db_analyses[db_name] = analyze_sql_dump(path)
    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    top_dirs = sorted(
        [(rel, data) for rel, data in stats.items() if rel != "."],
        key=lambda item: item[1]["size"],
        reverse=True,
    )[:150]
    top_files = sorted(files, key=lambda item: int(item["size"]), reverse=True)[:150]

    root_children = sorted(
        [d for d in dirs if d != "." and "/" not in d],
        key=lambda d: stats.get(d, {}).get("size", 0),
        reverse=True,
    )

    root_rows = []
    for d in root_children:
        status = "activo" if d in EXPECTED_ACTIVE_DIRS else PROTECTED_ROOT_DIRS.get(d, "revisar / posible muerto")
        wp = "si" if any(site["rel"] == d for site in installs) else ""
        root_rows.append([d, ACTIVE_SITES.get(d, ""), status, wp, fmt_bytes(stats[d]["size"]), stats[d]["files"]])

    active_missing = [d for d in EXPECTED_ACTIVE_DIRS if d != "." and d not in dirs]
    orphan_wp = [site for site in installs if site["rel"] not in EXPECTED_ACTIVE_DIRS]

    all_ext = Counter()
    for f in files:
        all_ext[str(f["ext"])] += 1
    ext_rows = [[ext, count] for ext, count in all_ext.most_common(60)]

    media_rows = []
    for top, counter in sorted(ext_by_dir.items(), key=lambda x: x[0]):
        media_count = sum(counter[e] for e in MEDIA_EXTS)
        code_count = sum(counter[e] for e in CODE_EXTS)
        media_rows.append([top, media_count, code_count, sum(counter.values())])

    wc_paths = []
    for rel, data in sorted(stats.items(), key=lambda x: x[1]["size"], reverse=True):
        low = rel.lower()
        if "woocommerce" in low or "/wc-" in low or low.endswith("/wc-logs") or "woocommerce_uploads" in low:
            wc_paths.append([rel, fmt_bytes(data["size"]), data["files"]])
    wc_paths = wc_paths[:120]

    site_sections = "\n".join(render_site_section(site) for site in installs)
    db_section = render_db_section(installs, db_analyses, dumps)
    tree_html = render_tree(dirs, files, stats)

    html_doc = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Analisis estructura Server AG</title>
  <style>
    :root {{
      --bg: #f7f8fa;
      --panel: #ffffff;
      --ink: #1d2430;
      --muted: #667085;
      --line: #d9dee7;
      --brand: #174ea6;
      --warn: #9a5b00;
    }}
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: var(--bg); color: var(--ink); }}
    header {{ background: #111827; color: #fff; padding: 28px 36px; }}
    header h1 {{ margin: 0 0 8px; font-size: 28px; }}
    header p {{ margin: 0; color: #d1d5db; }}
    main {{ padding: 24px 36px 48px; }}
    section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin: 0 0 20px; }}
    h2 {{ margin: 0 0 14px; font-size: 22px; }}
    h3 {{ margin: 20px 0 10px; font-size: 16px; color: #334155; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px 9px; text-align: left; vertical-align: top; }}
    th {{ background: #f1f4f8; color: #334155; position: sticky; top: 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; }}
    .grid > div {{ border: 1px solid var(--line); border-radius: 6px; padding: 10px; background: #fbfcfe; }}
    .muted, .meta {{ color: var(--muted); }}
    .badge {{ display: inline-block; border: 1px solid var(--line); border-radius: 999px; padding: 2px 8px; margin-right: 6px; background: #fff; }}
    .warn {{ color: var(--warn); font-weight: 600; }}
    details {{ margin-left: 16px; border-left: 1px solid #edf0f4; padding-left: 10px; }}
    details > summary {{ cursor: pointer; padding: 3px 0; }}
    details[open] > summary {{ color: var(--brand); }}
    ul {{ list-style: none; margin: 0 0 0 18px; padding: 0; }}
    li {{ padding: 2px 0; }}
    .folder {{ font-weight: 600; }}
    .file {{ color: #344054; }}
    .meta {{ margin-left: 10px; font-size: 12px; }}
    .site h2 {{ color: #123e73; }}
    .toc a {{ margin-right: 12px; white-space: nowrap; }}
  </style>
</head>
<body>
<header>
  <h1>Analisis de estructura del servidor AG</h1>
  <p>Generado: {h(generated)} · Ruta local: <code>{h(str(ROOT))}</code></p>
</header>
<main>
  <section>
    <h2>Resumen</h2>
    <div class="grid">
      <div><b>Tamano total escaneado</b><br>{fmt_bytes(stats['.']['size'])}</div>
      <div><b>Archivos</b><br>{h(stats['.']['files'])}</div>
      <div><b>Carpetas</b><br>{h(len(dirs))}</div>
      <div><b>WordPress detectados</b><br>{h(len(installs))}</div>
    </div>
    <p>
      <span class="badge">Activos esperados: {h(', '.join([f'{v} -> {k}' for k, v in ACTIVE_SITES.items()]))}</span>
    </p>
    <p class="muted">Este reporte no muestra passwords de WordPress. La carpeta <code>.git</code> y la carpeta local <code>.codex</code> se excluyen del escaneo.</p>
  </section>

  <section>
    <h2>Mapa raiz public_html</h2>
    {table(['carpeta', 'dominio esperado', 'estado inicial', 'WordPress', 'tamano', 'archivos'], root_rows)}
  </section>

  <section>
    <h2>Alertas iniciales</h2>
    {table(['tipo', 'detalle'], (
        [['Carpeta activa faltante', x] for x in active_missing] +
        [['WordPress no mapeado como activo', str(x['rel'])] for x in orphan_wp] +
        [['Errores de lectura', e] for e in errors[:50]]
    ), 'Sin alertas iniciales')}
  </section>

  <section>
    <h2>Instalaciones WordPress</h2>
    {site_sections}
  </section>

  {db_section}

  <section>
    <h2>Carpetas mas pesadas</h2>
    {table(['ruta', 'tamano', 'archivos', 'subcarpetas'], [[rel, fmt_bytes(d['size']), d['files'], d['dirs']] for rel, d in top_dirs])}
  </section>

  <section>
    <h2>Archivos mas pesados</h2>
    {table(['ruta', 'tamano', 'modificado', 'extension'], [[f['rel'], fmt_bytes(int(f['size'])), f['mtime'], f['ext']] for f in top_files])}
  </section>

  <section>
    <h2>Rastros WooCommerce / WC</h2>
    <p class="muted">Candidatos para revisar si WooCommerce ya no se usa. No significa borrar automaticamente.</p>
    {table(['ruta', 'tamano', 'archivos'], wc_paths, 'No se detectaron rutas WooCommerce por nombre')}
  </section>

  <section>
    <h2>Distribucion de extensiones</h2>
    {table(['extension', 'cantidad'], ext_rows)}
  </section>

  <section>
    <h2>Medios y codigo por carpeta superior</h2>
    {table(['carpeta superior', 'medios', 'codigo/config', 'total archivos'], media_rows)}
  </section>

  <section>
    <h2>Arbol completo de carpetas y archivos</h2>
    <p class="muted">Abrir/cerrar carpetas desde los triangulos. El arbol incluye todos los archivos escaneados salvo <code>.git</code> y <code>.codex</code>.</p>
    <div class="tree">{tree_html}</div>
  </section>
</main>
</body>
</html>
"""
    OUTPUT.write_text(html_doc, encoding="utf-8")
    print(str(OUTPUT))


if __name__ == "__main__":
    main()
