# Define the path to the directory you want to list files from
$workingDirectory = Get-Location
$inputPath = "$workingDirectory\inputs\"
$outputPath = "$workingDirectory\outputs\"
$executablePath = "C:\Program Files\Process Analysis Toolkit\Process Analysis Toolkit 3.5.1\PAT3.Console.exe"

# Use the Get-ChildItem cmdlet to list files in the directory
$files = Get-ChildItem -Path $inputPath -Filter *.pcsp | Where-Object { $_.PSIsContainer -eq $false }

# Check the number of files
if ($files.Count -eq 0) {
    Write-Host "No pcsp files found in the directory."
    Exit
} else {
    Write-Host "$($files.Count) pcsp files found in the directory, starting verification..."
}

# Loop through the list of files and do something with each file
foreach ($file in $files) {
    $input = "$inputPath$($file.Name)"
    $output = "$outputPath$($file.Name -replace '\.[^.]+$', ".txt")"
    $arguments = "-pcsp `"$input`" `"$output`""
    Write-Host "Verifying: $($file.Name)"

    $scriptBlock = {
        param($arg, $exe)
        & Start-Process -FilePath $exe -ArgumentList $arg -Wait
    }

    Start-Job -ScriptBlock $scriptBlock -ArgumentList $arguments, $executablePath
}

# Wait for all jobs to finish
Get-Job | Wait-Job

# Retrieve job results if needed (optional)
# Get-Job | Receive-Job

# Cleanup jobs
Remove-Job *