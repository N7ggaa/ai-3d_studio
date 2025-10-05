-- init.lua
-- Main entry point for the Roblox Studio plugin

local Plugin = script.Parent.Plugin
local Framework = require(Plugin.Packages.Framework)
local Roact = require(Plugin.Packages.Roact)

-- Initialize Framework services
local StudioUI = Framework.StudioUI
local StudioFrameworkStyles = Framework.StudioUI.StudioFramework.Style
local Theme = Framework.Style.Theme
local Localization = Framework.Util.Localization

-- Create plugin
local plugin = plugin or plugin
local pluginName = "AI3DModelGenerator"

-- Set up theme
local style = StudioFrameworkStyles.new(StudioUI.Themes.DarkTheme, StudioUI.ThemeSwitcher.ThemeNameChanged)
local theme = Theme.new(function()
    return style.currentTheme
end)

-- Set up localization
local localization = Localization.new()
local localizationPath = script.Parent:FindFirstChild("Localization")
if localizationPath then
    localization:addResource("en", localizationPath)
end

-- Create the main plugin component
local function init()
    local MainPlugin = require(script.Parent.src.MainPlugin)
    
    -- Create the plugin handle
    local handle
    
    -- Function to clean up the plugin
    local function cleanup()
        if handle then
            Roact.unmount(handle)
            handle = nil
        end
    end
    
    -- Function to toggle the plugin
    local function toggle()
        if handle then
            cleanup()
        else
            -- Create the plugin UI
            handle = Roact.mount(Roact.createElement(MainPlugin, {
                Plugin = plugin,
                Theme = theme,
                Localization = localization,
                onClose = cleanup
            }))
        end
    end
    
    -- Create the toolbar button and connect it
    local toolbar = plugin:CreateToolbar("AI 3D Model Generator")
    local toggleButton = toolbar:CreateButton(
        "AI 3D Model Generator",
        "Generate 3D models using AI",
        "rbxassetid://4458901886" -- Default icon, replace with your own
    )
    
    -- Connect the button click event
    toggleButton.Click:Connect(toggle)
    
    -- Handle plugin uninstallation
    plugin.Unloading:Connect(function()
        cleanup()
        toggleButton:Destroy()
    end)
    
    -- Return the plugin object
    return {
        -- Public API methods can be added here
        _plugin = plugin,
        _name = pluginName,
        
        -- Method to manually show the plugin window
        show = function()
            if not handle then
                toggle()
            end
        end,
        
        -- Method to manually hide the plugin window
        hide = function()
            cleanup()
        end,
        
        -- Method to toggle the plugin window
        toggle = toggle,
        
        -- Method to clean up resources
        destroy = function()
            cleanup()
            toggleButton:Destroy()
        end
    }
end

-- Initialize the plugin
local success, result = pcall(init)

-- Handle any initialization errors
if not success then
    warn("Failed to initialize AI 3D Model Generator plugin:")
    warn(result)
    
    -- Show an error message in Studio
    local message = "The AI 3D Model Generator plugin encountered an error during initialization. " ..
                   "Please check the output window for more details."
    
    -- Create an error notification
    local notificationService = game:GetService("NotificationService")
    notificationService:SendCoreNotification(
        "AI3DModelGeneratorError",
        {
            Title = "Plugin Error",
            Text = message,
            Duration = 10,
            Icon = "rbxasset://textures/error.png"
        }
    )
    
    -- Log the full error for debugging
    warn(debug.traceback(result))
end

-- Return the plugin object if successful
return success and result or nil
