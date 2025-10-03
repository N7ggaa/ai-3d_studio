# Simple build script for VideoTo3D plugin
# Creates a ZIP file that can be imported into Roblox Studio

$buildDir = "$PSScriptRoot\build"
$outputZip = "$buildDir\VideoTo3D.rbxm.zip"

# Create build directory if it doesn't exist
if (-not (Test-Path -Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
}

# Create a temporary directory for the plugin
$tempDir = "$env:TEMP\VideoTo3D_Build_$(Get-Date -Format 'yyyyMMdd_HHmmss')
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Copy all source files to the temp directory
$sourceDirs = @(
    "src\Components",
    "src\Services",
    "src\Utils"
)

# Copy files
foreach ($dir in $sourceDirs) {
    $sourcePath = Join-Path -Path $PSScriptRoot -ChildPath $dir
    $destPath = Join-Path -Path $tempDir -ChildPath $dir
    
    if (-not (Test-Path -Path $destPath)) {
        New-Item -ItemType Directory -Path $destPath -Force | Out-Null
    }
    
    Get-ChildItem -Path $sourcePath -Filter "*.lua" | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $destPath -Force
    }
}

# Copy root files
$rootFiles = @(
    "src\init.lua",
    "src\Main.lua",
    "src\Theme.lua",
    "src\VideoTo3D.lua"
)

foreach ($file in $rootFiles) {
    $sourceFile = Join-Path -Path $PSScriptRoot -ChildPath $file
    if (Test-Path -Path $sourceFile) {
        Copy-Item -Path $sourceFile -Destination $tempDir -Force
    }
}

# Create the plugin script
$pluginScript = @"
local Plugin = script.Parent
local Main = require(script.Parent.Main)

local function init()
    local success, result = pcall(function()
        local main = Main.new(Plugin)
        
        -- Create toolbar
        local toolbar = plugin:CreateToolbar("VideoTo3D")
        local button = toolbar:CreateButton("VideoTo3D", "Convert video to 3D model", "rbxassetid://6031075926")
        
        local function toggle()
            if main.isEnabled then
                main:Disable()
                button:SetActive(false)
            else
                main:Enable()
                button:SetActive(true)
            end
        end
        
        button.Click:Connect(toggle)
        
        -- Clean up when plugin is unloaded
        plugin.Unloading:Connect(function()
            if main.isEnabled then
                main:Disable()
            end
        end)
        
        return main
    end)
    
    if not success then
        warn("Failed to initialize VideoTo3D plugin:", result)
        error(result)
    end
end

return init()
"@

# Save the plugin script
$pluginScript | Out-File -FilePath "$tempDir\MainPlugin.lua" -Encoding UTF8

# Create a ZIP file
$zipFile = "$buildDir\VideoTo3D.rbxm.zip"
if (Test-Path -Path $zipFile) {
    Remove-Item -Path $zipFile -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $zipFile)

# Clean up
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Build completed!"
Write-Host "Plugin ZIP file created at: $zipFile"
Write-Host "To install in Roblox Studio:"
Write-Host "1. Rename the .zip to .rbxm"
Write-Host "2. In Roblox Studio, go to 'File' > 'Import' and select the .rbxm file"
Write-Host "3. The plugin will appear in the 'Plugins' tab"
