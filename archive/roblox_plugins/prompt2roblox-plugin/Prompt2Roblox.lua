-- Prompt2Roblox Plugin for Roblox Studio
-- This plugin helps create 3D models from video references

local Plugin = script.Parent
local Toolbar = plugin:CreateToolbar("Prompt2Roblox")
local Widget = require(script.Parent.Widget)

-- Configuration
local CONFIG = {
    PLUGIN_NAME = "Video to 3D",
    VERSION = "1.0.0",
    SETTINGS_KEY = "VideoTo3D_Settings"
}

-- Plugin state
local pluginState = {
    usageCount = 0,
    settings = {}
}

-- Load saved settings
local function loadSettings()
    local success, result = pcall(function()
        return plugin:GetSetting(CONFIG.SETTINGS_KEY) or {}
    end)
    
    if success then
        pluginState.settings = result
        pluginState.usageCount = result.usageCount or 0
        pluginState.isPro = result.isPro or false
    else
        warn("Failed to load settings:", tostring(result))
    end
end

-- Save settings
local function saveSettings()
    pluginState.settings.usageCount = pluginState.usageCount
    pluginState.settings.isPro = pluginState.isPro
    
    local success, err = pcall(function()
        plugin:SetSetting(CONFIG.SETTINGS_KEY, pluginState.settings)
    end)
    
    if not success then
        warn("Failed to save settings:", tostring(err))
    end
end

-- Check if user has access (free trial or pro)
local function checkAccess()
    if pluginState.isPro then return true end
    return pluginState.usageCount < CONFIG.TRIAL_LIMIT
end

-- Prompt for purchase
local function promptPurchase()
    local message = string.format(
        "You've used all %d free conversions.\n\n" ..
        "Upgrade to Pro for unlimited conversions!",
        CONFIG.TRIAL_LIMIT
    )
    
    local result = plugin:PromptPurchase(
        MarketplaceService,
        CONFIG.PRODUCT_ID,
        message
    )
    
    return result == Enum.ProductPurchaseDecision.Purchased
end

-- Create the plugin button
local button = Toolbar:CreateButton(
    CONFIG.PLUGIN_NAME,
    "Convert YouTube videos to Roblox assets",
    "rbxassetid://4458901886"  -- Default plugin icon, replace with your own
)

-- Function to show notifications
local function showNotification(title, message, duration)
    duration = duration or 5
    pcall(function()
        game:GetService("StarterGui"):SetCore("SendNotification", {
            Title = title,
            Text = tostring(message),
            Duration = duration
        })
    end)
end

-- Show error message
local function showError(message)
    showNotification(CONFIG.PLUGIN_NAME .. " Error", message, 5)
end

-- Show success message
local function showSuccess(message)
    showNotification(CONFIG.PLUGIN_NAME, message, 3)
end

-- Function to make API requests
local function makeRequest(method, endpoint, data)
    local url = CONFIG.API_URL .. endpoint
    
    -- Check if the URL is valid
    if not url:match("^https?://") then
        return nil, "Invalid API URL"
    end
    
    -- Show loading indicator
    local loading = showNotification("Processing", "Please wait...", 60)
    
    -- Make the request in a separate thread to avoid freezing the UI
    local result, errorMessage
    local thread = coroutine.create(function()
        local success, response = pcall(function()
            return HttpService:RequestAsync({
                Url = url,
                Method = method,
                Headers = {
                    ["Content-Type"] = "application/json",
                    ["X-Plugin-Version"] = CONFIG.VERSION
                },
                Body = data and HttpService:JSONEncode(data) or nil
            })
        end)
        
        -- Cancel loading indicator
        if loading and loading.Destroy then
            pcall(loading.Destroy, loading)
        end
        
        if not success then
            return nil, "Connection error: " .. tostring(response)
        end
        
        if response.Success then
            local success, decoded = pcall(HttpService.JSONDecode, HttpService, response.Body)
            if success then
                return decoded
            else
                return nil, "Failed to parse response: " .. tostring(decoded)
            end
        else
            return nil, string.format("API error (%d): %s", 
                response.StatusCode, 
                tostring(response.Body)
            )
        end
    end)
    
    -- Run the coroutine
    local success, response, err = coroutine.resume(thread)
    
    if not success then
        return nil, "Request failed: " .. tostring(response)
    end
    
    return response, err
end

-- Function to process a YouTube URL
local function processYouTube(url, prompt)
    -- Check access first
    if not checkAccess() then
        if not promptPurchase() then
            showError("Purchase required to continue")
            return nil
        end
        pluginState.isPro = true
        saveSettings()
    end
    
    -- Validate URL
    if not url or url == "" then
        showError("Please enter a valid YouTube URL")
        return nil
    end
    
    -- Prepare request data
    local data = {
        youtube_url = url,
        text = prompt or "",
        timestamp = os.time(),
        version = CONFIG.VERSION
    }
    
    -- Show processing message
    showNotification("Processing", "Sending request to server...", 5)
    
    -- Make the request
    local result, errorMessage = makeRequest("POST", "/process", data)
    
    if not result then
        showError(errorMessage or "Failed to process video")
        return nil
    end
    
    -- Update usage count
    if not pluginState.isPro then
        pluginState.usageCount = (pluginState.usageCount or 0) + 1
        saveSettings()
        
        -- Show trial count
        local remaining = math.max(0, CONFIG.TRIAL_LIMIT - pluginState.usageCount)
        if remaining > 0 then
            showNotification("Trial", string.format("%d free conversions remaining", remaining), 3)
        end
    end
    
    return result
end

-- Function to handle the main plugin action
local function onButtonClicked()
    -- Initialize if needed
    if pluginState.usageCount == nil then
        loadSettings()
    end
                
                return true
            end
            return false
        end
    })
    
    widget:Show()
end

-- Check for plugin updates
local function checkForUpdates()
    -- TODO: Implement update checking logic
    -- This would typically make a request to a version endpoint
    return nil
end

-- Connect the button click event
button.Click:Connect(onButtonClicked)

-- Handle plugin uninstallation
plugin.Unloading:Connect(function()
    -- Clean up any resources
    saveSettings()
end)

-- Initialize
loadSettings()
print(CONFIG.PLUGIN_NAME .. " v" .. CONFIG.VERSION .. " loaded successfully!")
print("Usage:", pluginState.usageCount, "/", CONFIG.TRIAL_LIMIT, "(Trial)")
print("Pro:", pluginState.isPro and "Yes" or "No")

-- Export public API
local PublicAPI = {
    -- Version information
    VERSION = CONFIG.VERSION,
    
    -- Core functions
    processYouTube = processYouTube,
    makeRequest = makeRequest,
    
    -- Plugin information
    getUsageInfo = function()
        return {
            usageCount = pluginState.usageCount,
            trialLimit = CONFIG.TRIAL_LIMIT,
            isPro = pluginState.isPro,
            version = CONFIG.VERSION
        }
    end,
    
    -- For testing
    _TEST = {
        resetTrial = function()
            pluginState.usageCount = 0
            pluginState.isPro = false
            saveSettings()
            return "Trial reset successfully"
        end
    }
}

return PublicAPI
