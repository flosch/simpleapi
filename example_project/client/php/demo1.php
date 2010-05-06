<?php
    require_once("class.client.php");
    
    $client = new Client(
        $ns="http://localhost:8888/api/calculator/multiple/",
        $access_key="91d9f7763572c7ebcce49b183454aeb0"
    );
    print("5 * 10 = ".$client->multiply(array('a'=>5, 'b'=>10))."<br />");
    
    $client = new Client(
        $ns="http://localhost:8888/api/functions/",
        $access_key="91d9f7763572c7ebcce49b183454aeb0"
    );
    try {
        print("This fails remotely...");
        $client->fail();
    } catch (RemoteException $e) {
        print($e."<br />");
    }

    $client = new Client("http://localhost:8888/api/misc/");
    print("Cool is ".$client->return_my_value(array('val' => 'cool')));

?>