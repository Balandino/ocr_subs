$pathway = "C:\Video Sub Finder\TXTImages"
$jpegs = Get-ChildItem -Path $pathway -Filter *.jpeg
$count = 0
$TOTAL_COUNT =((Get-ChildItem -Path $pathway -Filter *.jpeg -Recurse).BaseName | Sort length -Descending).Count

foreach ($jpeg in $jpegs) {
   $name_no_ext = (Get-Item $jpeg).Basename
   $png = "$pathway\$name_no_ext.png"
   ffmpeg -i $jpeg $png -y -vframes 1 -hide_banner -loglevel error

   $count = $count + 1
   Write-Host "$count/$TOTAL_COUNT Processed"
}

Write-Host "Completed!"

# Write-Host "Processing complete, deleting jpegs"
Remove-Item $pathway -Recurse -Include *.jpeg
