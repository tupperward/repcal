
$options = Import-Csv $PSScriptRoot\csv\Ventose.csv

foreach ($option in $options) {
  $dailyItem = $option.item
  $searchTerm = "@sansculotides $dailyItem"
  Start-Process "https://twitter.com/search?q=$searchTerm"
}
