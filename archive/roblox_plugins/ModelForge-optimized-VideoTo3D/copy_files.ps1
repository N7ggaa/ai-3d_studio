# PowerShell script to copy source files to the optimized directory

$sourceDir = "c:\Users\dell\Downloads\ModelForge-original\VideoTo3D\src"
$destDir = "c:\Users\dell\Downloads\ModelForge-optimized\VideoTo3D\src"

# Copy all Lua files
Get-ChildItem -Path $sourceDir -Recurse -Filter "*.lua" | ForEach-Object {
    $relativePath = $_.FullName.Substring($sourceDir.Length + 1)
    $destPath = Join-Path -Path $destDir -ChildPath $relativePath
    
    $destDirPath = [System.IO.Path]::GetDirectoryName($destPath)
    if (-not (Test-Path -Path $destDirPath)) {
        New-Item -ItemType Directory -Path $destDirPath -Force | Out-Null
    }
    
    Copy-Item -Path $_.FullName -Destination $destPath -Force
    Write-Host "Copied: $relativePath"
}

Write-Host "All files copied successfully!"
