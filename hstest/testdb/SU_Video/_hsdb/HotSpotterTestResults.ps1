$name = Get-Content -Path name_table.csv | Select-Object -Skip 2 | Foreach-Object {$_ -replace "#", ""}| ConvertFrom-Csv
$chip = Get-Content -Path chip_table.csv | Select-Object -Skip 2 | Foreach-Object {$_ -replace "#", ""}| ConvertFrom-Csv
$image = Get-Content -Path image_table.csv | Select-Object -Skip 2 | Foreach-Object {$_ -replace "#", ""}| ConvertFrom-Csv
$Labels = Import-Csv DB_Labels.csv

$chip|
   %{

      $ImgID=$_.ImgID
      $m=$image|?{$_.gid -eq $ImgId}
      $_.ImgID=$m.gname
          
      $NameID=$_.NameID
      $m=$name|?{$_.nid -eq $NameID}
      $_.NameID=$m.name
    }


$grouped = $chip | Group-Object ImgID, NameID | %{ $_.Group | Select ImgID, NameID -First 1} | Sort  ImgID, NameID
$regrouped = $grouped | group ImgID


$HotSpotter = $regrouped | foreach {

    $CatName = ""
    $_.group | %{$CatName = $CatName + $_.NameID + ", "}
    $CatName = $CatName.Substring(0,$CatName.Length-2)


    [pscustomobject] @{
        ImageName = $_.Name
        HotSpotterCatName = $CatName 
    }
}

$Labels = $Labels | %{

      $ImgID=$_.'New Name'
      $h=$HotSpotter|?{$_.ImageName-eq $ImgID}

      $HotSpotterCatName = $h.HotSpotterCatName


    [pscustomobject] @{
        Cat = $_.Cat
        HotSpotterCatName = $HotSpotterCatName
        'New Name'= $ImgID
        
    }

    }

$labels | Export-Csv DB_Large_Labels_And_Hotspotter.csv -noType

$Results = Import-Csv DB_Large_Labels_And_Hotspotter.csv

$assignmentComplete = $False

while (-Not $assignmentComplete) {

$ResultsGrouped = $Results | Group-Object Cat, HotSpotterCatName

$sortedResults = $ResultsGrouped | foreach {
	[pscustomobject] @{
                      Cat = $_.group | select -unique -expand Cat
                      HotSpotterCatName = $_.group | select -unique -expand HotSpotterCatName 
                      ImageCount = $_.Count}
} | sort Cat, ImageCount -d

$winningLabel = $sortedResults | group Cat | foreach {

$maxCount =  ($_.group | measure-object  -Property ImageCount -maximum).Maximum
$sum = ($_.group | measure-object  -Property ImageCount -sum).Sum
$WeightedCount = $maxCount * ($maxCount / $sum)
$correctNameMatch = $_.group | ?{$_.ImageCount -eq $maxCount} | select -unique
                      [pscustomobject] @{
                               Cat = $_.Name
                                HotSpotterCatName =  $correctNameMatch.HotSpotterCatName
                                ImageCount = $correctNameMatch.ImageCount
                                WeightedCount = $WeightedCount
}
}




$groupedWinningLabel = $winningLabel | group HotSpotterCatName

$assignmentComplete = $true

	 $markedForRemoval = $groupedWinningLabel | %{
	
	If ($_.Count -gt 1) { 
	     $assignmentComplete = $False
	     $group = $_.group | sort WeightedCount -d
	     $removalGroup = ({$group}.Invoke())
	     $removalGroup.RemoveAt(0)
	     $removalGroup | %{  
	                       [pscustomobject] @{            
	                               Cat = $_.Cat
	                                HotSpotterCatName =  $_.HotSpotterCatName
	                         }
	             }
	}
}

 if (-Not $assignmentComplete) {

	For ( $i=0; $i -lt ($markedForRemoval | measure).count) {
	
		$Results = $Results | where {!(($_.Cat -eq $markedForRemoval[$i].Cat) -and  ($_.HotSpotterCatName -eq $markedForRemoval[$i].HotSpotterCatName))}
	$i++
	}
}

}

$Results = Import-Csv DB_Large_Labels_And_Hotspotter.csv

$Results = $Results | % {
                       [pscustomobject] @{            
                               Cat = $_.Cat
                                HotSpotterCatName =  $_.HotSpotterCatName
                                winningLabel = ''
                                CorrectIdentification = 0
                               'New Name' = $_.'New Name'

                         }
}


For ( $i=0; $i -lt ($winningLabel| measure).count) {

	$Results | % {
	       if ($_.Cat -eq $winningLabel[$i].Cat) {$_.winningLabel = $winningLabel[$i].HotSpotterCatName}
                  if($_.HotSpotterCatName -eq $_.winningLabel ) {$_.CorrectIdentification = 1}
	}
	$i++
}

"Accuracy for this run:"
($results | where CorrectIdentification -eq 1).count / $results.count 


$results | Export-Csv DB_Large_Labels_And_Hotspotter_Accuracy.csv -noType


