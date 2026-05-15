<?php
/** Enable W3 Total Cache */
define('WP_CACHE', true); // Added by W3 Total Cache


/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/documentation/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'ag_wp290' );

/** Database username */
define( 'DB_USER', 'ag_wp290' );

/** Database password */
define( 'DB_PASSWORD', 'pTO(!268NS' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         '1abphwmhwkx3icmreumgzv8mtwjfgjertuvtjxeymgcwehit4ko25avbgmtmpu5e' );
define( 'SECURE_AUTH_KEY',  'ntxhmdqfjwzhsqmpvgbbrt8koccbdt9j5tps15fkfofclzohymdhijdt0ij8kavp' );
define( 'LOGGED_IN_KEY',    'uumb2zll3jfbzitcwvk6owyy0cqtjv9hqtkmymyjeosfg3a56jqeayqtxoadfkij' );
define( 'NONCE_KEY',        'o4wpxb3m1ficr1lbnere44tyciopfiphwz9ykxguwwwqkub58r0n9zrzszytikas' );
define( 'AUTH_SALT',        'bgdvosnzsjptv3dyqnmcleztmxhnzdps8lrodzagwzwbowascra6hafxpdhfmtmv' );
define( 'SECURE_AUTH_SALT', 'faaawlfe5x8ly0fva1h1tz5owvigflzzb7xhypqbsbbckewybovbq4oybfn8vlq7' );
define( 'LOGGED_IN_SALT',   'ubmj0nd9r8wtfgad7togznfjsyf6fcvw5fo7ddih1xij8urqumbuxvnxtsc9h9if' );
define( 'NONCE_SALT',       'nqvol1slerufohppxag0rr23wro8gkp9c1y7tjg1zgdcmhq0bqcpc9fqijqpkasi' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wpdg_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/documentation/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" line. */



/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
