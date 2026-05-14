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
define( 'DB_NAME', 'ag_wp367' );

/** Database username */
define( 'DB_USER', 'ag_wp367' );

/** Database password */
define( 'DB_PASSWORD', '(VYS33[Vp3' );

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
define( 'AUTH_KEY',         'dpvnlu7tpkxt0ebi5ixk0l5ernvwppbdlios6rwiyjlnge1qpbmrknchxxyynipd' );
define( 'SECURE_AUTH_KEY',  'choois4q2m1o8ctahqcratwmlplfs6gyt271jzc6eakze8w5p9zu6xvr1zawlfgc' );
define( 'LOGGED_IN_KEY',    'tyjlukumron9dktf60xxyefgcwdzvgaov4yx9b1cqst78fzdphxqg5xrtnqtcki4' );
define( 'NONCE_KEY',        '96myycvuudhje3sxngzlbpdwlnrn6sx5reowrytab6htdrb2eqra2hljsq8ooaij' );
define( 'AUTH_SALT',        'kcvgkrfwbb2jbvrmxv04s07xaea5iqdwjmn6qoy9gmgjhngi1tfjedgnp3zk6trb' );
define( 'SECURE_AUTH_SALT', 'xr9pmxt6tdc0jfg9mupujztpqxrelpoouaw936sw0cmvzg6zqza0epu2ycqvahvg' );
define( 'LOGGED_IN_SALT',   '8xizxfqvg3zqkhydscksq9ryj44v08votamathji9opm946ijopzo0toxfjqqtdv' );
define( 'NONCE_SALT',       'i3rjih3yhi7r3l7gjxrfzhgiovb8uqia4n78sxlwndsp6qlbtvogqgzlc6pxjet0' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wpfm_';

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
