@echo off
REM Simple batch file to package the VideoTo3D plugin

setlocal

set "BUILD_DIR=build"
set "TEMP_DIR=%TEMP%\VideoTo3D_Build_%RANDOM%"
set "OUTPUT_ZIP=%BUILD_DIR%\VideoTo3D.zip"

REM Create build directory if it doesn't exist
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

REM Create temporary directory structure
mkdir "%TEMP_DIR%"
mkdir "%TEMP_DIR%\src"
mkdir "%TEMP_DIR%\src\Components"
mkdir "%TEMP_DIR%\src\Services"
mkdir "%TEMP_DIR%\src\Utils"
mkdir "%TEMP_DIR%\src\Vendor"

REM Copy source files
xcopy /Y "src\*.lua" "%TEMP_DIR%\src\"
xcopy /Y "src\Components\*.lua" "%TEMP_DIR%\src\Components\"
xcopy /Y "src\Services\*.lua" "%TEMP_DIR%\src\Services\"
xcopy /Y "src\Utils\*.lua" "%TEMP_DIR%\src\Utils\"
xcopy /Y "src\Vendor\*.lua" "%TEMP_DIR%\src\Vendor\"

REM Create the plugin script
echo local Plugin = script.Parent > "%TEMP_DIR%\MainPlugin.lua"
echo local Main = require(script.Parent.Main) >> "%TEMP_DIR%\MainPlugin.lua"
echo. >> "%TEMP_DIR%\MainPlugin.lua"
echo local function init() >> "%TEMP_DIR%\MainPlugin.lua"
echo     local success, result = pcall(function() >> "%TEMP_DIR%\MainPlugin.lua"
echo         local main = Main.new(Plugin) >> "%TEMP_DIR%\MainPlugin.lua"
echo. >> "%TEMP_DIR%\MainPlugin.lua"
echo         -- Create toolbar >> "%TEMP_DIR%\MainPlugin.lua"
echo         local toolbar = plugin:CreateToolbar("VideoTo3D") >> "%TEMP_DIR%\MainPlugin.lua"
echo         local button = toolbar:CreateButton("VideoTo3D", "Convert video to 3D model", "rbxassetid://6031075926") >> "%TEMP_DIR%\MainPlugin.lua"
echo. >> "%TEMP_DIR%\MainPlugin.lua"
echo         local function toggle() >> "%TEMP_DIR%\MainPlugin.lua"
echo             if main.isEnabled then >> "%TEMP_DIR%\MainPlugin.lua"
echo                 main:Disable() >> "%TEMP_DIR%\MainPlugin.lua"
echo                 button:SetActive(false) >> "%TEMP_DIR%\MainPlugin.lua"
echo             else >> "%TEMP_DIR%\MainPlugin.lua"
echo                 main:Enable() >> "%TEMP_DIR%\MainPlugin.lua"
echo                 button:SetActive(true) >> "%TEMP_DIR%\MainPlugin.lua"
echo             end >> "%TEMP_DIR%\MainPlugin.lua"
echo         end >> "%TEMP_DIR%\MainPlugin.lua"
echo. >> "%TEMP_DIR%\MainPlugin.lua"
echo         button.Click:Connect(toggle) >> "%TEMP_DIR%\MainPlugin.lua"
echo. >> "%TEMP_DIR%\MainPlugin.lua"
echo         -- Clean up when plugin is unloaded >> "%TEMP_DIR%\MainPlugin.lua"
echo         plugin.Unloading:Connect(function() >> "%TEMP_DIR%\MainPlugin.lua"
echo             if main.isEnabled then >> "%TEMP_DIR%\MainPlugin.lua"
echo                 main:Disable() >> "%TEMP_DIR%\MainPlugin.lua"
echo             end >> "%TEMP_DIR%\MainPlugin.lua"
echo         end) >> "%TEMP_DIR%\MainPlugin.lua"
echo. >> "%TEMP_DIR%\MainPlugin.lua"
echo         return main >> "%TEMP_DIR%\MainPlugin.lua"
echo     end) >> "%TEMP_DIR%\MainPlugin.lua"
echo. >> "%TEMP_DIR%\MainPlugin.lua"
echo     if not success then >> "%TEMP_DIR%\MainPlugin.lua"
echo         warn("Failed to initialize VideoTo3D plugin:", result) >> "%TEMP_DIR%\MainPlugin.lua"
echo         error(result) >> "%TEMP_DIR%\MainPlugin.lua"
echo     end >> "%TEMP_DIR%\MainPlugin.lua"
echo end >> "%TEMP_DIR%\MainPlugin.lua"
echo. >> "%TEMP_DIR%\MainPlugin.lua"
echo return init() >> "%TEMP_DIR%\MainPlugin.lua"

REM Create a ZIP file
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%OUTPUT_ZIP%' -Force"

REM Clean up
rmdir /S /Q "%TEMP_DIR%"

echo.
echo Build completed!
echo Plugin file created at: %OUTPUT_ZIP%
echo.
echo To install in Roblox Studio:
echo 1. Rename the .rbxm file to .zip
echo 2. Extract the contents to a folder
echo 3. In Roblox Studio, go to 'File' > 'Import' and select the extracted folder
echo 4. The plugin will appear in the 'Plugins' tab
echo.

pause
