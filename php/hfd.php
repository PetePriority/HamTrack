<?php
require __DIR__ . '/vendor/autoload.php';

$loader = new Twig_Loader_Filesystem('templates');
$twig = new Twig_Environment($loader);

$servername = "<sql_host>";
$username = "<sql_username>";
$password = "<sql_password>";
$database = "<sql_db>";



$pdo = new PDO('mysql:host=$servername;dbname=$sql_db',
	       $username,
	       $password);

include('functions.inc.php');

// Daily totals
$sql = "SELECT
DATE(start + INTERVAL 12 HOUR) start,
DATE(start + INTERVAL 12 HOUR) start_order,
SUM(duration) duration,
SUM(distance) distance,
circumference
FROM hamstersession
GROUP BY start_order ORDER BY start_order DESC";
//WHERE start >= now() - INTERVAL 1 DAY;";
$tables = array();
$rows = get_table($pdo, $sql, "Daily totals", array('min', 'km', 'mi'));
$new_table = array(
    "title" => "Daily totals",
    "text" => "(A hamster day starts at noon of the previous day)",
    "rows" => $rows
);
array_push($tables, $new_table);

// Monthly totals
$sql = "SELECT
start + INTERVAL 12 HOUR temp,
CONCAT(YEAR(start + INTERVAL 12 HOUR),'-',MONTH(start + INTERVAL 12 HOUR)) start,
CONCAT(YEAR(start + INTERVAL 12 HOUR),'/',MONTH(start + INTERVAL 12 HOUR)) start_order,
SUM(duration) duration,
SUM(distance) distance,
circumference
FROM hamstersession
GROUP BY start_order ORDER BY start_order DESC";
//WHERE start >= now() - INTERVAL 1 DAY;";
$rows = get_table($pdo, $sql, "Daily totals", array('h', 'km', 'mi'));
$new_table = array(
    "title" => "Monthly totals",
    //"text" => "(A hamster day starts at noon of the previous day)",
    "rows" => $rows
);
array_push($tables, $new_table);


// Session details
$sql = "SELECT * FROM hamstersession
WHERE start >= CURDATE() - INTERVAL 2 DAY
ORDER BY start DESC";
$rows = get_table($pdo, $sql, "Sessions", array('min', 'm', 'ft'));
$new_table = array(
    "title" => "Sessions",
    "rows" => $rows
);
array_push($tables, $new_table);

echo $twig->render('index.html', array(
    "tables" => $tables
));
?>
