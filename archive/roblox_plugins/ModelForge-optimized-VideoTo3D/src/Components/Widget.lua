-- Widget component for VideoTo3D plugin

local Widget = {}
Widget.__index = Widget

-- Theme colors
local THEME = {
    Background = Color3.fromRGB(45, 45, 45),
    Surface = Color3.fromRGB(60, 60, 60),
    Primary = Color3.fromRGB(0, 120, 215),
    PrimaryHover = Color3.fromRGB(0, 100, 180),
    Text = Color3.fromRGB(255, 255, 255),
    TextSecondary = Color3.fromRGB(200, 200, 200),
    TextDisabled = Color3.fromRGB(150, 150, 150),
    Border = Color3.fromRGB(100, 100, 100),
    Card = Color3.fromRGB(60, 60, 60),
    CardHover = Color3.fromRGB(70, 70, 70),
    Error = Color3.fromRGB(255, 100, 100),
    Success = Color3.fromRGB(100, 255, 100)
}

-- Services
local TweenService = game:GetService("TweenService")

-- Create a UI element with rounded corners
local function createRoundedFrame(parent, size, position, color)
    local frame = Instance.new("Frame")
    frame.Size = size
    frame.Position = position
    frame.BackgroundColor3 = color or THEME.Card
    frame.BorderSizePixel = 0
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = frame
    
    if parent then
        frame.Parent = parent
    end
    
    return frame
end

-- Create a text label
local function createLabel(parent, text, size, position, options)
    local label = Instance.new("TextLabel")
    label.Size = size or UDim2.new(1, 0, 0, 20)
    label.Position = position or UDim2.new(0, 0, 0, 0)
    label.BackgroundTransparency = 1
    label.Text = text or ""
    label.TextColor3 = options and options.TextColor3 or THEME.Text
    label.TextSize = options and options.TextSize or 14
    label.Font = options and options.Font or Enum.Font.SourceSans
    label.TextXAlignment = options and options.TextXAlignment or Enum.TextXAlignment.Left
    label.TextYAlignment = options and options.TextYAlignment or Enum.TextYAlignment.Center
    label.TextWrapped = options and options.TextWrapped or false
    label.Parent = parent
    
    return label
end

-- Create a button
local function createButton(parent, text, size, position, onClick)
    local button = Instance.new("TextButton")
    button.Size = size or UDim2.new(0, 100, 0, 36)
    button.Position = position or UDim2.new(0, 0, 0, 0)
    button.BackgroundColor3 = THEME.Primary
    button.Text = text or "Button"
    button.TextColor3 = THEME.Text
    button.Font = Enum.Font.SourceSansSemibold
    button.TextSize = 14
    button.AutoButtonColor = false
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = button
    
    -- Hover effect
    button.MouseEnter:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.2), {
            BackgroundColor3 = THEME.PrimaryHover
        }):Play()
    end)
    
    button.MouseLeave:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.2), {
            BackgroundColor3 = THEME.Primary
        }):Play()
    end)
    
    -- Click handler
    if onClick then
        button.MouseButton1Click:Connect(onClick)
    end
    
    if parent then
        button.Parent = parent
    end
    
    return button
end

-- Create a text input field
local function createInput(parent, placeholder, size, position)
    local container = createRoundedFrame(parent, size, position, THEME.Surface)
    
    local input = Instance.new("TextBox")
    input.Name = "Input"
    input.Size = UDim2.new(1, -20, 1, -12)
    input.Position = UDim2.new(0, 10, 0, 6)
    input.BackgroundTransparency = 1
    input.PlaceholderText = placeholder or "Enter text..."
    input.PlaceholderColor3 = THEME.TextDisabled
    input.Text = ""
    input.TextColor3 = THEME.Text
    input.TextSize = 14
    input.Font = Enum.Font.SourceSans
    input.TextXAlignment = Enum.TextXAlignment.Left
    input.ClipsDescendants = true
    input.Parent = container
    
    return input
end

-- Widget constructor
function Widget.new(callbacks)
    local self = setmetatable({}, Widget)
    
    self.callbacks = callbacks or {}
    self.isVisible = false
    
    -- Create the widget
    self:createUI()
    
    return self
end

