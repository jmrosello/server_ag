<?php

// BEGIN iThemes Security - No modifiques ni borres esta línea
// iThemes Security Config Details: 2
define( 'DISALLOW_FILE_EDIT', true ); // Desactivar editor de archivos - Seguridad > Ajustes > Ajustes WordPress > Editor de archivos
define( 'FORCE_SSL_ADMIN', true ); // Redirige todas las peticiones de páginas HTTP a HTTPS - Seguridad > Ajustes > Secure Socket Layers (SSL) > SSL en el escritorio
// END iThemes Security - No modifiques ni borres esta línea

/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://codex.wordpress.org/Editing_wp-config.php
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'ag_new');

/** MySQL database username */
define('DB_USER', 'ag_mica');

/** MySQL database password */
define('DB_PASSWORD', 'XsK21jYkuJbYM8Xo');

/** MySQL hostname */
define('DB_HOST', 'localhost');

/** Database Charset to use in creating database tables. */
define('DB_CHARSET', 'utf8mb4');

/** The Database Collate type. Don't change this if in doubt. */
define('DB_COLLATE', '');

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define('AUTH_KEY',         'uihriw0pq9ojdwgdddvqlvpjvj11apjf7cole6cfdl9ctsisvwvecqmsp84se7km');
define('SECURE_AUTH_KEY',  'ojbjun1gmnf5lmyo35slj6rb9her9wrs8smzgzkoet2rhlrmbdpxncigufl2ihnj');
define('LOGGED_IN_KEY',    'v7hwhhiaaxtb3ibyhekyhhh0avtke4iugcud8ryathfr1hk23j27bzzrecvqv0jd');
define('NONCE_KEY',        'lql3myiwx194lmcjcn9frfctqjq3ldd8lxujliexgecbej2yi2ez71oggeafparn');
define('AUTH_SALT',        'urj8klgjlquwjxh16a4rjiokw9vwel8glb4tx2dbcg8wqihsr6rxpbbpiagcp8ex');
define('SECURE_AUTH_SALT', 'yclncxwrdfebevwdw4qobxlsfbsrv1c3d3unmerez6derxwc2yzw2eibr6q1r9nd');
define('LOGGED_IN_SALT',   'lbs7qzxsex0qotmbverzceh0wpaj7cy9jj6qwvc9izi9mtzl8nf6ud4yeubc6kvh');
define('NONCE_SALT',       'cvafzs33dklnbptip3ltphhezmbhtgesnpr0toxgg3xcs6zq6bm7npn5i9d7hnf3');

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix  = 'ag_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the Codex.
 *
 * @link https://codex.wordpress.org/Debugging_in_WordPress
 */
define('WP_DEBUG', false);

/* That's all, stop editing! Happy blogging. */


/** Absolute path to the WordPress directory. */
if ( !defined('ABSPATH') )
	define('ABSPATH', dirname(__FILE__) . '/');

/** Sets up WordPress vars and included files. */
require_once(ABSPATH . 'wp-settings.php');
/*
define( 'ALLOW_UNFILTERED_UPLOADS', true );*/