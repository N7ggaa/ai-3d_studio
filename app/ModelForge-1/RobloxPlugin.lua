--[[
    ModelForge Roblox Studio Plugin
    Premium 3D Model Generator - 500 Robux
    Connects to local bridge at http://127.0.0.1:8765
    
    Installation:
    1. Save this file as ModelForgePlugin.lua
    2. In Roblox Studio: Plugins > Plugins Folder
    3. Create a new folder called "ModelForge"
    4. Save this script inside as "Main.lua"
    5. Restart Studio
    
    Monetization: 500 Robux for full access
    Friend Referral: Get 100 Robux credit per friend
]]

local HttpService = game:GetService("HttpService")
local InsertService = game:GetService("InsertService")
local Selection = game:GetService("Selection")
local StudioService = game:GetService("StudioService")

-- Configuration
local BASE_URL = "http://127.0.0.1:8765"
local PLUGIN_NAME = "ModelForge Pro"
local PLUGIN_ID = "ModelForge_Gallery"
local PLUGIN_PRICE = 500 -- Robux
local REFERRAL_BONUS = 100 -- Robux per friend
local PRODUCT_ID = "1234567890" -- Replace with actual Roblox product ID
local MODEL_NAME = "ModelForge_Generated" -- Name for uploaded models

-- License Management
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

-- License check
local function checkLicense()
    local settings = plugin:GetSetting("ModelForgeLicense") or {}
    
    -- Check if user has purchased or has trial
    if settings.isPurchased then
        return true, "full"
    elseif settings.trialUsesLeft and settings.trialUsesLeft > 0 then
        return true, "trial"
    elseif settings.referralCredits and settings.referralCredits >= PLUGIN_PRICE then
        -- Auto-unlock with referral credits
        settings.isPurchased = true
        settings.referralCredits = settings.referralCredits - PLUGIN_PRICE
        plugin:SetSetting("ModelForgeLicense", settings)
        return true, "full"
    else
        return false, "none"
    end
end

-- Initialize trial
local function initializeTrial()
    local settings = plugin:GetSetting("ModelForgeLicense") or {}
    if not settings.initialized then
        settings.initialized = true
        settings.trialUsesLeft = 3 -- 3 free uses
        settings.referralCredits = 0
        settings.referralCode = tostring(math.random(100000, 999999))
        settings.referredFriends = {}
        plugin:SetSetting("ModelForgeLicense", settings)
    end
    return settings
end

-- Process referral
local function processReferral(friendCode)
    local settings = plugin:GetSetting("ModelForgeLicense") or {}
    
    if friendCode and friendCode ~= settings.referralCode then
        -- Check if already referred this friend
        if not settings.referredFriends[friendCode] then
            settings.referredFriends[friendCode] = true
            settings.referralCredits = (settings.referralCredits or 0) + REFERRAL_BONUS
            plugin:SetSetting("ModelForgeLicense", settings)
            return true, settings.referralCredits
        end
    end
    return false, settings.referralCredits or 0
end

-- Create plugin
local toolbar = plugin:CreateToolbar(PLUGIN_NAME)
local button = toolbar:CreateButton(
    "ModelForge Pro",
    "Premium 3D Model Generator (500 Robux)",
    "rbxasset://textures/ui/GuiImagePlaceholder.png"
)

-- Create dock widget
local widgetInfo = DockWidgetPluginGuiInfo.new(
    Enum.InitialDockState.Float,
    false,  -- Initially enabled
    false,  -- Override previous enabled state
    400,    -- Default width
    600,    -- Default height
    300,    -- Minimum width
    200     -- Minimum height
)

local widget = plugin:CreateDockWidgetPluginGui(PLUGIN_ID, widgetInfo)
widget.Title = "ModelForge Gallery"

