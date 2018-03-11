<html>
    <head>
        <title>CIS 322 REST-api demo: Laptop list</title>
    </head>

    <body>

        <h1>Get All Times</h1>
        <ul>
            <?php
            $service = 'http://laptop-service/';
            $field = 'listAll';
            $format = '/json';

            $json = file_get_contents($service . $field . $format);
            $obj = json_decode($json);

            $times = array();

            if($field == 'listAll'){
              array_push($times, $obj->km);
              array_push($times, $obj->open);
              array_push($times, $obj->close);
            }

            if($field == 'listOpenOnly'){
              array_push($times, $obj->open);
            }

            if($field == 'listCloseOnly'){
              array_push($times, $obj->close);
            }

            $amt_fields = count($times);
            $amt_data = count($times[0]);

            for ($i=0; $i<$amt_data; $i++){
              $out = "";
              for ($j=0; $j<$amt_fields; $j++){
                $out = $out." ".$times[$j][$i];
              }
              echo "<li> $out </li>";
            }


            ?>
        </ul>
    </body>
</html>
