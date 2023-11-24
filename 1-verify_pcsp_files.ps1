# Define thread limit
$thread = 8
$inputPath = "$(Get-Location)\inputs\"
$outputPath = "$(Get-Location)\outputs\"

# Use the Get-ChildItem cmdlet to list files in the directory
$files = Get-ChildItem -Path $inputPath -Filter *.pcsp | Where-Object { $_.PSIsContainer -eq $false }

# Check the number of files
if ($files.Count -eq 0) {
    Write-Host "No pcsp files found in the directory."
    Exit
} else {
    Write-Host "$($files.Count) pcsp files found in the directory, starting verification..."
}

if (-not (Test-Path -Path $outputPath -PathType Container)) {
    New-Item -Path $outputPath -ItemType Directory
}
$startTime = Get-Date
$Job = $files | ForEach-Object -Parallel { 
    $executablePath = "C:\Program Files\Process Analysis Toolkit\Process Analysis Toolkit 3.5.1\PAT3.Console.exe"
    $input = "$(Get-Location)\inputs\$($_.Name)"
    $output = "$(Get-Location)\outputs\$($_.Name -replace '\.[^.]+$', ".txt")"
    $arguments = "-pcsp `"$input`" `"$output`""
    
    Write-Host "Verifying $($_.Name)"
    Start-Process -FilePath $executablePath -ArgumentList $arguments -Wait
 } -ThrottleLimit $thread -AsJob 
$job | Receive-Job -Wait -AutoRemoveJob
$endTime = Get-Date
$elapsedTime = $endTime - $startTime
Write-Host "Count: $($files.Count) Elapsed Time: $elapsedTime"