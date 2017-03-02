<?php
use PhpUnitsOfMeasure\PhysicalQuantity\Length;
use PhpUnitsOfMeasure\PhysicalQuantity\Time;

function get_table($pdo, $sql, $title, $units)
{
    $rows = array();
    foreach ($pdo->query($sql) as $row) {
        $start = $row['start'];
        $duration = new Time(round($row['duration'],1), 's');
        $distance = new Length(round($row['distance'],1), 'cm');
        $circumference = new Length($row['circumference'], 'cm');
        $revolutions = $distance->toUnit('cm') / $circumference->toUnit('cm');
        //$distance_ft = $distance_cm / 100.0 * 3.28084;
        $rpm = $revolutions / $duration->toUnit('min');

        $new_row = array(
            "start" => $start,
            "duration" => number_format($duration->toUnit($units[0]), 1, '.', '')." ".$units[0],
            "distance" => number_format($distance->toUnit($units[1]), 1, '.', '')." ".$units[1],
            "distance_imp" => number_format($distance->toUnit($units[2]), 1, '.', '')." ".$units[2],
            "rpm" => number_format($rpm, 1, '.', '')
        );
        array_push($rows, $new_row);
    }
    return $rows;
}
?>