-- Create the main UI
function Widget:createUI()
    -- Create the main widget
    self.widget = plugin:CreateDockWidgetPluginGui(
        "VideoTo3D_Widget",
        DockWidgetPluginGuiInfo.new(
            Enum.InitialDockState.Float,
            false,
            false,
            400,
            600,
            300,
            300
        )
    )
    self.widget.Title = "Video to 3D"
    self.widget.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    
    -- Main container
    local container = createRoundedFrame(self.widget, UDim2.new(1, -20, 1, -20), UDim2.new(0, 10, 0, 10), THEME.Background)
    
    -- Title
    local title = createLabel(container, "Video to 3D", UDim2.new(1, -20, 0, 40), UDim2.new(0, 15, 0, 10), {
        TextSize = 20,
        Font = Enum.Font.SourceSansSemibold,
        TextXAlignment = Enum.TextXAlignment.Left
    })
    
    -- Video URL input
    createLabel(container, "Video URL or ID:", UDim2.new(1, -40, 0, 20), UDim2.new(0, 15, 0, 60))
    self.urlInput = createInput(container, "Enter YouTube URL or video ID", UDim2.new(1, -30, 0, 36), UDim2.new(0, 15, 0, 85))
    
    -- Prompt input
    createLabel(container, "Prompt (optional):", UDim2.new(1, -40, 0, 20), UDim2.new(0, 15, 0, 135))
    self.promptInput = createInput(container, "Describe what you want to create", UDim2.new(1, -30, 0, 36), UDim2.new(0, 15, 0, 160))
    
    -- Process button
    self.processButton = createButton(container, "Generate 3D Model", UDim2.new(1, -30, 0, 40), UDim2.new(0, 15, 0, 220), function()
        local url = self.urlInput.Text
        local prompt = self.promptInput.Text
        
        if url == "" then
            self:showMessage("Please enter a video URL", THEME.Error)
            return
        end
        
        self:setLoading(true, "Processing video...")
        
        -- Call the process callback
        if self.callbacks.onProcess then
            spawn(function()
                local success, result = pcall(function()
                    return self.callbacks.onProcess(url, prompt, {
                        duration = 30, -- Process first 30 seconds
                        frameRate = 1  -- 1 frame per second
                    })
                end)
                
                self:setLoading(false)
                
                if success and result.success then
                    self:showMessage(result.message, THEME.Success)
                    
                    -- Add the model to the workspace
                    if result.model then
                        result.model.Parent = workspace
                    end
                else
                    self:showMessage("Failed to process video: " .. tostring(result or "Unknown error"), THEME.Error)
                end
            end)
        end
    end)
    
    -- Status message
    self.statusLabel = createLabel(container, "", UDim2.new(1, -30, 0, 20), UDim2.new(0, 15, 0, 280), {
        TextColor3 = THEME.TextSecondary,
        TextXAlignment = Enum.TextXAlignment.Center
    })
    
    -- Templates section
    local templatesLabel = createLabel(container, "Templates:", UDim2.new(1, -40, 0, 20), UDim2.new(0, 15, 0, 320), {
        TextSize = 16,
        Font = Enum.Font.SourceSansSemibold
    })
    
    -- Templates grid
    local templatesGrid = Instance.new("ScrollingFrame")
    templatesGrid.Name = "TemplatesGrid"
    templatesGrid.Size = UDim2.new(1, -30, 0, 180)
    templatesGrid.Position = UDim2.new(0, 15, 0, 350)
    templatesGrid.BackgroundTransparency = 1
    templatesGrid.ScrollBarThickness = 4
    templatesGrid.ScrollBarImageColor3 = THEME.Border
    templatesGrid.CanvasSize = UDim2.new(0, 0, 0, 0)
    templatesGrid.AutomaticCanvasSize = Enum.AutomaticSize.Y
    templatesGrid.Parent = container
    
    local gridLayout = Instance.new("UIGridLayout")
    gridLayout.CellSize = UDim2.new(0.5, -10, 0, 80)
    gridLayout.CellPadding = UDim2.new(0, 10, 0, 10)
    gridLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
    gridLayout.SortOrder = Enum.SortOrder.LayoutOrder
    gridLayout.Parent = templatesGrid
    
    -- Add some template buttons
    local templates = {
        {name = "Character", prompt = "A 3D character model", icon = "rbxassetid://6031075926"},
        {name = "Vehicle", prompt = "A 3D vehicle model", icon = "rbxassetid://6031075930"},
        {name = "Building", prompt = "A 3D building model", icon = "rbxassetid://6031075935"},
        {name = "Weapon", prompt = "A 3D weapon model", icon = "rbxassetid://6031075940"}
    }
    
    for _, template in ipairs(templates) do
        local templateButton = createRoundedFrame(templatesGrid, UDim2.new(1, 0, 0, 80), nil, THEME.Card)
        
        -- Template icon
        local icon = Instance.new("ImageLabel")
        icon.Size = UDim2.new(0, 60, 0, 60)
        icon.Position = UDim2.new(0, 10, 0.5, -30)
        icon.BackgroundTransparency = 1
        icon.Image = template.icon
        icon.Parent = templateButton
        
        -- Template name
        local nameLabel = createLabel(templateButton, template.name, UDim2.new(1, -80, 0, 20), UDim2.new(0, 80, 0.5, -10), {
            TextSize = 14,
            Font = Enum.Font.SourceSansSemibold
        })
        
        -- Hover effect
        templateButton.MouseEnter:Connect(function()
            TweenService:Create(templateButton, TweenInfo.new(0.2), {
                BackgroundColor3 = THEME.CardHover
            }):Play()
        end)
        
        templateButton.MouseLeave:Connect(function()
            TweenService:Create(templateButton, TweenInfo.new(0.2), {
                BackgroundColor3 = THEME.Card
            }):Play()
        end)
        
        -- Click handler
        templateButton.MouseButton1Click:Connect(function()
            self.promptInput.Text = template.prompt
            self:showMessage("Selected template: " .. template.name, THEME.Primary)
            
            if self.callbacks.onTemplateSelected then
                self.callbacks.onTemplateSelected(template)
            end
        end)
    end
    
    -- Hide the widget by default
    self:Hide()
end

-- Show the widget
function Widget:Show()
    self.widget.Enabled = true
    self.isVisible = true
end

-- Hide the widget
function Widget:Hide()
    self.widget.Enabled = false
    self.isVisible = false
end

-- Toggle widget visibility
function Widget:Toggle()
    if self.isVisible then
        self:Hide()
    else
        self:Show()
    end
end

-- Check if widget is visible
function Widget:IsVisible()
    return self.isVisible
end

-- Show a status message
function Widget:showMessage(message, color)
    self.statusLabel.Text = message
    self.statusLabel.TextColor3 = color or THEME.Text
end

-- Set loading state
function Widget:setLoading(isLoading, message)
    self.processButton.Text = isLoading and "Processing..." or "Generate 3D Model"
    self.processButton.Active = not isLoading
    
    if message then
        self:showMessage(message, THEME.TextSecondary)
    end
end

return Widget
