# Build script for VideoTo3D plugin
# This script will create a single .rbxm file that can be imported into Roblox Studio

$buildDir = "$PSScriptRoot\build"
$outputFile = "$buildDir\VideoTo3D.rbxm"

# Create build directory if it doesn't exist
if (-not (Test-Path -Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
}

# Create a temporary directory for the plugin
$tempDir = "$env:TEMP\VideoTo3D_Build_$(Get-Date -Format 'yyyyMMdd_HHmmss')
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Copy all necessary files to the temp directory
$filesToCopy = @(
    "src\init.lua",
    "src\Main.lua",
    "src\Theme.lua",
    "src\VideoTo3D.lua",
    "src\Components\*.lua",
    "src\Services\*.lua",
    "src\Utils\*.lua"
)

foreach ($filePattern in $filesToCopy) {
    $sourcePath = Join-Path -Path $PSScriptRoot -ChildPath $filePattern
    $destDir = Join-Path -Path $tempDir -ChildPath (Split-Path -Path $filePattern -Parent)
    
    if (-not (Test-Path -Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    Copy-Item -Path $sourcePath -Destination $destDir -Recurse -Force
}

# Create the plugin script
$pluginScript = @"
local Plugin = script.Parent
local Main = require(script.Parent.Main)

local function init()
    local success, result = pcall(function()
        return Main.new(Plugin)
    end)
    
    if not success then
        warn("Failed to initialize VideoTo3D plugin:", result)
        error(result)
    end
    
    return result
end

return init()
"@

# Create the plugin structure
$plugin = New-Object -TypeName System.Collections.ArrayList

# Create the plugin instance
$pluginInstance = @{
    "Name" = "VideoTo3D"
    "ClassName" = "Plugin"
    "Children" = @(
        @{
            "Name" = "Main"
            "ClassName" = "ModuleScript"
            "Source" = (Get-Content -Path "$PSScriptRoot\src\Main.lua" -Raw)
        },
        @{
            "Name" = "init"
            "ClassName" = "ModuleScript"
            "Source" = (Get-Content -Path "$PSScriptRoot\src\init.lua" -Raw)
        },
        @{
            "Name" = "Theme"
            "ClassName" = "ModuleScript"
            "Source" = (Get-Content -Path "$PSScriptRoot\src\Theme.lua" -Raw)
        },
        @{
            "Name" = "VideoTo3D"
            "ClassName" = "ModuleScript"
            "Source" = (Get-Content -Path "$PSScriptRoot\src\VideoTo3D.lua" -Raw)
        },
        @{
            "Name" = "Components"
            "ClassName" = "Folder"
            "Children" = (Get-ChildItem -Path "$PSScriptRoot\src\Components\*.lua" | ForEach-Object {
                @{
                    "Name" = $_.BaseName
                    "ClassName" = "ModuleScript"
                    "Source" = (Get-Content -Path $_.FullName -Raw)
                }
            })
        },
        @{
            "Name" = "Services"
            "ClassName" = "Folder"
            "Children" = (Get-ChildItem -Path "$PSScriptRoot\src\Services\*.lua" | ForEach-Object {
                @{
                    "Name" = $_.BaseName
                    "ClassName" = "ModuleScript"
                    "Source" = (Get-Content -Path $_.FullName -Raw)
                }
            })
        },
        @{
            "Name" = "Utils"
            "ClassName" = "Folder"
            "Children" = (Get-ChildItem -Path "$PSScriptRoot\src\Utils\*.lua" | ForEach-Object {
                @{
                    "Name" = $_.BaseName
                    "ClassName" = "ModuleScript"
                    "Source" = (Get-Content -Path $_.FullName -Raw)
                }
            })
        },
        @{
            "Name" = "MainPlugin"
            "ClassName" = "Script"
            "Source" = $pluginScript
        }
    )
}

# Convert the plugin structure to JSON
$pluginJson = $pluginInstance | ConvertTo-Json -Depth 10

# Save the plugin file
$pluginJson | Out-File -FilePath "$tempDir\plugin.json" -Encoding UTF8

# Use Roblox CLI to build the .rbxm file
$pluginFile = Join-Path -Path $PSScriptRoot -ChildPath "VideoTo3D.rbxm"

# If Roblox CLI is not available, just zip the files
if ($null -eq (Get-Command "rbxmk" -ErrorAction SilentlyContinue)) {
    # Fallback: Create a zip file
    $zipFile = "$buildDir\VideoTo3D.zip"
    Compress-Archive -Path "$tempDir\*" -DestinationPath $zipFile -Force
    Write-Host "Roblox CLI not found. Created ZIP file: $zipFile"
    Write-Host "To create a .rbxm file, install Roblox CLI (rbxmk) and run this script again."
} else {
    # Use rbxmk to build the .rbxm file
    $rbxmkOutput = & rbxmk build --output "$pluginFile" "$tempDir"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully built plugin: $pluginFile"
    } else {
        Write-Error "Failed to build plugin with rbxmk. Error: $rbxmkOutput"
    }
}

# Clean up
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Build process completed!"
