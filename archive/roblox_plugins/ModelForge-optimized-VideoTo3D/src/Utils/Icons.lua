-- Icons: Centralized icon management for the plugin

local Icons = {}
Icons._VERSION = "1.0.0"
Icons._DESCRIPTION = "Centralized icon management for the VideoTo3D plugin"
Icons._LICENSE = [[
    MIT License
    Copyright (c) 2023 Your Name
]]

-- Base URL for Roblox icon assets
local ICON_BASE_URL = "rbxassetid://"

-- Default icon set (using Roblox built-in icons)
local DEFAULT_ICONS = {
    -- File operations
    ["file"] = 6031075926,
    ["folder"] = 6031075187,
    ["folder-open"] = 6031112432,
    ["upload"] = 6031091004,
    ["download"] = 6031091003,
    ["save"] = 6031091002,
    ["trash"] = 6031091005,
    ["copy"] = 6031091006,
    ["cut"] = 6031091007,
    ["paste"] = 6031091008,
    
    -- Navigation
    ["arrow-left"] = 6031068439,
    ["arrow-right"] = 6031068440,
    ["arrow-up"] = 6031068441,
    ["arrow-down"] = 6031068442,
    ["chevron-left"] = 6031068435,
    ["chevron-right"] = 6031068436,
    ["chevron-up"] = 6031068437,
    ["chevron-down"] = 6031068438,
    ["home"] = 6031068434,
    ["refresh"] = 6031068433,
    
    -- Media controls
    ["play"] = 6031068421,
    ["pause"] = 6031068422,
    ["stop"] = 6031068423,
    ["skip-back"] = 6031068418,
    ["skip-forward"] = 6031068419,
    ["volume"] = 6031068424,
    ["volume-off"] = 6031068425,
    ["volume-up"] = 6031068426,
    ["volume-down"] = 6031068427,
    ["fullscreen"] = 6031068428,
    ["fullscreen-exit"] = 6031068429,
    
    -- Common UI
    ["check"] = 6031068410,
    ["x"] = 6031068409,
    ["plus"] = 6031068407,
    ["minus"] = 6031068408,
    ["close"] = 6031068409,
    ["menu"] = 6031068411,
    ["settings"] = 6031068412,
    ["help"] = 6031068413,
    ["info"] = 6031068414,
    ["alert"] = 6031068415,
    ["warning"] = 6031068416,
    ["error"] = 6031068417,
    ["spinner"] = 6031068420,
    
    -- Social
    ["heart"] = 6031068401,
    ["star"] = 6031068402,
    ["star-filled"] = 6031068403,
    ["thumbs-up"] = 6031068404,
    ["thumbs-down"] = 6031068405,
    ["share"] = 6031068406,
    
    -- Editor
    ["bold"] = 6031068391,
    ["italic"] = 6031068392,
    ["underline"] = 6031068393,
    ["strikethrough"] = 6031068394,
    ["link"] = 6031068395,
    ["image"] = 6031068396,
    ["video"] = 6031068397,
    ["code"] = 6031068398,
    ["list"] = 6031068399,
    ["list-ordered"] = 6031068400,
    
    -- Custom icons
    ["check-circle"] = 6031068381,
    ["x-circle"] = 6031068382,
    ["alert-triangle"] = 6031068383,
    ["info"] = 6031068384,
    ["help-circle"] = 6031068385,
    ["external-link"] = 6031068386,
    ["download-cloud"] = 6031068387,
    ["upload-cloud"] = 6031068388,
    ["more-horizontal"] = 6031068389,
    ["more-vertical"] = 6031068390,
    
    -- 3D specific
    ["cube"] = 6031068371,
    ["grid"] = 6031068372,
    ["move"] = 6031068373,
    ["rotate"] = 6031068374,
    ["scale"] = 6031068375,
    ["camera"] = 6031068376,
    ["light"] = 6031068377,
    ["material"] = 6031068378,
    ["texture"] = 6031068379,
    ["vertex"] = 6031068380,
    
    -- Video processing
    ["film"] = 6031068361,
    ["video-off"] = 6031068362,
    ["camera-off"] = 6031068363,
    ["aperture"] = 6031068364,
    ["crop"] = 6031068365,
    ["filter"] = 6031068366,
    ["layers"] = 6031068367,
    ["sliders"] = 6031068368,
    ["toggle-left"] = 6031068369,
    ["toggle-right"] = 6031068370,
    
    -- Status
    ["clock"] = 6031068351,
    ["calendar"] = 6031068352,
    ["bell"] = 6031068353,
    ["bell-off"] = 6031068354,
    ["eye"] = 6031068355,
    ["eye-off"] = 6031068356,
    ["lock"] = 6031068357,
    ["unlock"] = 6031068358,
    ["user"] = 6031068359,
    ["users"] = 6031068360,
    
    -- Arrows
    ["arrow-up-circle"] = 6031068341,
    ["arrow-right-circle"] = 6031068342,
    ["arrow-down-circle"] = 6031068343,
    ["arrow-left-circle"] = 6031068344,
    ["chevron-up-circle"] = 6031068345,
    ["chevron-right-circle"] = 6031068346,
    ["chevron-down-circle"] = 6031068347,
    ["chevron-left-circle"] = 6031068348,
    ["corner-up-left"] = 6031068349,
    ["corner-up-right"] = 6031068350,
    
    -- File types
    ["file-text"] = 6031068331,
    ["file-code"] = 6031068332,
    ["file-image"] = 6031068333,
    ["file-video"] = 6031068334,
    ["file-audio"] = 6031068335,
    ["file-archive"] = 6031068336,
    ["file-pdf"] = 6031068337,
    ["file-word"] = 6031068338,
    ["file-excel"] = 6031068339,
    ["file-powerpoint"] = 6031068340,
    
    -- Custom VideoTo3D icons
    ["videotothree"] = 0, -- Replace with your custom icon ID
    ["model"] = 0, -- Replace with your custom icon ID
    ["rig"] = 0, -- Replace with your custom icon ID
    ["animation"] = 0, -- Replace with your custom icon ID
    ["export"] = 0, -- Replace with your custom icon ID
    ["import"] = 0, -- Replace with your custom icon ID
    ["preview"] = 0, -- Replace with your custom icon ID
    ["render"] = 0, -- Replace with your custom icon ID
    ["settings-advanced"] = 0, -- Replace with your custom icon ID
    ["template"] = 0, -- Replace with your custom icon ID
}

