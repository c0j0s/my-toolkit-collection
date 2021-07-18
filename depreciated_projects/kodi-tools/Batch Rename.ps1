Get-ChildItem | foreach {
$ep = $_.Name.Substring(0,1)
$new = $_.Name -replace "$ep集.mp4", "$ep.mp4"
#$new = $_.Name -replace '[\[]', ''
$new + " | " + $ep
#Rename-Item @$_ @$new

}