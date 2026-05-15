# Server AG Working Notes

## Current Business Direction

This repository is a cPanel `public_html` snapshot for AG-related websites. The next strategic direction is to stop depending on WordPress for the active marketing sites and move to a simpler React-based implementation while preserving the visual design with 100% fidelity.

The active future scope is:

- `ag.com.ar`: keep functioning. This is the main AG brand site and the visual base for the unified future design.
- `liggett.com.ar`: keep functioning. Liggett is the same company as AG, currently presented as a separate brand, with additional product lines AG does not yet have.
- `grupoag.com.ar`: keep as institutional site, but remove references to Cobreq, Textar, and their websites/brands.

The following are explicitly out of scope for the refactor:

- `prode`: do not modify. It is a standalone World Cup app and must remain as-is.
- `cobreqargentina`: this site will be removed.
- `textarargentina`: this site will be removed.

In a separate project, the unified B2B catalog for AG and Liggett is being built. Do not recreate that catalog here unless explicitly requested. The marketing-site refactor should assume catalog functionality is moving elsewhere.

## Design Unification Rule

AG and Liggett should be treated as one company moving toward a unified design system:

- Use AG as the base visual language.
- Let Liggett differ mainly through brand colors and product-line content.
- Do not preserve unnecessary WordPress/plugin implementation details when migrating; preserve the rendered design, content, assets, routes, and business intent.
- Liggett has product lines that AG does not currently have, so the content model must allow brand-specific product families.

## Inventory Source Of Truth

Use `server-structure-report.html` as the current inventory and context file. It was updated after database analysis and includes:

- Filesystem summary.
- Active WordPress installs.
- Plugins and themes from files.
- Upload/media breakdown.
- SQL dump mapping.
- WordPress options from DB.
- Active plugins from DB.
- Table sizes and row estimates.
- WooCommerce traces.

Do not rely only on file presence. WordPress content, menus, Elementor data, WPBakery state, plugin settings, forms, products, and many visual decisions live in MySQL exports under `dbdumps/`.

## Current Mapped Sites And Databases

The current DB dump mapping from `server-structure-report.html` is:

| Site | Folder | DB dump | WP prefix | Current role |
| --- | --- | --- | --- | --- |
| `ag.com.ar` | `.` | `dbdumps/ag_new.sql` | `ag_` | Keep. Main AG site and visual base. |
| `liggett.com.ar` | `liggett` | `dbdumps/ag_wp388.sql` | `wpnj_` | Keep. Brand site with extra product lines. |
| `grupoag.com.ar` | `grupoag` | `dbdumps/ag_wp943.sql` | `wpro_` | Keep institutional, remove Cobreq/Textar references. |
| `prode.ag.com.ar` | `prode` | `dbdumps/ag_wp684.sql` | `wpfp_` | Do not modify. Standalone World Cup app. |
| `cobreqargentina.com.ar` | `cobreqargentina` | `dbdumps/ag_wp367.sql` | `wpfm_` | To be removed. |
| `textarargentina.com.ar` | `textarargentina` | `dbdumps/ag_wp290.sql` | `wpdg_` | To be removed. |

There are also unmapped dumps:

- `dbdumps/ag_mapa.sql`
- `dbdumps/information_schema.sql`

## Root / AG Site Notes

The root site is WordPress 6.6.5 with DB `ag_new`, active theme `ag`, and active plugins including:

- `better-wp-security`
- `contact-form-7`
- `elementor`
- `elementor-pro`
- `js_composer`
- `relevanssi`
- `wp-store-locator`

The file tree contains WooCommerce, WooCommerce Admin, YITH WooCommerce plugins, and WooCommerce tables, but the DB report says WooCommerce is not active in the WordPress active plugin list. Treat WooCommerce as legacy/catalog data to inspect, not as a runtime dependency to preserve.

Important source areas:

- `wp-content/themes/ag/`: custom AG theme and primary design source.
- `wp-content/themes/ag/style.css`: AG visual language and component styling.
- `wp-content/themes/ag/functions.php`: menus, sidebars, scripts, WooCommerce hooks, external assets.
- `wp-content/themes/ag/header.php` and `footer.php`: global layout, navigation, social links, metadata, tracking.
- `wp-content/themes/ag/inc/woocommerce.php`: legacy shop/catalog behavior and WooCommerce theme support.
- `wp-content/themes/ag/woocommerce/`: copied WooCommerce template overrides.
- `wp-content/uploads/`: AG media, Visual Composer assets, Elementor CSS, older exports.
- `ml/`: large media/marketplace asset store; treat as assets, not app code.

The AG DB has high-volume content tables:

