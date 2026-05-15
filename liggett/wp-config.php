<?php

/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'ag_wp388' );

/** MySQL database username */
define( 'DB_USER', 'ag_wp388' );

/** MySQL database password */
define( 'DB_PASSWORD', '1!p6Sk4[Il' );

/** MySQL hostname */
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
define( 'AUTH_KEY',         'atlstp98styfk6267bj6yxlssah8d9y0zvnfqquxgvnyyy8zx9qpgtpapqgxdimr' );
define( 'SECURE_AUTH_KEY',  'g5suwfwymssv5brblzpckcyyhclk26df8x64c7y3buntrr3fei6uhrh2prsy5o0g' );
define( 'LOGGED_IN_KEY',    'xwy6hwro7fr93ionptrjtsouzctdir3xksivwm2wajtbkogwmakjrtpk0kasjtgp' );
define( 'NONCE_KEY',        'k0d3i8unet3ntmk3ognxabw9xfl7ucrnldlzfbzla8dsatwy2ia8crcilplfcii4' );
define( 'AUTH_SALT',        'ppzs7ajdzjf7bpgnplyvuwrwkipo6rdfnf4xvjucdk4rorw0hkalcbz6z75br2ew' );
define( 'SECURE_AUTH_SALT', '0xad1ljeg93fjtjaxx8jak1p4pfwi2bdqyhuzecn82axhxnwkmqryve7jsiescrx' );
define( 'LOGGED_IN_SALT',   'wpzpuhbe4j0cxkpyhuuavvf5qlbdvj2yxx1vu6cjtjhusnformbve1dw1uxkseyq' );
define( 'NONCE_SALT',       '156bdlrxnih7yip5leg9ed06rvzrlx5heidrnawdwnq6wlwawye0fredygxbkvcl' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wpnj_';

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
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
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