-- UI Creation
local function createUI()
    -- Main frame
    local mainFrame = Instance.new("Frame")
    mainFrame.Size = UDim2.new(1, 0, 1, 0)
    mainFrame.BackgroundColor3 = Color3.fromRGB(46, 46, 46)
    mainFrame.Parent = widget
    
    -- Header
    local header = Instance.new("Frame")
    header.Size = UDim2.new(1, 0, 0, 50)
    header.BackgroundColor3 = Color3.fromRGB(35, 35, 35)
    header.Parent = mainFrame
    
    local title = Instance.new("TextLabel")
    title.Size = UDim2.new(0.5, 0, 1, 0)
    title.Position = UDim2.new(0, 10, 0, 0)
    title.BackgroundTransparency = 1
    title.Text = "ModelForge Gallery"
    
    -- Status label
    local statusLabel = Instance.new("TextLabel")
    statusLabel.Size = UDim2.new(0.4, -10, 0.5, 0)
    statusLabel.Position = UDim2.new(0.6, 0, 0.25, 0)
    statusLabel.BackgroundTransparency = 1
    statusLabel.Text = "Connecting..."
    statusLabel.TextColor3 = Color3.fromRGB(255, 255, 0)
    statusLabel.TextScaled = true
    statusLabel.Font = Enum.Font.SourceSans
    statusLabel.Parent = header
    
    -- Controls frame
    local controls = Instance.new("Frame")
    controls.Size = UDim2.new(1, 0, 0, 40)
    controls.Position = UDim2.new(0, 0, 0, 50)
    controls.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
    controls.Parent = mainFrame
    
    -- Refresh button
    local refreshBtn = Instance.new("TextButton")
    refreshBtn.Size = UDim2.new(0, 100, 0, 30)
    refreshBtn.Position = UDim2.new(0, 5, 0, 5)
    refreshBtn.BackgroundColor3 = Color3.fromRGB(0, 162, 255)
    refreshBtn.Text = "Refresh"
    refreshBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
    refreshBtn.Font = Enum.Font.SourceSansBold
    refreshBtn.Parent = controls
    
    -- Filter input
    local filterBox = Instance.new("TextBox")
    filterBox.Size = UDim2.new(0, 150, 0, 30)
    filterBox.Position = UDim2.new(0, 110, 0, 5)
    filterBox.BackgroundColor3 = Color3.fromRGB(60, 60, 60)
    filterBox.Text = ""
    filterBox.PlaceholderText = "Filter by name..."
    filterBox.TextColor3 = Color3.fromRGB(255, 255, 255)
    filterBox.Font = Enum.Font.SourceSans
    filterBox.Parent = controls
    
    -- Limit selector
    local limitBox = Instance.new("TextBox")
    limitBox.Size = UDim2.new(0, 60, 0, 30)
    limitBox.Position = UDim2.new(0, 265, 0, 5)
    limitBox.BackgroundColor3 = Color3.fromRGB(60, 60, 60)
    limitBox.Text = "50"
    limitBox.PlaceholderText = "Limit"
    limitBox.TextColor3 = Color3.fromRGB(255, 255, 255)
    limitBox.Font = Enum.Font.SourceSans
    limitBox.Parent = controls
    
    -- Scroll frame for variants
    local scrollFrame = Instance.new("ScrollingFrame")
    scrollFrame.Size = UDim2.new(1, -10, 1, -100)
    scrollFrame.Position = UDim2.new(0, 5, 0, 95)
    scrollFrame.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
    scrollFrame.BorderSizePixel = 0
    scrollFrame.ScrollBarThickness = 8
    scrollFrame.Parent = mainFrame
    
    -- List layout
    local listLayout = Instance.new("UIListLayout")
    listLayout.Padding = UDim.new(0, 5)
    listLayout.SortOrder = Enum.SortOrder.LayoutOrder
    listLayout.Parent = scrollFrame
    
    return {
        mainFrame = mainFrame,
        statusLabel = statusLabel,
        refreshBtn = refreshBtn,
        filterBox = filterBox,
        limitBox = limitBox,
        scrollFrame = scrollFrame
    }
end

-- HTTP request wrapper
local function httpRequest(url, method)
    method = method or "GET"
    local success, result = pcall(function()
        return HttpService:RequestAsync({
            Url = url,
            Method = method,
            Headers = {
                ["Content-Type"] = "application/json"
            }
        })
    end)
    
    if not success then
        return nil, result
    end
    
    if result.StatusCode ~= 200 then
        return nil, "HTTP " .. result.StatusCode
    end
    
    local jsonSuccess, data = pcall(function()
        return HttpService:JSONDecode(result.Body)
    end)
    
    if not jsonSuccess then
        return nil, "JSON parse error"
    end
    
    return data, nil
end

-- Check bridge connection
local function checkConnection()
    local data, err = httpRequest(BASE_URL .. "/health")
    return data ~= nil and data.status == "ok"
end

