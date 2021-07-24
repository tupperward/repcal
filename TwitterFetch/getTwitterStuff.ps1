
$options = Import-Csv $PSScriptRoot\csv\Thermidor.csv

foreach ($option in $options) {
  $dailyItem = $option.item
  $searchTerm = "@sansculotides $dailyItem"
  Start-Process "https://twitter.com/search?q=$searchTerm"
}
