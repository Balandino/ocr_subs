$pathway = "C:\Video Sub Finder\TXTImages"
Remove-Item $pathway -Recurse -Include *.png
Remove-Item $pathway -Recurse -Include *.jpeg

$pathway =  "C:\Video Sub Finder\RGBImages"
Remove-Item $pathway -Recurse -Include *.jpeg
