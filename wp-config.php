<?php

// BEGIN Solid Security - No modifiques ni borres esta línea
// Solid Security Config Details: 2
define( 'DISALLOW_FILE_EDIT', true ); // Desactivar editor de archivos - Seguridad > Ajustes > Ajustes WordPress > Editor de archivos
define( 'FORCE_SSL_ADMIN', true ); // Redirigir todas las solicitud de páginas HTTP a HTTPS - Seguridad > Ajustes > Forzar SSL
// END Solid Security - No modifiques ni borres esta línea

define( 'ITSEC_ENCRYPTION_KEY', 'IC0yKTlmQVAmZSsmcUk5bjEzZm5Re0hZT35HTGNIIyU6SFsrcld3ZVByI2ouV15CfV1AYz06eSEjKHQmSH5CYw==' );

define('WP_AUTO_UPDATE_CORE', 'minor');// This setting is required to make sure that WordPress updates can be properly managed in WordPress Toolkit. Remove this line if this WordPress website is not managed by WordPress Toolkit anymore.

/**
 * Configuración básica de WordPress.
 *
 * Este archivo contiene las siguientes configuraciones: ajustes de MySQL, prefijo de tablas,
 * claves secretas, idioma de WordPress y ABSPATH. Para obtener más información,
 * visita la página del Codex{@link http://codex.wordpress.org/Editing_wp-config.php Editing
 * wp-config.php} . Los ajustes de MySQL te los proporcionará tu proveedor de alojamiento web.
 *
 * This file is used by the wp-config.php creation script during the
 * installation. You don't have to use the web site, you can just copy this file
 * to "wp-config.php" and fill in the values.
 *
 * @package WordPress
 */

// ** Ajustes de MySQL. Solicita estos datos a tu proveedor de alojamiento web. ** //
/** El nombre de tu base de datos de WordPress */
define('DB_NAME', 'ag_new');

/** Tu nombre de usuario de MySQL */
define('DB_USER', 'ag_mica');

/** Tu contraseña de MySQL */
define('DB_PASSWORD', 'XsK21jYkuJbYM8Xo');

/** Host de MySQL (es muy probable que no necesites cambiarlo) */
define('DB_HOST', 'localhost');

/** Codificación de caracteres para la base de datos. */
define('DB_CHARSET', 'utf8mb4');

/** Cotejamiento de la base de datos. No lo modifiques si tienes dudas. */
define('DB_COLLATE', '');

// Disabled by Performance Manager

define( 'WP_HOME', 'https://www.ag.com.ar' );
define( 'WP_SITEURL', 'https://www.ag.com.ar' );

/**#@+
 * Claves únicas de autentificación.
 *
 * Define cada clave secreta con una frase aleatoria distinta.
 * Puedes generarlas usando el {@link https://api.wordpress.org/secret-key/1.1/salt/ servicio de claves secretas de WordPress}
 * Puedes cambiar las claves en cualquier momento para invalidar todas las cookies existentes. Esto forzará a todos los usuarios a volver a hacer login.
 *
 * @since 2.6.0
 */
define('AUTH_KEY', 'uihriw0pq9ojdwgdddvqlvpjvj11apjf7cole6cfdl9ctsisvwvecqmsp84se7km'); // Cambia esto por tu frase aleatoria.
define('SECURE_AUTH_KEY', 'ojbjun1gmnf5lmyo35slj6rb9her9wrs8smzgzkoet2rhlrmbdpxncigufl2ihnj'); // Cambia esto por tu frase aleatoria.
define('LOGGED_IN_KEY', 'v7hwhhiaaxtb3ibyhekyhhh0avtke4iugcud8ryathfr1hk23j27bzzrecvqv0jd'); // Cambia esto por tu frase aleatoria.
define('NONCE_KEY', 'lql3myiwx194lmcjcn9frfctqjq3ldd8lxujliexgecbej2yi2ez71oggeafparn'); // Cambia esto por tu frase aleatoria.
define('AUTH_SALT', 'urj8klgjlquwjxh16a4rjiokw9vwel8glb4tx2dbcg8wqihsr6rxpbbpiagcp8ex'); // Cambia esto por tu frase aleatoria.
define('SECURE_AUTH_SALT', 'yclncxwrdfebevwdw4qobxlsfbsrv1c3d3unmerez6derxwc2yzw2eibr6q1r9nd'); // Cambia esto por tu frase aleatoria.
define('LOGGED_IN_SALT', 'lbs7qzxsex0qotmbverzceh0wpaj7cy9jj6qwvc9izi9mtzl8nf6ud4yeubc6kvh'); // Cambia esto por tu frase aleatoria.
define('NONCE_SALT', 'cvafzs33dklnbptip3ltphhezmbhtgesnpr0toxgg3xcs6zq6bm7npn5i9d7hnf3'); // Cambia esto por tu frase aleatoria.

/**#@-*/

/**
 * Prefijo de la base de datos de WordPress.
 *
 * Cambia el prefijo si deseas instalar multiples blogs en una sola base de datos.
 * Emplea solo números, letras y guión bajo.
 */
$table_prefix = 'ag_';


/**
 * Para desarrolladores: modo debug de WordPress.
 *
 * Cambia esto a true para activar la muestra de avisos durante el desarrollo.
 * Se recomienda encarecidamente a los desarrolladores de temas y plugins que usen WP_DEBUG
 * en sus entornos de desarrollo.
 */
define('WP_DEBUG', false);

/* ¡Eso es todo, deja de editar! Feliz blogging */
// define('WP_MEMORY_LIMIT', '256M');

/** WordPress absolute path to the Wordpress directory. */
if ( !defined('ABSPATH') )
	define('ABSPATH', dirname(__FILE__) . '/');

/** Sets up WordPress vars and included files. */
require_once(ABSPATH . 'wp-settings.php');

