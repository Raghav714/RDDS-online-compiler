<!DOCTYPE html>
<html>

<head>
    <title>RDDS Compiler</title>
    
    <link rel="stylesheet" type="text/css" href="css/main.css" />


    <meta name="viewport" content="width=device-width, user-scalable=no">
</head>

<body>
    <div id="topBar">
        <span id="title"><em>RDDS</em> Compiler</span>
    </div>

    <div id="console">
        <div id="settings">
            

        </div>

        <div id="content">
            <div id="left">
	<form method="post" action="index1.php">
                <textarea maxlength="5000000000000" rows="19" cols="60" id="jscontent"  name="textarea">
<?php

if (isset($_POST['textarea']))
{
$textarea=$_POST['textarea'];
$myfile = fopen("test.src", "w") or die("Unable to open file!");
fwrite($myfile, $textarea. PHP_EOL);
fclose($myfile);
echo $textarea;
}
    ?>

                </textarea>
<?php
echo "-----INPUT-----";?>
	<textarea maxlength="5000000000000" rows="2" cols="60" id="jscontent"  name="inp" placeholder= "input" style = "border: solid;">
<?php
   if (isset($_POST['inp']))
{
$textarea=$_POST['inp'];
$myFile = "input.txt";
file_put_contents($myFile,$textarea);
}
    ?>
		
             </textarea>

<button class="material-button red" name = "compile"><span>Compile</span></button>
            <!--<button class="material-button red" onclick="reloadPage()"><span>Reload Page</span></button>-->
       


            

</form>
<form>
<button class="material-button blue" onclick=dj()><span>clear editor</span></button>
<script>
function dj()
{
window.location.href="http://127.0.0.1/index1.php";
}
</script>
</form>
            <a href="https://github.com/" target="_blank"><button class="material-button orange"><span>View Github</span></button></a>

            <a href="" target="_blank"><button class="material-button orange"><span>Main Website</span></button></a>
            </div>

            <div id="right">
<?php
echo "OUTPUT </br> ";
  if (isset($_POST['textarea']))
{
echo shell_exec("python3 /home/raghav/RDDS/code/compiler.py -o OUT test.src");
echo shell_exec("./a.out < input.txt"); 
}
    ?>
            </div>
        </div>
    </div>

</body>

</html>
