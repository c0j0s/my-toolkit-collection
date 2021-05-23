$totalTrue = 0
$totalFalse = 0
$totalChecked = 0

Get-ChildItem -Directory | ForEach-Object { 

    $current_folder = $_.FullName

    "============================="
    $_.Name
    "============================="

    Get-ChildItem $current_folder -Directory | ForEach-Object { 
        $query = $_.Name -replace '[(].*[)]', ''
        $HTML = Invoke-RestMethod "www.themoviedb.org/search?query=$query"  

        $Pattern = '<a(?<a>.*)class="title result"(?<b>.*)>(?<Title>.*)<\/a>'
        $matchResult = $HTML -match $Pattern
        "【$matchResult】 $query"

        if($matchResult){ $totalTrue++ }ELSE{ $totalFalse++ }
        $totalChecked++
    }

}

"=========================================="
"检查总数：【$totalChecked】 正常：【$totalTrue】 失败：【$totalFalse】"
read-host “Press ENTER to exit...”