-- Load variants
local function loadVariants(ui, filter, limit)
    ui.statusLabel.Text = "Loading..."
    ui.statusLabel.TextColor3 = Color3.fromRGB(255, 255, 0)
    
    -- Build query
    local query = "/variants?limit=" .. (limit or 50)
    if filter and filter ~= "" then
        query = query .. "&q=" .. HttpService:UrlEncode(filter)
    end
    
    local variants, err = httpRequest(BASE_URL .. query)
    
    if not variants then
        ui.statusLabel.Text = "Error: " .. (err or "Unknown")
        ui.statusLabel.TextColor3 = Color3.fromRGB(255, 0, 0)
        return
    end
    
    -- Clear existing items
    for _, child in pairs(ui.scrollFrame:GetChildren())
        if child:IsA("Frame") then
            child:Destroy()
        end
    end
    
    -- Create variant items
    for i, variant in ipairs(variants) do
        local item = Instance.new("Frame")
        item.Size = UDim2.new(1, -10, 0, 80)
        item.BackgroundColor3 = Color3.fromRGB(60, 60, 60)
        item.Parent = ui.scrollFrame
        
        -- Name label
        local nameLabel = Instance.new("TextLabel")
        nameLabel.Size = UDim2.new(0.4, -10, 0, 30)
        nameLabel.Position = UDim2.new(0, 10, 0, 5)
        nameLabel.BackgroundTransparency = 1
        nameLabel.Text = variant.name or "Unknown"
        nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
        nameLabel.TextXAlignment = Enum.TextXAlignment.Left
        nameLabel.Font = Enum.Font.SourceSansBold
        nameLabel.TextScaled = true
        nameLabel.Parent = item
        
        -- Score label
        local scoreLabel = Instance.new("TextLabel")
        scoreLabel.Size = UDim2.new(0.2, 0, 0, 20)
        scoreLabel.Position = UDim2.new(0, 10, 0, 35)
        scoreLabel.BackgroundTransparency = 1
        scoreLabel.Text = "Score: " .. string.format("%.2f", variant.score_total or 999)
        scoreLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
        scoreLabel.TextXAlignment = Enum.TextXAlignment.Left
        scoreLabel.Font = Enum.Font.SourceSans
        scoreLabel.TextScaled = true
        scoreLabel.Parent = item
        
        -- Info label
        local infoLabel = Instance.new("TextLabel")
        infoLabel.Size = UDim2.new(0.3, 0, 0, 20)
        infoLabel.Position = UDim2.new(0.2, 10, 0, 35)
        infoLabel.BackgroundTransparency = 1
        infoLabel.Text = "Faces: " .. tostring(variant.faces_total or "?")
        infoLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
        infoLabel.TextXAlignment = Enum.TextXAlignment.Left
        infoLabel.Font = Enum.Font.SourceSans
        infoLabel.TextScaled = true
        infoLabel.Parent = item
        
        -- Upload button
        local uploadBtn = Instance.new("TextButton")
        uploadBtn.Size = UDim2.new(0, 80, 0, 30)
        uploadBtn.Position = UDim2.new(0.6, 0, 0, 25)
        uploadBtn.BackgroundColor3 = Color3.fromRGB(0, 162, 255)
        uploadBtn.Text = "Upload"
        uploadBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
        uploadBtn.Font = Enum.Font.SourceSans
        uploadBtn.Parent = item
        
        -- Insert button (disabled until uploaded)
        local insertBtn = Instance.new("TextButton")
        insertBtn.Size = UDim2.new(0, 80, 0, 30)
        insertBtn.Position = UDim2.new(0.75, 0, 0, 25)
        insertBtn.BackgroundColor3 = Color3.fromRGB(100, 100, 100)
        insertBtn.Text = "Insert"
        insertBtn.TextColor3 = Color3.fromRGB(200, 200, 200)
        insertBtn.Font = Enum.Font.SourceSans
        insertBtn.Parent = item
        
        -- Upload click handler
        uploadBtn.MouseButton1Click:Connect(function()
            uploadBtn.Text = "Uploading..."
            uploadBtn.BackgroundColor3 = Color3.fromRGB(255, 162, 0)
            
            local uploadResult, uploadErr = httpRequest(
                BASE_URL .. "/upload/" .. variant.name .. "?poll_timeout=60",
                "POST"
            )
            
            if uploadResult and uploadResult.asset_id then
                uploadBtn.Text = "Uploaded!"
                uploadBtn.BackgroundColor3 = Color3.fromRGB(0, 200, 0)
                
                -- Enable insert button
                insertBtn.BackgroundColor3 = Color3.fromRGB(0, 162, 255)
                insertBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
                
                -- Insert click handler
                insertBtn.MouseButton1Click:Connect(function()
                    local assetId = tonumber(uploadResult.asset_id)
                    if assetId then
                        local model = game:GetObjects("rbxassetid://" .. assetId)[1]
                        model.Name = MODEL_NAME .. "_" .. variant.name
                        model.Parent = workspace
                        Selection:Set({model})
                        
                        -- Track usage for trial
                        local settings = plugin:GetSetting("ModelForgeLicense") or {}
                        if settings.trialUsesLeft and settings.trialUsesLeft > 0 and not settings.isPurchased then
                            settings.trialUsesLeft = settings.trialUsesLeft - 1
                            plugin:SetSetting("ModelForgeLicense", settings)
                        end
                        insertBtn.Text = "Inserted!"
                        insertBtn.BackgroundColor3 = Color3.fromRGB(0, 200, 0)
                    else
                        insertBtn.Text = "Failed"
                        insertBtn.BackgroundColor3 = Color3.fromRGB(255, 0, 0)
                    end
                end)
            else
                uploadBtn.Text = "Failed"
                uploadBtn.BackgroundColor3 = Color3.fromRGB(255, 0, 0)
                warn("Upload failed:", uploadErr or uploadResult)
            end
        end)
    end
    
    -- Update scroll canvas size
    ui.scrollFrame.CanvasSize = UDim2.new(0, 0, 0, #variants * 85)
    
    ui.statusLabel.Text = "Connected (" .. #variants .. " variants)"
    ui.statusLabel.TextColor3 = Color3.fromRGB(0, 255, 0)
end

-- Main setup
local ui = createUI()

-- Button click handler
button.Click:Connect(function()
    local hasLicense, licenseType = checkLicense()
    
    if not hasLicense then
        -- Show purchase dialog
        local purchaseWidget = plugin:CreateDockWidgetPluginGui(
            "ModelForge_Purchase",
            DockWidgetPluginGuiInfo.new(
                Enum.InitialDockState.Float,
                false, false,
                400, 300,
                400, 300
            )
        )
        purchaseWidget.Title = "ModelForge Pro - Purchase Required"
        
        local purchaseFrame = Instance.new("Frame")
        purchaseFrame.Size = UDim2.new(1, 0, 1, 0)
        purchaseFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
        purchaseFrame.Parent = purchaseWidget
        
        local title = Instance.new("TextLabel")
        title.Text = "ModelForge Pro - 500 Robux"
        title.Size = UDim2.new(1, -20, 0, 40)
        title.Position = UDim2.new(0, 10, 0, 10)
        title.Font = Enum.Font.SourceSansBold
        title.TextScaled = true
        title.TextColor3 = Color3.new(1, 1, 1)
        title.BackgroundTransparency = 1
        title.Parent = purchaseFrame
        
        local info = Instance.new("TextLabel")
        info.Text = "Trial Uses Left: " .. (licenseSettings.trialUsesLeft or 0) .. "\n\n" ..
                   "Referral Credits: " .. (licenseSettings.referralCredits or 0) .. " Robux\n" ..
                   "Your Referral Code: " .. (licenseSettings.referralCode or "N/A") .. "\n\n" ..
                   "Share your code with friends to earn 100 Robux per referral!"
        info.Size = UDim2.new(1, -20, 0, 100)
        info.Position = UDim2.new(0, 10, 0, 60)
        info.Font = Enum.Font.SourceSans
        info.TextScaled = true
        info.TextColor3 = Color3.new(0.9, 0.9, 0.9)
        info.BackgroundTransparency = 1
        info.Parent = purchaseFrame
        
        -- Referral input
        local referralLabel = Instance.new("TextLabel")
        referralLabel.Text = "Enter Friend's Code:"
        referralLabel.Size = UDim2.new(0.5, -10, 0, 30)
        referralLabel.Position = UDim2.new(0, 10, 0, 170)
        referralLabel.Font = Enum.Font.SourceSans
        referralLabel.TextScaled = true
        referralLabel.TextColor3 = Color3.new(1, 1, 1)
        referralLabel.BackgroundTransparency = 1
        referralLabel.Parent = purchaseFrame
        
        local referralInput = Instance.new("TextBox")
        referralInput.PlaceholderText = "Friend's code"
        referralInput.Size = UDim2.new(0.5, -10, 0, 30)
        referralInput.Position = UDim2.new(0.5, 0, 0, 170)
        referralInput.Font = Enum.Font.SourceSans
        referralInput.TextScaled = true
        referralInput.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
        referralInput.TextColor3 = Color3.new(1, 1, 1)
        referralInput.Parent = purchaseFrame
        
        -- Buttons
        local buttonContainer = Instance.new("Frame")
        buttonContainer.Size = UDim2.new(1, -20, 0, 40)
        buttonContainer.Position = UDim2.new(0, 10, 1, -50)
        buttonContainer.BackgroundTransparency = 1
        buttonContainer.Parent = purchaseFrame
        
        local purchaseBtn = Instance.new("TextButton")
        purchaseBtn.Text = "Purchase (500 Robux)"
        purchaseBtn.Size = UDim2.new(0.3, -5, 1, 0)
        purchaseBtn.Position = UDim2.new(0, 0, 0, 0)
        purchaseBtn.Font = Enum.Font.SourceSansBold
        purchaseBtn.TextScaled = true
        purchaseBtn.BackgroundColor3 = Color3.fromRGB(0, 162, 255)
        purchaseBtn.TextColor3 = Color3.new(1, 1, 1)
        purchaseBtn.Parent = buttonContainer
        
        local referralBtn = Instance.new("TextButton")
        referralBtn.Text = "Apply Code"
        referralBtn.Size = UDim2.new(0.3, -5, 1, 0)
        referralBtn.Position = UDim2.new(0.35, 0, 0, 0)
        referralBtn.Font = Enum.Font.SourceSansBold
        referralBtn.TextScaled = true
        referralBtn.BackgroundColor3 = Color3.fromRGB(76, 175, 80)
        referralBtn.TextColor3 = Color3.new(1, 1, 1)
        referralBtn.Parent = buttonContainer
        
        local trialBtn = Instance.new("TextButton")
        trialBtn.Text = "Use Trial (" .. (licenseSettings.trialUsesLeft or 0) .. " left)"
        trialBtn.Size = UDim2.new(0.3, -5, 1, 0)
        trialBtn.Position = UDim2.new(0.7, 0, 0, 0)
        trialBtn.Font = Enum.Font.SourceSansBold
        trialBtn.TextScaled = true
        trialBtn.BackgroundColor3 = Color3.fromRGB(255, 152, 0)
        trialBtn.TextColor3 = Color3.new(1, 1, 1)
        trialBtn.Parent = buttonContainer
        
        purchaseBtn.MouseButton1Click:Connect(function()
            -- Simulate purchase (in real plugin, use MarketplaceService)
            local settings = plugin:GetSetting("ModelForgeLicense") or {}
            settings.isPurchased = true
            plugin:SetSetting("ModelForgeLicense", settings)
            purchaseWidget.Enabled = false
            widgetInfo.Enabled = true
            createUI()
        end)
        
        referralBtn.MouseButton1Click:Connect(function()
            local success, credits = processReferral(referralInput.Text)
            if success then
                info.Text = "Referral applied! +100 Robux\nTotal Credits: " .. credits .. " Robux"
            else
                info.Text = "Invalid or already used code\nCredits: " .. credits .. " Robux"
            end
        end)
        
        trialBtn.MouseButton1Click:Connect(function()
            if licenseSettings.trialUsesLeft and licenseSettings.trialUsesLeft > 0 then
                licenseSettings.trialUsesLeft = licenseSettings.trialUsesLeft - 1
                plugin:SetSetting("ModelForgeLicense", licenseSettings)
                purchaseWidget.Enabled = false
                widgetInfo.Enabled = true
                createUI()
            end
        end)
        
        purchaseWidget.Enabled = true
    else
        -- Has license, open main UI
        if widgetInfo.Enabled then
            widgetInfo.Enabled = false
        else
            widgetInfo.Enabled = true
            createUI()
        end
    end
end)

-- Refresh handler
ui.refreshBtn.MouseButton1Click:Connect(function()
    local filter = ui.filterBox.Text
    local limit = tonumber(ui.limitBox.Text) or 50
    loadVariants(ui, filter, limit)
end)

-- Filter change handler
ui.filterBox.FocusLost:Connect(function(enterPressed)
    if enterPressed then
        local filter = ui.filterBox.Text
        local limit = tonumber(ui.limitBox.Text) or 50
        loadVariants(ui, filter, limit)
    end
end)

-- Initial connection check
if checkConnection() then
    loadVariants(ui, "", 50)
else
    ui.statusLabel.Text = "Bridge offline"
    ui.statusLabel.TextColor3 = Color3.fromRGB(255, 0, 0)
end

print("ModelForge Plugin loaded. Bridge URL:", BASE_URL)
