<?php header('Access-Control-Allow-Origin: *'); ?>

<?php 


if(!empty($_POST['pdfdata']) && !empty($_POST['id']) && !empty($_POST['country'])){
    $data = base64_decode($_POST['pdfdata']);
    $fname = ("S21/" . $_POST['country'] . "/Certificate-". $_POST['id'] ."-Summer2021.pdf"); // name the file
    $file = fopen("" . $fname, 'w'); // open the file path
    fwrite($file, $data); //save data
    fclose($file);
    
    echo "wrote " . $fname;
} else {
    echo "No Data Sent";
}

?>