- `ag_postmeta`: about 100k inserted rows.
- `ag_posts`: about 6.3k inserted rows.
- `ag_term_relationships`, `ag_terms`, `ag_term_taxonomy`, `ag_termmeta`: product/content taxonomy history.
- `ag_wc_product_meta_lookup` and other WooCommerce tables: likely legacy catalog/product data.

## Liggett Site Notes

Liggett is WordPress 6.9.4 with DB `ag_wp388`. The DB report shows active theme `generatepress`, while the filesystem also contains Astra and a minimal `liggett` child theme. Do not assume the child theme contains the real design.

Active plugins from DB include:

- `advanced-custom-fields`
- `elementor`
- `elementor-pro`
- `google-captcha`
- `happy-elementor-addons`
- `wordfence`

Important source areas:

- `liggett/wp-content/uploads/`: largest useful design/content asset source, including catalog PDFs and product/brand imagery.
- `liggett/wp-content/uploads/elementor/`: generated Elementor CSS and assets.
- `liggett/wp-content/themes/liggett/`: minimal child theme; mostly not the design source.
- `liggett/wp-content/themes/generatepress/` and `liggett/wp-content/themes/astra/`: installed themes, but DB currently reports `generatepress` as active.
- `liggett/wp-content/plugins/advanced-custom-fields/` and `custom-post-type-ui/`: indicates possible custom content modeling in DB.

The Liggett DB has meaningful content/state:

- `wpnj_postmeta`: about 8.8k inserted rows.
- `wpnj_posts`: about 1.2k inserted rows.
- Elementor submissions exist, so forms or lead captures may matter.

For a React migration, extract rendered pages, Elementor JSON/meta, media, forms, and product-line content. Do not rebuild the WordPress plugin stack.

## GrupoAG Site Notes

GrupoAG is WordPress 6.9.4 with DB `ag_wp943`, active theme `generatepress`, and active plugins:

- `elementor`
- `elementor-pro`
- `elementor-beta`
- `google-captcha`
- `wordfence`

Future role: institutional site only.

Required content change:

- Remove Cobreq references.
- Remove Textar references.
- Remove links to `cobreqargentina.com.ar` and `textarargentina.com.ar`.
- Reframe GrupoAG around AG and Liggett as the active brands/company sites.

The GrupoAG DB has significant Elementor/page data:

- `wpro_postmeta`: about 6.6k inserted rows.
- `wpro_posts`: about 882 inserted rows.

Expect the visible content and layout to be DB/Elementor-driven rather than theme-file-driven.

## Sites To Remove

`cobreqargentina` and `textarargentina` are not future active sites.

Do not spend refactor effort preserving their WordPress implementations. Their useful role is only as historical reference while removing links/references from `grupoag`.

If removing files later, do it intentionally and only when deployment/routing plans are clear. Do not delete them casually during analysis.

## Prode Protection Rule

Do not modify `prode` unless the user explicitly changes this decision.

It is a standalone World Cup app using WordPress plus the `football-pool` plugin. The DB has active pool tables such as predictions, matches, teams, score history, users, and related plugin state. It is not part of the AG/Liggett marketing-site refactor.

## Security And Hygiene Notes

This repository contains WordPress configuration files and SQL dumps. Do not print secrets or credentials from:

- `wp-config.php`
- nested `wp-config.php` files
- `wp-config.old.php`
- `dbdumps/*.sql`

There are also large operational artifacts and cache/security files:

- `error_log` is very large.
- Wordfence logs and GeoIP databases appear across sites.
- W3 Total Cache and Autoptimize artifacts are present.
- `.htaccess` backups and old files exist.
- `.index.html.swp` exists.

These are not design source and should not be migrated to React.

## React Refactor Guidance

For the future React project:

1. Establish screenshot baselines of the live AG, Liggett, and GrupoAG pages before rebuilding.
2. Export page/content data from the mapped SQL dumps.
3. Extract Elementor layouts from postmeta where applicable.
4. Extract AG theme CSS/design tokens and normalize them into a shared design system.
5. Use AG as the default style; add Liggett brand color/theme overrides.
6. Keep static media under a planned asset pipeline, especially `wp-content/uploads`, `liggett/wp-content/uploads`, and `ml`.
7. Preserve SEO-relevant routes and redirects for the sites that remain.
8. Do not port WordPress core, plugin internals, cache folders, Wordfence data, or admin-only assets.

The minimum future public surface should be:

- `ag.com.ar`
- `liggett.com.ar`
- `grupoag.com.ar`

Everything else should be treated as external, deprecated, archived, or protected according to the rules above.