-- Custom icons can be added or overridden here
local CUSTOM_ICONS = {
    -- Example:
    -- ["my-custom-icon"] = 1234567890,
}

-- Cache for loaded images
local imageCache = {}

-- Get an icon by name
function Icons.getIcon(name, size)
    -- Check if the icon exists in the cache
    if imageCache[name] then
        return imageCache[name]
    end
    
    -- Check custom icons first, then default icons
    local iconId = CUSTOM_ICONS[name] or DEFAULT_ICONS[name]
    
    if not iconId then
        warn(string.format("Icon '%s' not found", name))
        return ""
    end
    
    if iconId == 0 then
        warn(string.format("Icon '%s' has an invalid ID of 0", name))
        return ""
    end
    
    -- Create the full asset URL
    local url = ICON_BASE_URL .. tostring(iconId)
    
    -- Cache the URL
    imageCache[name] = url
    
    return url
end

-- Get a circular version of an icon (useful for avatars, etc.)
function Icons.getCircularIcon(name, size)
    local icon = Icons.getIcon(name)
    if icon == "" then return "" end
    
    -- Create a circular mask for the icon
    -- In a real implementation, you would use an ImageButton with a UICorner
    -- or a custom image with a circular mask
    return icon
end

-- Preload icons to reduce loading times
function Icons.preloadIcons(iconNames)
    for _, name in ipairs(iconNames) do
        Icons.getIcon(name)
    end
end

-- Clear the icon cache
function Icons.clearCache()
    table.clear(imageCache)
end

-- Add custom icons at runtime
function Icons.addCustomIcons(icons)
    for name, id in pairs(icons) do
        CUSTOM_ICONS[name] = id
    end
    
    -- Clear cache to ensure new icons are used
    Icons.clearCache()
end

-- Remove custom icons
function Icons.removeCustomIcons(iconNames)
    for _, name in ipairs(iconNames) do
        CUSTOM_ICONS[name] = nil
    end
    
    -- Clear cache to ensure changes take effect
    Icons.clearCache()
end

-- Get all available icon names
function Icons.getAvailableIcons()
    local icons = {}
    
    -- Add default icons
    for name, _ in pairs(DEFAULT_ICONS) do
        table.insert(icons, name)
    end
    
    -- Add custom icons
    for name, _ in pairs(CUSTOM_ICONS) do
        if not DEFAULT_ICONS[name] then
            table.insert(icons, name)
        end
    end
    
    table.sort(icons)
    return icons
end

-- Check if an icon exists
function Icons.hasIcon(name)
    return DEFAULT_ICONS[name] ~= nil or CUSTOM_ICONS[name] ~= nil
end

-- Create an ImageLabel with an icon
function Icons.createIconLabel(name, size, color, transparency)
    local icon = Icons.getIcon(name)
    if icon == "" then return nil end
    
    size = size or UDim2.new(0, 24, 0, 24)
    color = color or Color3.new(1, 1, 1)
    transparency = transparency or 0
    
    return {
        Size = size,
        BackgroundTransparency = 1,
        Image = icon,
        ImageColor3 = color,
        ImageTransparency = transparency,
        ScaleType = Enum.ScaleType.Fit
    }
end

-- Create an ImageButton with an icon
function Icons.createIconButton(name, size, color, hoverColor, pressedColor, disabledColor)
    local icon = Icons.getIcon(name)
    if icon == "" then return nil end
    
    size = size or UDim2.new(0, 32, 0, 32)
    color = color or Color3.new(1, 1, 1)
    hoverColor = hoverColor or Color3.fromRGB(200, 200, 200)
    pressedColor = pressedColor or Color3.fromRGB(180, 180, 180)
    disabledColor = disabledColor or Color3.fromRGB(100, 100, 100)
    
    return {
        Size = size,
        BackgroundTransparency = 1,
        AutoButtonColor = false,
        Image = icon,
        ImageColor3 = color,
        ScaleType = Enum.ScaleType.Fit,
        
        [Roact.Event.MouseEnter] = function(rbx)
            if not rbx.SelectionImageObject then
                rbx.ImageColor3 = hoverColor
            end
        end,
        
        [Roact.Event.MouseLeave] = function(rbx)
            if not rbx.SelectionImageObject then
                rbx.ImageColor3 = color
            end
        end,
        
        [Roact.Event.MouseButton1Down] = function(rbx)
            if not rbx.SelectionImageObject then
                rbx.ImageColor3 = pressedColor
            end
        end,
        
        [Roact.Event.MouseButton1Up] = function(rbx)
            if not rbx.SelectionImageObject then
                rbx.ImageColor3 = hoverColor
            end
        end,
        
        [Roact.Event.SelectionGained] = function(rbx)
            rbx.ImageColor3 = hoverColor
        end,
        
        [Roact.Event.SelectionLost] = function(rbx)
            rbx.ImageColor3 = color
        end
    }
end

return Icons
