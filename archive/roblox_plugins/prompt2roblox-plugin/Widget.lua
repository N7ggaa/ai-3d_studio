-- Widget module for the Prompt2Roblox plugin
-- Modern UI with tabs, batch processing, and templates

local Widget = {}
Widget.__index = Widget

-- Simple theme colors
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
local HttpService = game:GetService("HttpService")

-- Theme system with light/dark mode support
local ThemeService = {}
ThemeService.__index = ThemeService

-- Define light and dark themes with modern design tokens
local THEMES = {
    dark = {
        Name = "Dark",
        -- Primary colors
        Primary = Color3.fromRGB(0, 162, 255),
        PrimaryHover = Color3.fromRGB(0, 182, 255),
        PrimaryPressed = Color3.fromRGB(0, 122, 204),
        
        -- Secondary colors
        Secondary = Color3.fromRGB(138, 180, 248),
        SecondaryHover = Color3.fromRGB(158, 200, 255),
        
        -- Status colors
        Success = Color3.fromRGB(56, 217, 123),
        Error = Color3.fromRGB(255, 87, 87),
        Warning = Color3.fromRGB(255, 193, 7),
        Info = Color3.fromRGB(0, 174, 239),
        
        -- Background colors
        Background = Color3.fromRGB(25, 25, 30),
        Surface = Color3.fromRGB(35, 35, 40),
        Card = Color3.fromRGB(45, 45, 50),
        CardHover = Color3.fromRGB(60, 60, 70),
        
        -- Text colors
        Text = Color3.fromRGB(245, 246, 247),
        TextSecondary = Color3.fromRGB(180, 185, 190),
        TextDisabled = Color3.fromRGB(120, 125, 130),
        
        -- Border and dividers
        Border = Color3.fromRGB(60, 64, 72),
        BorderHover = Color3.fromRGB(80, 84, 92),
        Divider = Color3.fromRGB(50, 54, 60),
        
        -- Shadows and overlays
        Shadow = Color3.fromRGB(0, 0, 0),
        Overlay = Color3.fromRGB(0, 0, 0),
        
        -- Animation and effects
        Transition = 0.2,
        HoverIntensity = 1.1,
        ActiveIntensity = 0.9,
        
        -- Elevation levels (for shadows and depth)
        Elevation = {
            Low = 0.05,
            Medium = 0.1,
            High = 0.2
        },
        
        -- Border radius
        BorderRadius = {
            Small = 4,
            Medium = 8,
            Large = 12,
            XLarge = 20
        },
        
        -- Spacing system (in pixels)
        Spacing = {
            XS = 4,
            S = 8,
            M = 12,
            L = 16,
            XL = 24,
            XXL = 32
        }
    },
    light = {
        Name = "Light",
        -- Primary colors
        Primary = Color3.fromRGB(0, 120, 212),
        PrimaryHover = Color3.fromRGB(0, 140, 232),
        PrimaryPressed = Color3.fromRGB(0, 90, 180),
        
        -- Secondary colors
        Secondary = Color3.fromRGB(100, 140, 220),
        SecondaryHover = Color3.fromRGB(120, 160, 240),
        
        -- Status colors
        Success = Color3.fromRGB(16, 137, 62),
        Error = Color3.fromRGB(197, 17, 17),
        Warning = Color3.fromRGB(202, 103, 2),
        Info = Color3.fromRGB(0, 120, 212),
        
        -- Background colors
        Background = Color3.fromRGB(250, 250, 250),
        Surface = Color3.fromRGB(255, 255, 255),
        Card = Color3.fromRGB(255, 255, 255),
        CardHover = Color3.fromRGB(245, 245, 245),
        
        -- Text colors
        Text = Color3.fromRGB(30, 30, 30),
        TextSecondary = Color3.fromRGB(100, 100, 100),
        TextDisabled = Color3.fromRGB(150, 150, 150),
        
        -- Border and dividers
        Border = Color3.fromRGB(200, 200, 200),
        BorderHover = Color3.fromRGB(170, 170, 170),
        Divider = Color3.fromRGB(220, 220, 220),
        
        -- Shadows and overlays
        Shadow = Color3.fromRGB(100, 100, 100),
        Overlay = Color3.fromRGB(0, 0, 0),
        
        -- Animation and effects
        Transition = 0.2,
        HoverIntensity = 1.05,
        ActiveIntensity = 0.95,
        
        -- Elevation levels (for shadows and depth)
        Elevation = {
            Low = 0.1,
            Medium = 0.15,
            High = 0.25
        },
        
        -- Border radius
        BorderRadius = {
            Small = 4,
            Medium = 8,
            Large = 12,
            XLarge = 20
        },
        
        -- Spacing system (in pixels)
        Spacing = {
            XS = 4,
            S = 8,
            M = 12,
            L = 16,
            XL = 24,
            XXL = 32
        }
    }
}

-- Current theme (default to dark)
local currentTheme = "dark"
local THEME = THEMES[currentTheme]

-- Theme management functions
function ThemeService:SetTheme(themeName)
    if THEMES[themeName] then
        currentTheme = themeName
        THEME = THEMES[themeName]
        self:UpdateTheme()
        self:SaveThemePreference()
        return true
    end
    return false
end

function ThemeService:ToggleTheme()
    return self:SetTheme(currentTheme == "dark" and "light" or "dark")
end

function ThemeService:GetCurrentTheme()
    return currentTheme
end

function ThemeService:SaveThemePreference()
    -- Save to DataStore or other persistence
    pcall(function()
        local success = pcall(function()
            local DataStoreService = game:GetService("DataStoreService")
            local store = DataStoreService:GetDataStore("Prompt2Roblox_Settings")
            store:SetAsync("theme", currentTheme)
        end)
        if not success then
            warn("Failed to save theme preference")
        end
    end)
end

function ThemeService:LoadThemePreference()
    -- Load from DataStore or other persistence
    pcall(function()
        local success, savedTheme = pcall(function()
            local DataStoreService = game:GetService("DataStoreService")
            local store = DataStoreService:GetDataStore("Prompt2Roblox_Settings")
            return store:GetAsync("theme")
        end)
        
        if success and savedTheme and THEMES[savedTheme] then
            self:SetTheme(savedTheme)
        end
    end)
end

-- Initialize theme service
ThemeService:LoadThemePreference()

-- Keyboard shortcuts
local KeybindService = {}
KeybindService.__index = KeybindService

local KEYBINDS = {
    {
        name = "Toggle Theme",
        keys = {"LeftControl", "T"},
        action = function()
            ThemeService:ToggleTheme()
        end
    },
    {
        name = "Process Video",
        keys = {"LeftControl", "Enter"},
        action = function(widget)
            if widget.currentTab == "single" then
                widget:processSingleVideo()
            elseif widget.currentTab == "batch" then
                widget:processBatchVideos()
            end
        end
    },
    {
        name = "Focus Search",
        keys = {"LeftControl", "F"},
        action = function(widget)
            if widget.searchBox and widget.searchBox:IsA("TextBox") then
                widget.searchBox:CaptureFocus()
            end
        end
    },
    {
        name = "Switch Tab",
        keys = {"Tab"},
        action = function(widget)
            local tabs = {"single", "batch", "templates"}
            local currentIndex = table.find(tabs, widget.currentTab) or 1
            local nextIndex = currentIndex % #tabs + 1
            widget:switchTab(tabs[nextIndex])
        end
    }
}

function KeybindService:HandleInput(input, widget)
    if input.UserInputType ~= Enum.UserInputType.Keyboard then return end
    
    local keysDown = {
        [Enum.KeyCode.LeftControl] = UserInputService:IsKeyDown(Enum.KeyCode.LeftControl),
        [Enum.KeyCode.LeftShift] = UserInputService:IsKeyDown(Enum.KeyCode.LeftShift),
        [Enum.KeyCode.LeftAlt] = UserInputService:IsKeyDown(Enum.KeyCode.LeftAlt),
        [Enum.KeyCode.RightControl] = UserInputService:IsKeyDown(Enum.KeyCode.RightControl),
        [Enum.KeyCode.RightShift] = UserInputService:IsKeyDown(Enum.KeyCode.RightShift),
        [Enum.KeyCode.RightAlt] = UserInputService:IsKeyDown(Enum.KeyCode.RightAlt)
    }
    
    for _, keybind in ipairs(KEYBINDS) do
        local allKeysPressed = true
        for _, key in ipairs(keybind.keys) do
            local keyCode = Enum.KeyCode[key]
            if not keysDown[keyCode] and keyCode ~= input.KeyCode then
                allKeysPressed = false
                break
            end
        end
        
        if allKeysPressed and input.KeyCode == Enum.KeyCode[keybind.keys[#keybind.keys]] then
            keybind.action(widget)
            break
        end
    end
end

-- Initialize keybind service
local UserInputService = game:GetService("UserInputService")

-- Add utility functions for colors
local function darken(color, intensity)
    return Color3.new(
        math.clamp(color.R * intensity, 0, 1),
        math.clamp(color.G * intensity, 0, 1),
        math.clamp(color.B * intensity, 0, 1)
    )
end

local function lighten(color, intensity)
    return Color3.new(
        math.clamp(color.R * (1 + (intensity - 1)) - (intensity - 1), 0, 1),
        math.clamp(color.G * (1 + (intensity - 1)) - (intensity - 1), 0, 1),
        math.clamp(color.B * (1 + (intensity - 1)) - (intensity - 1), 0, 1)
    )
end

-- UI Component Factories
local function createButton(parent, size, position, text, onClick)
    local button = Instance.new("TextButton")
    button.Size = size
    button.Position = position
    button.BackgroundColor3 = THEME.Primary
    button.TextColor3 = THEME.Text
    button.Text = text
    button.Font = Enum.Font.SourceSansSemibold
    button.TextSize = 14
    button.AutoButtonColor = false
    button.BorderSizePixel = 0
    button.ZIndex = 2
    button.Parent = parent
    
    -- Add corner radius
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = button
    
    -- Add hover and click effects
    button.MouseEnter:Connect(function()
        TweenService:Create(button, TweenInfo.new(THEME.Transition), {
            BackgroundColor3 = THEME.PrimaryHover,
            TextColor3 = THEME.Text
        }):Play()
    end)
    
    button.MouseLeave:Connect(function()
        TweenService:Create(button, TweenInfo.new(THEME.Transition), {
            BackgroundColor3 = THEME.Primary,
            TextColor3 = THEME.Text
        }):Play()
    end)
    
    button.MouseButton1Down:Connect(function()
        TweenService:Create(button, TweenInfo.new(THEME.Transition/2), {
            BackgroundColor3 = THEME.PrimaryPressed,
            TextColor3 = THEME.Text
        }):Play()
    end)
    
    button.MouseButton1Up:Connect(function()
        TweenService:Create(button, TweenInfo.new(THEME.Transition/2), {
            BackgroundColor3 = THEME.PrimaryHover,
            TextColor3 = THEME.Text
        }):Play()
        onClick(button)
    end)
    
    return button
end

local function createInputField(parent, size, position, placeholder, isPassword)
    local container = Instance.new("Frame")
    container.Size = size
    container.Position = position
    container.BackgroundColor3 = THEME.Card
    container.BorderSizePixel = 1
    container.BorderColor3 = THEME.Border
    container.ClipsDescendants = true
    container.Parent = parent
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 6)
    corner.Parent = container
    
    local textBox = Instance.new("TextBox")
    textBox.Size = UDim2.new(1, -20, 1, 0)
    textBox.Position = UDim2.new(0, 10, 0, 0)
    textBox.BackgroundTransparency = 1
    textBox.Text = ""
    textBox.PlaceholderText = placeholder
    textBox.TextColor3 = THEME.Text
    textBox.PlaceholderColor3 = THEME.TextDisabled
    textBox.TextXAlignment = Enum.TextXAlignment.Left
    textBox.Font = Enum.Font.SourceSans
    textBox.TextSize = 14
    textBox.ClipsDescendants = true
    textBox.Parent = container
    
    if isPassword then
        textBox.TextTransparency = 1
        local dots = Instance.new("TextLabel")
        dots.Size = UDim2.new(1, 0, 1, 0)
        dots.BackgroundTransparency = 1
        dots.Text = string.rep("•", #textBox.Text)
        dots.TextColor3 = THEME.Text
        dots.TextXAlignment = Enum.TextXAlignment.Left
        dots.Font = Enum.Font.SourceSans
        dots.TextSize = 14
        dots.Parent = container
        
        textBox:GetPropertyChangedSignal("Text"):Connect(function()
            dots.Text = string.rep("•", #textBox.Text)
        end)
    end
    
    -- Focus effects
    textBox.Focused:Connect(function()
        TweenService:Create(container, TweenInfo.new(THEME.Transition), {
            BorderColor3 = THEME.Primary,
            BackgroundColor3 = THEME.CardHover
        }):Play()
    end)
    
    textBox.FocusLost:Connect(function()
        TweenService:Create(container, TweenInfo.new(THEME.Transition), {
            BorderColor3 = THEME.Border,
            BackgroundColor3 = THEME.Card
        }):Play()
    end)
    
    return textBox, container
end

local function createCard(parent, size, position)
    local card = Instance.new("Frame")
    card.Size = size
    card.Position = position
    card.BackgroundColor3 = THEME.Card
    card.BorderSizePixel = 0
    card.ClipsDescendants = true
    card.Parent = parent
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = card
    
    -- Add subtle shadow
    local shadow = Instance.new("ImageLabel")
    shadow.Name = "Shadow"
    shadow.Size = UDim2.new(1, 10, 1, 10)
    shadow.Position = UDim2.new(0, -5, 0, -5)
    shadow.BackgroundTransparency = 1
    shadow.Image = "rbxassetid://5554236805"
    shadow.ImageColor3 = THEME.Shadow
    shadow.ImageTransparency = 0.9
    shadow.ScaleType = Enum.ScaleType.Slice
    shadow.SliceCenter = Rect.new(10, 10, 90, 90)
    shadow.ZIndex = -1
    shadow.Parent = card
    
    return card
end

-- Templates for common use cases
local TEMPLATES = {
    {
        id = "basic_script",
        name = "Basic Script",
        category = "Scripting",
        description = "A well-structured Roblox script with comments",
        prompt = "Create a well-commented Roblox script that demonstrates basic functionality including proper variable declarations, functions, and error handling.",
        icon = "rbxassetid://6031302932", -- Script icon
        tags = {"beginner", "scripting", "template"}
    },
    {
        id = "gui_layout",
        name = "GUI Layout",
        category = "UI/UX",
        description = "Modern responsive GUI with common elements",
        prompt = "Design a clean, responsive GUI layout that includes a title bar, navigation menu, content area with scrolling frame, and action buttons. Use appropriate padding and spacing.",
        icon = "rbxassetid://6031071051", -- GUI icon
        tags = {"ui", "design", "responsive"}
    },
    {
        id = "npc_behavior",
        name = "NPC Behavior",
        category = "Gameplay",
        description = "AI-driven NPC with pathfinding",
        prompt = "Create an NPC that uses pathfinding to navigate the map, detect and follow the nearest player, and has basic idle and chase states. Include smooth animations and proper collision handling.",
        icon = "rbxassetid://6034509018", -- NPC icon
        tags = {"ai", "gameplay", "pathfinding"}
    },
    {
        id = "tycoon_base",
        name = "Tycoon Base",
        category = "Game Modes",
        description = "Basic tycoon game structure",
        prompt = "Set up the foundation for a tycoon game including baseplate, player plots, currency system, and a basic building system with placeable objects that generate income over time.",
        icon = "rbxassetid://6031071051",
        tags = {"tycoon", "game-mode", "economy"}
    },
    {
        id = "fps_controller",
        name = "FPS Controller",
        category = "Gameplay",
        description = "First-person shooter controller with smooth movement, jumping, and looking around.",
        prompt = [[Create a first-person controller with these features:
- WASD for movement with acceleration/deceleration
- Mouse look with configurable sensitivity
- Jumping with coyote time and jump buffering
- Crouching and sprinting
- Head bobbing and view tilt when strafing
- Footstep sounds based on surface material
- Smooth camera transitions
- Configurable movement settings (speed, jump height, etc.)]],
        icon = "rbxassetid://6031075926",
        tags = {"fps", "controller", "movement", "gameplay"},
        previewImage = "rbxassetid://6031075926",
        author = "ModelForge",
        version = "1.0.0",
        lastUpdated = "2025-08-28"
    },
    {
        id = "inventory_system",
        name = "Inventory System",
        category = "Gameplay",
        description = "Flexible inventory system with item stacking, equipment slots, and UI integration.",
        prompt = [[Design an inventory system with these features:
- Grid-based inventory with configurable size
- Item stacking and splitting
- Equipment slots (weapons, armor, accessories)
- Drag and drop functionality
- Tooltips with item details
- Save/load inventory state
- Weight and capacity system
- Item categories and filters
- Visual feedback for actions]],
        icon = "rbxassetid://6031075926",
        tags = {"inventory", "ui", "rpg", "system"},
        previewImage = "rbxassetid://6031075926",
        author = "ModelForge",
        version = "1.0.0",
        lastUpdated = "2025-08-28"
    },
    {
        id = "dialog_system",
        name = "Dialog System",
        category = "UI/UX",
        description = "Interactive dialog system with branching conversations and character expressions.",
        prompt = [[Create a dialog system with these features:
- Branching dialog trees
- Character expressions and portraits
- Typewriter text effect
- Dialog choices with conditions
- Variables and flags for tracking dialog state
- Audio support for character voices
- Skip and auto-advance options
- Integration with quest system]],
        icon = "rbxassetid://6031075926",
        tags = {"dialog", "ui", "npc", "story"},
        previewImage = "rbxassetid://6031075926",
        author = "ModelForge",
        version = "1.1.0",
        lastUpdated = "2025-08-28"
    },
    {
        id = "quest_system",
        name = "Quest System",
        category = "Gameplay",
        description = "Quest management system with objectives, rewards, and progress tracking.",
        prompt = [[Implement a quest system with these features:
- Multiple quest types (fetch, kill, explore, etc.)
- Quest givers and turn-in NPCs
- Objective tracking and progress updates
- Quest rewards (items, experience, etc.)
- Quest log UI
- Save/load quest progress
- Quest chains and dependencies
- Timed and repeatable quests
- Quest markers and waypoints]],
        icon = "rbxassetid://6031075926",
        tags = {"quest", "rpg", "gameplay", "system"},
        previewImage = "rbxassetid://6031075926",
        author = "ModelForge",
        version = "1.2.0",
        lastUpdated = "2025-08-28"
    },
    {
        id = "day_night_cycle",
        name = "Day/Night Cycle",
        category = "Environment",
        description = "Dynamic day/night cycle with configurable lighting and environmental effects.",
        prompt = [[Create a day/night cycle with these features:
- Smooth transitions between day and night
- Configurable cycle duration
- Dynamic skybox and lighting changes
- Environmental effects (fog, ambient sounds, etc.)
- Time of day events (dawn, noon, dusk, midnight)
- Moon phases and star visibility
- Weather system integration
- Performance optimizations]],
        icon = "rbxassetid://6031075926",
        tags = {"environment", "lighting", "atmosphere", "effects"},
        previewImage = "rbxassetid://6031075926",
        author = "ModelForge",
        version = "1.0.0",
        lastUpdated = "2025-08-28"
    },
    {
        id = "ai_pathfinding",
        name = "AI Pathfinding",
        category = "AI",
        description = "Advanced pathfinding for NPCs with obstacle avoidance and dynamic navigation.",
        prompt = [[Implement an AI pathfinding system with these features:
- A* pathfinding algorithm
- Dynamic obstacle avoidance
- Navmesh generation and updates
- Path smoothing and optimization
- Multiple agent types with different movement capabilities
- Following and chasing behaviors
- Patrol routes and waypoint systems
- Performance optimizations for multiple agents]],
        icon = "rbxassetid://6031075926",
        tags = {"ai", "pathfinding", "navigation", "gameplay"},
        previewImage = "rbxassetid://6031075926",
        author = "ModelForge",
        version = "1.1.0",
        lastUpdated = "2025-08-28"
    },
    {
        id = "save_load_system",
        name = "Save/Load System",
        category = "System",
        description = "Robust save/load system for game state persistence.",
        prompt = [[Create a save/load system with these features:
- Serialization of game state to JSON
- Multiple save slots
- Auto-save functionality
- Data compression and encryption
- Versioning for save compatibility
- Error handling and recovery
- Cloud save support
- Progress tracking and statistics]],
        icon = "rbxassetid://6031075926",
        tags = {"save", "load", "data", "system"},
        previewImage = "rbxassetid://6031075926",
        author = "ModelForge",
        version = "1.0.0",
        lastUpdated = "2025-08-28"
    },
    {
        id = "combat_system",
        name = "Combat System",
        category = "Gameplay",
        description = "Modular combat system with stats, abilities, and damage calculations.",
        prompt = [[Design a combat system with these features:
- Attribute system (health, attack, defense, etc.)
- Damage calculation with modifiers
- Status effects (poison, stun, etc.)
- Combat abilities with cooldowns
- Hit detection and collision
- Combat log and damage numbers
- Enemy AI behaviors
- Loot and experience system
- Visual and audio feedback]],
        icon = "rbxassetid://6031075926",
        tags = {"combat", "rpg", "gameplay", "system"},
        previewImage = "rbxassetid://6031075926",
        author = "ModelForge",
        version = "1.2.0",
        lastUpdated = "2025-08-28"
    },
    {
        id = "quest_system",
        name = "Quest System",
        category = "Game Systems",
        description = "Quest management framework",
        prompt = "Create a quest system with support for main and side quests, objectives, rewards, and progress tracking. Include a quest log UI and notification system.",
        icon = "rbxassetid://6031071051",
        tags = {"quests", "progression", "ui"}
    }
}

-- Group templates by category
local TEMPLATE_CATEGORIES = {
    {
        id = "all",
        name = "All Templates",
        icon = "rbxassetid://6034509018"
    },
    {
        id = "scripting",
        name = "Scripting",
        icon = "rbxassetid://6031302932"
    },
    {
        id = "ui_ux",
        name = "UI/UX",
        icon = "rbxassetid://6031071051"
    },
    {
        id = "gameplay",
        name = "Gameplay",
        icon = "rbxassetid://6034509018"
    },
    {
        id = "game_systems",
        name = "Game Systems",
        icon = "rbxassetid://6031071051"
    },
    {
        id = "environment",
        name = "Environment",
        icon = "rbxassetid://6031071051"
    }
}

function Widget.new(plugin, callbacks)
    local self = setmetatable({}, Widget)
    
    self.plugin = plugin
    self.callbacks = callbacks or {}
    self.currentTab = "single"
    
    -- Initialize theme service
    self.themeService = setmetatable({}, { __index = ThemeService })
    
    -- Create widget with adjusted size
    self.widgetInfo = DockWidgetPluginGuiInfo.new(
        Enum.InitialDockState.Float,
        false,
        false,
        500,  -- Increased width for better layout
        700,  -- Increased height for better layout
        500,
        700
    )
    
    self.widget = plugin:CreateDockWidgetPluginGui("Prompt2Roblox_Widget", self.widgetInfo)
    self.widget.Title = "Prompt2Roblox"
    self.widget.Name = "Prompt2Roblox"
    
    -- State
    self.currentTab = "single"
    self.tabs = {}
    self.isProcessing = false
    
    self:createUI()
    
    return self
end

-- Helper function to create a rounded corner
local function createCorner(radius)
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, radius or 6)
    return corner
end

-- Create a styled button
local function createButton(name, parent, size, position)
    local button = Instance.new("TextButton")
    button.Name = name
    button.Size = size or UDim2.new(1, -20, 0, 36)
    button.Position = position or UDim2.new(0, 10, 0, 0)
    button.BackgroundColor3 = THEME.Primary
    button.TextColor3 = THEME.Text
    button.Font = Enum.Font.SourceSansSemibold
    button.TextSize = 14
    button.Text = name
    button.Parent = parent
    
    -- Add corner radius
    local corner = createCorner(6)
    corner.Parent = button
    
    -- Hover effect
    button.MouseEnter:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.2), {BackgroundColor3 = THEME.Secondary}):Play()
    end)
    
    button.MouseLeave:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.2), {BackgroundColor3 = THEME.Primary}):Play()
    end)
    
    return button
end

-- Create a card container
local function createCard(parent, size, position)
    local card = Instance.new("Frame")
    card.Size = size or UDim2.new(1, -20, 0, 100)
    card.Position = position or UDim2.new(0, 10, 0, 10)
    card.BackgroundColor3 = THEME.Card
    card.BorderSizePixel = 0
    card.Parent = parent
    
    -- Add corner radius
    local corner = createCorner(8)
    corner.Parent = card
    
    return card
end

function Widget:createTab(name, container)
    local tab = {
        name = name,
        container = Instance.new("ScrollingFrame"),
        visible = false
    }
    
    tab.container.Name = name .. "Tab"
    tab.container.Size = UDim2.new(1, 0, 1, -40)
    tab.container.Position = UDim2.new(0, 0, 0, 40)
    tab.container.BackgroundTransparency = 1
    tab.container.Visible = false
    tab.container.ScrollBarThickness = 6
    tab.container.ScrollBarImageColor3 = THEME.Border
    tab.container.CanvasSize = UDim2.new(0, 0, 0, 0)
    tab.container.AutomaticCanvasSize = Enum.AutomaticSize.Y
    tab.container.Parent = container
    
    -- Add padding
    local padding = Instance.new("UIPadding")
    padding.PaddingLeft = UDim.new(0, 10)
    padding.PaddingRight = UDim.new(0, 10)
    padding.PaddingTop = UDim.new(0, 10)
    padding.PaddingBottom = UDim.new(0, 10)
    padding.Parent = tab.container
    
    -- Add list layout
    local listLayout = Instance.new("UIListLayout")
    listLayout.Padding = UDim.new(0, 10)
    listLayout.Parent = tab.container
    
    return tab
        
        self.plugin = plugin
        self.callbacks = callbacks or {}
        self.currentTab = "single"
        
        -- Initialize theme service
        self.themeService = setmetatable({}, { __index = ThemeService })
end

function Widget:updateBatchStatus(message, type)
    self.batchStatusLabel.Text = message
    self.batchStatusLabel.TextColor3 = type == "error" and THEME.Error 
                                    or type == "success" and THEME.Success 
                                    or type == "warning" and THEME.Warning 
                                    or THEME.Text
    
    -- Auto-resize the status label
    self.batchStatusLabel.Size = UDim2.new(1, -24, 0, self.batchStatusLabel.TextBounds.Y)
    
    -- If this is an error, log it to the output
    if type == "error" then
        warn("[Prompt2Roblox] " .. message)
    end
end

function Widget:setBatchProcessingState(isProcessing, statusMessage)
    self.batchProcessButton.Text = isProcessing and "Processing..." or "Process Videos"
    self.batchProcessButton.Active = not isProcessing
    
    if isProcessing then
        self.batchUrlBox.TextEditable = false
        self.batchPromptBox.TextEditable = false
        
        -- Disable the button with a visual effect
        TweenService:Create(self.batchProcessButton, TweenInfo.new(0.2), {
            BackgroundColor3 = THEME.TextDisabled,
            TextColor3 = THEME.TextSecondary
        }):Play()
    else
        self.batchUrlBox.TextEditable = true
        self.batchPromptBox.TextEditable = true
        
        -- Re-enable the button with a visual effect
        TweenService:Create(self.batchProcessButton, TweenInfo.new(0.2), {
            BackgroundColor3 = THEME.Primary,
            TextColor3 = THEME.Text
        }):Play()
    end
    
    if statusMessage then
        self:updateBatchStatus(statusMessage, "")
    end
end

function Widget:createSingleTab()
    local tab = self.tabs.single.container
    
    -- URL Input
    local urlLabel = Instance.new("TextLabel")
    urlLabel.Size = UDim2.new(1, 0, 0, 20)
    urlLabel.Position = UDim2.new(0, 0, 0, 0)
    urlLabel.Text = "YouTube URL:"
    urlLabel.TextColor3 = THEME.Text
    urlLabel.TextXAlignment = Enum.TextXAlignment.Left
    urlLabel.Font = Enum.Font.SourceSansSemibold
    urlLabel.TextSize = 14
    urlLabel.BackgroundTransparency = 1
    urlLabel.Parent = tab
    
    self.urlBox = Instance.new("TextBox")
    self.urlBox.Size = UDim2.new(1, 0, 0, 30)
    self.urlBox.Position = UDim2.new(0, 0, 0, 25)
    self.urlBox.PlaceholderText = "https://www.youtube.com/watch?v=..."
    self.urlBox.ClearTextOnFocus = false
    self.urlBox.Parent = tab
    
    -- Prompt Input
    local promptLabel = Instance.new("TextLabel")
    promptLabel.Size = UDim2.new(1, 0, 0, 20)
    promptLabel.Position = UDim2.new(0, 0, 0, 65)
    promptLabel.Text = "Prompt (optional):"
    promptLabel.TextColor3 = THEME.Text
    promptLabel.TextXAlignment = Enum.TextXAlignment.Left
    promptLabel.Font = Enum.Font.SourceSansSemibold
    promptLabel.TextSize = 14
    promptLabel.BackgroundTransparency = 1
    promptLabel.Parent = tab
    
    self.promptBox = Instance.new("TextBox")
    self.promptBox.Size = UDim2.new(1, 0, 0, 100)
    self.promptBox.Position = UDim2.new(0, 0, 0, 90)
    self.promptBox.MultiLine = true
    self.promptBox.TextWrapped = true
    self.promptBox.PlaceholderText = "Describe what you want to create..."
    self.promptBox.ClearTextOnFocus = false
    self.promptBox.Parent = tab
    
    -- Process Button
    self.processButton = createButton("Process Video", tab, 
        UDim2.new(1, 0, 0, 40), UDim2.new(0, 0, 0, 200))
    
    -- Status Label
    self.statusLabel = Instance.new("TextLabel")
    self.statusLabel.Size = UDim2.new(1, 0, 0, 20)
    self.statusLabel.Position = UDim2.new(0, 0, 0, 250)
    self.statusLabel.BackgroundTransparency = 1
    self.statusLabel.Text = ""
    self.statusLabel.TextColor3 = THEME.Success
    self.statusLabel.TextXAlignment = Enum.TextXAlignment.Left
    self.statusLabel.Font = Enum.Font.SourceSans
    self.statusLabel.TextSize = 12
    self.statusLabel.Parent = tab
    
    -- Connect button click
    self.processButton.MouseButton1Click:Connect(function()
        local url = self.urlBox.Text:gsub("^%s*(.-)%s*$", "%1")
        local prompt = self.promptBox.Text:gsub("^%s*(.-)%s*$", "%1")
        
        if url == "" then
            self:updateStatus("Please enter a YouTube URL", "error")
            return
        end
        
        if self.callbacks.onProcess then
            self:updateStatus("Processing...", "info")
            self.isProcessing = true
            self.processButton.Text = "Processing..."
            
            -- Process in a separate thread to avoid freezing the UI
            task.spawn(function()
                local success, result = pcall(function()
                    return self.callbacks.onProcess(url, prompt)
                end)
                
                self.isProcessing = false
                self.processButton.Text = "Process Video"
                
                if success and result then
                    self:updateStatus("Processing completed successfully!", "success")
                else
                    local errorMsg = "Failed to process video"
                    if not success then
                        errorMsg = tostring(result)
                    end
                    self:updateStatus(errorMsg, "error")
                end
            end)
        end
    end)
end

function Widget:createBatchTab()
    local tab = self.tabs.batch.container
    
    -- Create a scroll frame for the tab content
    local scrollFrame = Instance.new("ScrollingFrame")
    scrollFrame.Name = "BatchScrollFrame"
    scrollFrame.Size = UDim2.new(1, 0, 1, 0)
    scrollFrame.Position = UDim2.new(0, 0, 0, 0)
    scrollFrame.BackgroundTransparency = 1
    scrollFrame.ScrollBarThickness = 6
    scrollBarThumbSize = 0.5
    scrollFrame.ScrollBarImageColor3 = THEME.Border
    scrollFrame.ScrollBarImageTransparency = 0.5
    scrollFrame.CanvasSize = UDim2.new(0, 0, 0, 600) -- Will be adjusted
    scrollFrame.Parent = tab
    
    -- Container for all content
    local content = Instance.new("Frame")
    content.Name = "Content"
    content.Size = UDim2.new(1, -12, 1, 0) -- Account for scrollbar
    content.BackgroundTransparency = 1
    content.Parent = scrollFrame
    
    -- Batch instructions card
    local instructionsCard = createCard(content, UDim2.new(1, 0, 0, 80), UDim2.new(0, 0, 0, 10))
    
    local instructionsIcon = Instance.new("ImageLabel")
    instructionsIcon.Name = "Icon"
    instructionsIcon.Size = UDim2.new(0, 24, 0, 24)
    instructionsIcon.Position = UDim2.new(0, 12, 0, 12)
    instructionsIcon.BackgroundTransparency = 1
    instructionsIcon.Image = "rbxassetid://6034509018" -- Info icon
    instructionsIcon.ImageColor3 = THEME.Primary
    instructionsIcon.Parent = instructionsCard
    
    local instructionsText = Instance.new("TextLabel")
    instructionsText.Name = "Text"
    instructionsText.Size = UDim2.new(1, -48, 1, -24)
    instructionsText.Position = UDim2.new(0, 48, 0, 12)
    instructionsText.BackgroundTransparency = 1
    instructionsText.Text = "Enter one YouTube URL per line. All videos will be processed with the same prompt. You can process up to 10 videos at once."
    instructionsText.TextColor3 = THEME.Text
    instructionsText.TextWrapped = true
    instructionsText.TextXAlignment = Enum.TextXAlignment.Left
    instructionsText.TextYAlignment = Enum.TextYAlignment.Top
    instructionsText.Font = Enum.Font.SourceSans
    instructionsText.TextSize = 13
    instructionsText.Parent = instructionsCard
    
    -- URLs Input Card
    local urlsCard = createCard(content, UDim2.new(1, 0, 0, 150), UDim2.new(0, 0, 0, 100))
    
    local urlsLabel = Instance.new("TextLabel")
    urlsLabel.Name = "Label"
    urlsLabel.Size = UDim2.new(1, -24, 0, 20)
    urlsLabel.Position = UDim2.new(0, 12, 0, 12)
    urlsLabel.BackgroundTransparency = 1
    urlsLabel.Text = "Video URLs (one per line)"
    urlsLabel.TextColor3 = THEME.Text
    urlsLabel.TextXAlignment = Enum.TextXAlignment.Left
    urlsLabel.Font = Enum.Font.SourceSansSemibold
    urlsLabel.TextSize = 14
    urlsLabel.Parent = urlsCard
    
    -- URL counter
    local urlCounter = Instance.new("TextLabel")
    urlCounter.Name = "Counter"
    urlCounter.Size = UDim2.new(0, 60, 0, 20)
    urlCounter.Position = UDim2.new(1, -72, 0, 12)
    urlCounter.AnchorPoint = Vector2.new(1, 0)
    urlCounter.BackgroundTransparency = 1
    urlCounter.Text = "0/10"
    urlCounter.TextColor3 = THEME.TextSecondary
    urlCounter.TextXAlignment = Enum.TextXAlignment.Right
    urlCounter.Font = Enum.Font.SourceSans
    urlCounter.TextSize = 12
    urlCounter.Parent = urlsCard
    
    -- URL input with scroll
    local urlScrollingFrame = Instance.new("ScrollingFrame")
    urlScrollingFrame.Name = "UrlScroller"
    urlScrollingFrame.Size = UDim2.new(1, -24, 1, -44)
    urlScrollingFrame.Position = UDim2.new(0, 12, 0, 40)
    urlScrollingFrame.BackgroundTransparency = 1
    urlScrollingFrame.ScrollBarThickness = 4
    urlScrollingFrame.ScrollBarImageColor3 = THEME.Border
    urlScrollingFrame.CanvasSize = UDim2.new(0, 0, 0, 0)
    urlScrollingFrame.Parent = urlsCard
    
    self.batchUrlBox = Instance.new("TextBox")
    self.batchUrlBox.Size = UDim2.new(1, 0, 1, 0)
    self.batchUrlBox.MultiLine = true
    self.batchUrlBox.TextWrapped = true
    self.batchUrlBox.PlaceholderText = "https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=..."
    self.batchUrlBox.ClearTextOnFocus = false
    self.batchUrlBox.TextColor3 = THEME.Text
    self.batchUrlBox.PlaceholderColor3 = THEME.TextDisabled
    self.batchUrlBox.TextXAlignment = Enum.TextXAlignment.Left
    self.batchUrlBox.TextYAlignment = Enum.TextYAlignment.Top
    self.batchUrlBox.Font = Enum.Font.SourceSans
    self.batchUrlBox.TextSize = 14
    self.batchUrlBox.Parent = urlScrollingFrame
    
    -- Update URL counter
    local function updateUrlCounter()
        local count = 0
        for _ in self.batchUrlBox.Text:gmatch("[^\r\n]+") do
            count = count + 1
        end
        urlCounter.Text = string.format("%d/10", math.min(count, 10))
        urlCounter.TextColor3 = count > 10 and THEME.Error or THEME.TextSecondary
    end
    
    self.batchUrlBox:GetPropertyChangedSignal("Text"):Connect(updateUrlCounter)
    
    -- Prompt Input Card
    local promptCard = createCard(content, UDim2.new(1, 0, 0, 150), UDim2.new(0, 0, 0, 260))
    
    local promptLabel = Instance.new("TextLabel")
    promptLabel.Name = "Label"
    promptLabel.Size = UDim2.new(1, -24, 0, 20)
    promptLabel.Position = UDim2.new(0, 12, 0, 12)
    promptLabel.BackgroundTransparency = 1
    promptLabel.Text = "Prompt for all videos"
    promptLabel.TextColor3 = THEME.Text
    promptLabel.TextXAlignment = Enum.TextXAlignment.Left
    promptLabel.Font = Enum.Font.SourceSansSemibold
    promptLabel.TextSize = 14
    promptLabel.Parent = promptCard
    
    -- Prompt input with scroll
    local promptScrollingFrame = Instance.new("ScrollingFrame")
    promptScrollingFrame.Name = "PromptScroller"
    promptScrollingFrame.Size = UDim2.new(1, -24, 1, -44)
    promptScrollingFrame.Position = UDim2.new(0, 12, 0, 40)
    promptScrollingFrame.BackgroundTransparency = 1
    promptScrollingFrame.ScrollBarThickness = 4
    promptScrollingFrame.ScrollBarImageColor3 = THEME.Border
    promptScrollingFrame.CanvasSize = UDim2.new(0, 0, 0, 0)
    promptScrollingFrame.Parent = promptCard
    
    self.batchPromptBox = Instance.new("TextBox")
    self.batchPromptBox.Size = UDim2.new(1, 0, 1, 0)
    self.batchPromptBox.MultiLine = true
    self.batchPromptBox.TextWrapped = true
    self.batchPromptBox.PlaceholderText = "Describe what you want to create from these videos..."
    self.batchPromptBox.ClearTextOnFocus = false
    self.batchPromptBox.TextColor3 = THEME.Text
    self.batchPromptBox.PlaceholderColor3 = THEME.TextDisabled
    self.batchPromptBox.TextXAlignment = Enum.TextXAlignment.Left
    self.batchPromptBox.TextYAlignment = Enum.TextYAlignment.Top
    self.batchPromptBox.Font = Enum.Font.SourceSans
    self.batchPromptBox.TextSize = 14
    self.batchPromptBox.Parent = promptScrollingFrame
    
    -- Process Button Card
    local buttonCard = createCard(content, UDim2.new(1, 0, 0, 80), UDim2.new(0, 0, 0, 420))
    
    -- Status label
    self.batchStatusLabel = Instance.new("TextLabel")
    self.batchStatusLabel.Name = "StatusLabel"
    self.batchStatusLabel.Size = UDim2.new(1, -24, 0, 0)
    self.batchStatusLabel.Position = UDim2.new(0, 12, 0, 12)
    self.batchStatusLabel.BackgroundTransparency = 1
    self.batchStatusLabel.Text = ""
    self.batchStatusLabel.TextColor3 = THEME.Text
    self.batchStatusLabel.TextWrapped = true
    self.batchStatusLabel.TextXAlignment = Enum.TextXAlignment.Left
    self.batchStatusLabel.TextYAlignment = Enum.TextYAlignment.Top
    self.batchStatusLabel.Font = Enum.Font.SourceSans
    self.batchStatusLabel.TextSize = 13
    self.batchStatusLabel.AutomaticSize = Enum.AutomaticSize.Y
    self.batchStatusLabel.Parent = buttonCard
    
    -- Process button
    self.batchProcessButton = createButton("Process Videos", buttonCard, 
        UDim2.new(1, -24, 0, 36), UDim2.new(0, 12, 1, -48))
    
    -- Connect batch process button with enhanced error handling
    self.batchProcessButton.MouseButton1Click:Connect(function()
        -- Get and validate URLs
        local urls = {}
        local urlCount = 0
        
        for url in self.batchUrlBox.Text:gmatch("[^\r\n]+") do
            url = url:gsub("^%s*(.-)%s*$", "%1")
            if url ~= "" then
                -- Basic URL validation
                if not url:match("^https?://") or not url:match("youtu") then
                    self:updateBatchStatus("Invalid URL: " .. url, "error")
                    return
                end
                
                table.insert(urls, url)
                urlCount = urlCount + 1
                
                -- Limit to 10 URLs per batch
                if urlCount >= 10 then
                    self:updateBatchStatus("Maximum of 10 videos per batch. Only the first 10 will be processed.", "warning")
                    break
                end
            end
        end
        
        if #urls == 0 then
            self:updateBatchStatus("Please enter at least one valid YouTube URL", "error")
            return
        end
        
        local prompt = self.batchPromptBox.Text:gsub("^%s*(.-)%s*$", "%1")
        if prompt == "" then
            self:updateBatchStatus("Please enter a prompt describing what to create", "error")
            return
        end
        
        -- Process the batch
        if self.callbacks.onBatchProcess then
            self:setBatchProcessingState(true, string.format("Processing %d video%s...", #urls, #urls > 1 and "s" or ""))
            
            -- Process in a separate thread to avoid freezing the UI
            task.spawn(function()
                local success, result = pcall(function()
                    return self.callbacks.onBatchProcess(urls, prompt)
                end)
                
                if success and result then
                    if result.success then
                        self:updateBatchStatus("Batch processing completed successfully!", "success")
                    else
                        self:updateBatchStatus("Batch processing completed with some issues: " .. (result.message or "Unknown error"), 
                                            result.status or "warning")
                    end
                else
                    self:updateBatchStatus("Error processing batch: " .. tostring(result), "error")
                end
                
                self:setBatchProcessingState(false, "")
                end)
                
                self.batchProcessButton.Text = "Process Batch"
                self.batchProcessButton.Active = true
                
                if success and result then
                    self.batchStatusLabel.TextColor3 = THEME.Success
                    self.batchStatusLabel.Text = string.format(
                        "Successfully processed %d/%d videos", 
                        result.success or 0, 
                        #urls
                    )
                else
                    self.batchStatusLabel.TextColor3 = THEME.Error
                    self.batchStatusLabel.Text = "Batch processing failed: " .. tostring(result or "Unknown error")
                end
            end)
        end
    end)
    
    -- Initial render
    scrollFrame.CanvasSize = UDim2.new(0, 0, 0, 600) -- Will be updated by renderTemplates
    self.templateStatusLabel.Size = UDim2.new(1, 0, 0, 20)
    self.templateStatusLabel.Position = UDim2.new(0, 0, 1, -30)
    self.templateStatusLabel.BackgroundTransparency = 1
    self.templateStatusLabel.Text = ""
    self.templateStatusLabel.TextColor3 = THEME.SubText
    self.templateStatusLabel.TextXAlignment = Enum.TextXAlignment.Left
    self.templateStatusLabel.Font = Enum.Font.SourceSansItalic
    self.templateStatusLabel.TextSize = 12
    self.templateStatusLabel.Parent = tab
end

function Widget:createTemplatesTab()
    local tab = self.tabs.templates.container
    tab.BackgroundColor3 = THEME.Background
    
    -- Create a search container
    local searchContainer = Instance.new("Frame")
    searchContainer.Name = "SearchContainer"
    searchContainer.Size = UDim2.new(1, -24, 0, 40)
    searchContainer.Position = UDim2.new(0, 12, 0, 12)
    searchContainer.BackgroundColor3 = THEME.Card
    searchContainer.BorderSizePixel = 0
    
    local searchCorner = Instance.new("UICorner")
    searchCorner.CornerRadius = UDim.new(0, 8)
    searchCorner.Parent = searchContainer
    
    -- Search icon
    local searchIcon = Instance.new("ImageLabel")
    searchIcon.Name = "SearchIcon"
    searchIcon.Size = UDim2.new(0, 20, 0, 20)
    searchIcon.Position = UDim2.new(0, 12, 0.5, -10)
    searchIcon.BackgroundTransparency = 1
    searchIcon.Image = "rbxassetid://6031302932" -- Search icon
    searchIcon.ImageColor3 = THEME.TextSecondary
    searchIcon.Parent = searchContainer
    
    -- Search box
    local searchBox = Instance.new("TextBox")
    searchBox.Name = "SearchBox"
    searchBox.Size = UDim2.new(1, -44, 1, -20)
    searchBox.Position = UDim2.new(0, 40, 0, 10)
    searchBox.BackgroundTransparency = 1
    searchBox.PlaceholderText = "Search templates..."
    searchBox.PlaceholderColor3 = THEME.TextDisabled
    searchBox.Text = ""
    searchBox.TextColor3 = THEME.Text
    searchBox.TextXAlignment = Enum.TextXAlignment.Left
    searchBox.Font = Enum.Font.SourceSans
    searchBox.TextSize = 14
    searchBox.ClearTextOnFocus = false
    searchBox.Parent = searchContainer
    
    searchContainer.Parent = tab
    
    -- Categories scroller
    local categoriesScroller = Instance.new("ScrollingFrame")
    categoriesScroller.Name = "CategoriesScroller"
    categoriesScroller.Size = UDim2.new(1, -24, 0, 50)
    categoriesScroller.Position = UDim2.new(0, 12, 0, 64)
    categoriesScroller.BackgroundTransparency = 1
    categoriesScroller.ScrollBarThickness = 0
    categoriesScroller.CanvasSize = UDim2.new(2, 0, 0, 0)
    categoriesScroller.AutomaticCanvasSize = Enum.AutomaticSize.X
    categoriesScroller.ScrollingDirection = Enum.ScrollingDirection.X
    categoriesScroller.VerticalScrollBarInset = Enum.ScrollBarInset.None
    
    local categoriesList = Instance.new("UIListLayout")
    categoriesList.FillDirection = Enum.FillDirection.Horizontal
    categoriesList.Padding = UDim.new(0, 8)
    categoriesList.SortOrder = Enum.SortOrder.LayoutOrder
    categoriesList.Parent = categoriesScroller
    
    categoriesScroller.Parent = tab
    
    -- Templates grid
    local templatesGrid = Instance.new("ScrollingFrame")
    templatesGrid.Name = "TemplatesGrid"
    templatesGrid.Size = UDim2.new(1, -24, 1, -140)
    templatesGrid.Position = UDim2.new(0, 12, 0, 126)
    templatesGrid.BackgroundTransparency = 1
    templatesGrid.ScrollBarThickness = 4
    templatesGrid.ScrollBarImageColor3 = THEME.Border
    templatesGrid.CanvasSize = UDim2.new(0, 0, 0, 0)
    templatesGrid.AutomaticCanvasSize = Enum.AutomaticSize.Y
    
    local gridLayout = Instance.new("UIGridLayout")
    gridLayout.CellSize = UDim2.new(0.5, -10, 0, 160)
    gridLayout.CellPadding = UDim2.new(0, 10, 0, 10)
    gridLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
    gridLayout.SortOrder = Enum.SortOrder.LayoutOrder
    gridLayout.Parent = templatesGrid
    
    -- Create a container for the templates grid and preview
    local contentContainer = Instance.new("Frame")
    contentContainer.Name = "ContentContainer"
    contentContainer.Size = UDim2.new(1, 0, 1, 0)
    contentContainer.BackgroundTransparency = 1
    contentContainer.Parent = tab
    
    templatesGrid.Parent = contentContainer
    
    -- Add a UIPadding to the templates grid
    local gridPadding = Instance.new("UIPadding")
    gridPadding.PaddingTop = UDim.new(0, 10)
    gridPadding.PaddingBottom = UDim.new(0, 10)
    gridPadding.PaddingLeft = UDim.new(0, 10)
    gridPadding.PaddingRight = UDim.new(0, 10)
    gridPadding.Parent = templatesGrid
    
    -- Preview panel (initially hidden)
    local previewPanel = Instance.new("Frame")
    previewPanel.Name = "PreviewPanel"
    previewPanel.Size = UDim2.new(0.4, 0, 1, -24)
    previewPanel.Position = UDim2.new(0.6, 12, 0, 12)
    previewPanel.BackgroundColor3 = THEME.Card
    previewPanel.BorderSizePixel = 0
    previewPanel.Visible = false
    previewPanel.ZIndex = 10
    
    local previewCorner = Instance.new("UICorner")
    previewCorner.CornerRadius = UDim.new(0, 8)
    previewCorner.Parent = previewPanel
    
    local previewTitle = Instance.new("TextLabel")
    previewTitle.Name = "Title"
    previewTitle.Size = UDim2.new(1, -24, 0, 30)
    previewTitle.Position = UDim2.new(0, 12, 0, 12)
    previewTitle.BackgroundTransparency = 1
    previewTitle.Text = "Template Preview"
    previewTitle.TextColor3 = THEME.Text
    previewTitle.Font = Enum.Font.SourceSansSemibold
    previewTitle.TextSize = 18
    previewTitle.TextXAlignment = Enum.TextXAlignment.Left
    previewTitle.Parent = previewPanel
    
    local previewDescription = Instance.new("TextLabel")
    previewDescription.Name = "Description"
    previewDescription.Size = UDim2.new(1, -24, 0, 60)
    previewDescription.Position = UDim2.new(0, 12, 0, 50)
    previewDescription.BackgroundTransparency = 1
    previewDescription.Text = "Select a template to preview"
    previewDescription.TextColor3 = THEME.TextSecondary
    previewDescription.TextWrapped = true
    previewDescription.TextXAlignment = Enum.TextXAlignment.Left
    previewDescription.TextYAlignment = Enum.TextYAlignment.Top
    previewDescription.Font = Enum.Font.SourceSans
    previewDescription.TextSize = 14
    previewDescription.Parent = previewPanel
    
    local useTemplateButton = Instance.new("TextButton")
    useTemplateButton.Name = "UseTemplateButton"
    useTemplateButton.Size = UDim2.new(1, -24, 0, 36)
    useTemplateButton.Position = UDim2.new(0, 12, 1, -56)
    useTemplateButton.BackgroundColor3 = THEME.Primary
    useTemplateButton.Text = "Use Template"
    useTemplateButton.TextColor3 = THEME.Text
    useTemplateButton.Font = Enum.Font.SourceSansSemibold
    useTemplateButton.TextSize = 14
    useTemplateButton.AutoButtonColor = false
    
    local buttonCorner = Instance.new("UICorner")
    buttonCorner.CornerRadius = UDim.new(0, 6)
    buttonCorner.Parent = useTemplateButton
    
    -- Hover effect for button
    useTemplateButton.MouseEnter:Connect(function()
        TweenService:Create(useTemplateButton, TweenInfo.new(0.2), {
            BackgroundColor3 = THEME.PrimaryHover
        }):Play()
    end)
    
    useTemplateButton.MouseLeave:Connect(function()
        TweenService:Create(useTemplateButton, TweenInfo.new(0.2), {
            BackgroundColor3 = THEME.Primary
        }):Play()
    end)
    
    useTemplateButton.Parent = previewPanel
    previewPanel.Parent = tab
    
    -- Function to render categories
    local function renderCategories()
        -- Clear existing categories
        for _, child in ipairs(categoriesScroller:GetChildren()) do
            if child:IsA("TextButton") then
                child:Destroy()
            end
        end
        
        -- Get all unique categories
        local categories = {"All"}
        local categorySet = {["All"] = true}
        
        for _, template in ipairs(TEMPLATES) do
            if not categorySet[template.category] then
                table.insert(categories, template.category)
                categorySet[template.category] = true
            end
        end
        
        -- Create category buttons
        for i, category in ipairs(categories) do
            local button = Instance.new("TextButton")
            button.Name = category .. "Category"
            button.Size = UDim2.new(0, 100, 0, 36)
            button.Position = UDim2.new(0, (i-1) * 108, 0, 0)
            button.BackgroundColor3 = category == "All" and THEME.Primary or THEME.Card
            button.Text = category
            button.TextColor3 = category == "All" and THEME.Text or THEME.TextSecondary
            button.Font = Enum.Font.SourceSansSemibold
            button.TextSize = 14
            button.AutoButtonColor = false
            
            local corner = Instance.new("UICorner")
            corner.CornerRadius = UDim.new(0, 18)
            corner.Parent = button
            
            -- Hover effect
            button.MouseEnter:Connect(function()
                if button.BackgroundColor3 ~= THEME.Primary then
                    TweenService:Create(button, TweenInfo.new(0.2), {
                        BackgroundColor3 = THEME.CardHover,
                        TextColor3 = THEME.Text
                    }):Play()
                end
            end)
            
            button.MouseLeave:Connect(function()
                if button.BackgroundColor3 ~= THEME.Primary then
                    TweenService:Create(button, TweenInfo.new(0.2), {
                        BackgroundColor3 = THEME.Card,
                        TextColor3 = THEME.TextSecondary
                    }):Play()
                end
            end)
            
            -- Click handler
            button.MouseButton1Click:Connect(function()
                -- Update all buttons
                for _, btn in ipairs(categoriesScroller:GetChildren()) do
                    if btn:IsA("TextButton") then
                        local isSelected = btn == button
                        TweenService:Create(btn, TweenInfo.new(0.2), {
                            BackgroundColor3 = isSelected and THEME.Primary or THEME.Card,
                            TextColor3 = isSelected and THEME.Text or THEME.TextSecondary
                        }):Play()
                    end
                end
                
                -- Filter templates
                renderTemplates(searchBox.Text, category == "All" and nil or category)
            end)
            
            button.Parent = categoriesScroller
        end
        
        -- Update canvas size
        categoriesScroller.CanvasSize = UDim2.new(0, #categories * 108 - 8, 0, 0)
    end
    
    -- Function to render templates
    local function renderTemplates(searchTerm, category)
        -- Clear existing templates
        for _, child in ipairs(templatesGrid:GetChildren()) do
            if child:IsA("TextButton") or child:IsA("Frame") then
                child:Destroy()
            end
        end
        
        -- Filter templates
        local filteredTemplates = {}
        local searchLower = searchTerm and string.lower(searchTerm) or ""
        
        for _, template in ipairs(TEMPLATES) do
            local matchesSearch = searchTerm == "" or
                string.find(string.lower(template.name), searchLower, 1, true) or
                string.find(string.lower(template.description), searchLower, 1, true) or
                string.find(string.lower(template.category), searchLower, 1, true)
                
            local matchesCategory = not category or template.category == category
            
            if matchesSearch and matchesCategory then
                table.insert(filteredTemplates, template)
            end
        end
        
        -- Show message if no templates found
        if #filteredTemplates == 0 then
            local noResults = Instance.new("TextLabel")
            noResults.Size = UDim2.new(1, 0, 1, 0)
            noResults.BackgroundTransparency = 1
            noResults.Text = "No templates found. Try a different search term."
            noResults.TextColor3 = THEME.TextSecondary
            noResults.TextSize = 16
            noResults.Font = Enum.Font.SourceSansItalic
            noResults.Parent = templatesGrid
            return
        end
        
        -- Create template cards
        for _, template in ipairs(filteredTemplates) do
            local card = Instance.new("TextButton")
            card.Name = template.id .. "Card"
            card.BackgroundColor3 = THEME.Card
            card.AutoButtonColor = false
            
            local corner = Instance.new("UICorner")
            corner.CornerRadius = UDim.new(0, 8)
            corner.Parent = card
            
            -- Hover effect
            card.MouseEnter:Connect(function()
                TweenService:Create(card, TweenInfo.new(0.2), {
                    BackgroundColor3 = THEME.CardHover,
                    Position = card.Position - UDim2.new(0, 0, 0, 2)
                }):Play()
            end)
            
            card.MouseLeave:Connect(function()
                TweenService:Create(card, TweenInfo.new(0.2), {
                    BackgroundColor3 = THEME.Card,
                    Position = card.Position + UDim2.new(0, 0, 0, 2)
                }):Play()
            end)
            
            -- Template icon
            local icon = Instance.new("ImageLabel")
            icon.Name = "Icon"
            icon.Size = UDim2.new(1, -16, 0, 80)
            icon.Position = UDim2.new(0, 8, 0, 8)
            icon.BackgroundColor3 = THEME.CardHover
            icon.Image = template.icon
            icon.ScaleType = Enum.ScaleType.Crop
            
            local iconCorner = Instance.new("UICorner")
            iconCorner.CornerRadius = UDim.new(0, 6)
            iconCorner.Parent = icon
            icon.Parent = card
            
            -- Template name
            local nameLabel = Instance.new("TextLabel")
            nameLabel.Name = "Name"
            nameLabel.Size = UDim2.new(1, -16, 0, 20)
            nameLabel.Position = UDim2.new(0, 8, 0, 96)
            nameLabel.BackgroundTransparency = 1
            nameLabel.Text = template.name
            nameLabel.TextColor3 = THEME.Text
            nameLabel.Font = Enum.Font.SourceSansSemibold
            nameLabel.TextSize = 14
            nameLabel.TextXAlignment = Enum.TextXAlignment.Left
            nameLabel.TextTruncate = Enum.TextTruncate.AtEnd
            nameLabel.Parent = card
            
            -- Template category
            local categoryLabel = Instance.new("TextLabel")
            categoryLabel.Name = "Category"
            categoryLabel.Size = UDim2.new(1, -16, 0, 16)
            categoryLabel.Position = UDim2.new(0, 8, 0, 116)
            categoryLabel.BackgroundTransparency = 1
            categoryLabel.Text = template.category
            categoryLabel.TextColor3 = THEME.TextSecondary
            categoryLabel.Font = Enum.Font.SourceSans
            categoryLabel.TextSize = 12
            categoryLabel.TextXAlignment = Enum.TextXAlignment.Left
            categoryLabel.Parent = card
            
            -- Click handler
            card.MouseButton1Click:Connect(function()
                -- Show preview panel
                previewPanel.Visible = true
                previewTitle.Text = template.name
                previewDescription.Text = template.description
                
                -- Update use template button
                useTemplateButton.MouseButton1Click:Connect(function()
                    if self.callbacks.onTemplateSelected then
                        self.callbacks.onTemplateSelected(template)
                    end
                end)
            end)
            
            card.Parent = templatesGrid
        end
    end
    
    -- Setup search box events
    local searchDebounce = false
    searchBox:GetPropertyChangedSignal("Text"):Connect(function()
        if not searchDebounce then
            searchDebounce = true
            wait(0.3) -- Debounce time
            renderTemplates(searchBox.Text, nil)
            searchDebounce = false
        end
    end)
    
    -- Initial render
    renderCategories()
    renderTemplates("", nil)
    
    -- Set up the preview panel close button
    local closeButton = Instance.new("TextButton")
    closeButton.Name = "CloseButton"
    closeButton.Size = UDim2.new(0, 24, 0, 24)
    closeButton.Position = UDim2.new(1, -32, 0, 12)
    closeButton.BackgroundTransparency = 1
    closeButton.Text = "✕"
    closeButton.TextColor3 = THEME.TextSecondary
    closeButton.Font = Enum.Font.SourceSansSemibold
    closeButton.TextSize = 18
    closeButton.Parent = previewPanel
    
    closeButton.MouseEnter:Connect(function()
        closeButton.TextColor3 = THEME.Text
    end)
    
    closeButton.MouseLeave:Connect(function()
        closeButton.TextColor3 = THEME.TextSecondary
    end)
    
    closeButton.MouseButton1Click:Connect(function()
        previewPanel.Visible = false
    end)
    
    -- Set up the preview image
    local previewImage = Instance.new("ImageLabel")
    previewImage.Name = "PreviewImage"
    previewImage.Size = UDim2.new(1, -24, 0, 150)
    previewImage.Position = UDim2.new(0, 12, 0, 90)
    previewImage.BackgroundColor3 = THEME.CardHover
    previewImage.BorderSizePixel = 0
    previewImage.ScaleType = Enum.ScaleType.Crop
    previewImage.Image = "rbxassetid://6031075926" -- Default image
    
    local imageCorner = Instance.new("UICorner")
    imageCorner.CornerRadius = UDim.new(0, 6)
    imageCorner.Parent = previewImage
    
    previewImage.Parent = previewPanel
    
    -- Update the preview function to show the template image
    local originalRenderTemplates = renderTemplates
    renderTemplates = function(searchTerm, category)
        originalRenderTemplates(searchTerm, category)
        
        -- Update the card click handler to show the preview image
        for _, card in ipairs(templatesGrid:GetChildren()) do
            if card:IsA("TextButton") and card.Name:find("Card$") then
                local templateId = card.Name:gsub("Card$", "")
                local template
                for _, t in ipairs(TEMPLATES) do
                    if t.id == templateId then
                        template = t
                        break
                    end
                end
                
                if template then
                    card.MouseButton1Click:Connect(function()
                        previewPanel.Visible = true
                        previewTitle.Text = template.name
                        previewDescription.Text = template.description
                        previewImage.Image = template.previewImage or template.icon or "rbxassetid://6031075926"
                        
                        -- Update use template button
                        useTemplateButton.MouseButton1Click:Connect(function()
                            if self.callbacks.onTemplateSelected then
                                self.callbacks.onTemplateSelected(template)
                            end
                        end)
                    end)
                end
            end
        end
    end
    
    -- Initial render
    renderCategories()
    renderTemplates("", nil)
    previewTitle.TextXAlignment = Enum.TextXAlignment.Left
    previewTitle.Font = Enum.Font.SourceSansSemibold
    previewTitle.TextSize = 16
    previewTitle.Parent = previewContainer
    
    local previewDescription = Instance.new("TextLabel")
    previewDescription.Name = "Description"
    previewDescription.Size = UDim2.new(1, -24, 0, 60)
    previewDescription.Position = UDim2.new(0, 12, 0, 50)
    previewDescription.BackgroundTransparency = 1
    previewDescription.Text = ""
    previewDescription.TextColor3 = THEME.Text
    previewDescription.TextWrapped = true
    previewDescription.TextXAlignment = Enum.TextXAlignment.Left
    previewDescription.TextYAlignment = Enum.TextYAlignment.Top
    previewDescription.Font = Enum.Font.SourceSans
    previewDescription.TextSize = 13
    previewDescription.Parent = previewContainer
    
    local previewPrompt = Instance.new("TextLabel")
    previewPrompt.Name = "Prompt"
    previewPrompt.Size = UDim2.new(1, -24, 0, 80)
    previewPrompt.Position = UDim2.new(0, 12, 0, 120)
    previewPrompt.BackgroundTransparency = 1
    previewPrompt.Text = ""
    previewPrompt.TextColor3 = THEME.TextSecondary
    previewPrompt.TextWrapped = true
    previewPrompt.TextXAlignment = Enum.TextXAlignment.Left
    previewPrompt.TextYAlignment = Enum.TextYAlignment.Top
    previewPrompt.Font = Enum.Font.SourceSansItalic
    previewPrompt.TextSize = 12
    previewPrompt.Parent = previewContainer
    
    local useTemplateButton = createButton("Use This Template", previewContainer, 
        UDim2.new(1, -24, 0, 36), UDim2.new(0, 12, 1, -48))
    useTemplateButton.Name = "UseTemplateButton"
    
    -- Function to render templates
    local function renderTemplates(filterText, categoryId)
        -- Clear existing templates
        for _, child in ipairs(templatesGrid:GetChildren()) do
            if child:IsA("TextButton") or child:IsA("ImageButton") then
                child:Destroy()
            end
        end
        
        -- Filter templates
        local filteredTemplates = {}
        for _, template in ipairs(TEMPLATES) do
            local matchesSearch = not filterText or filterText == "" or
                                template.name:lower():find(filterText:lower(), 1, true) or
                                template.description:lower():find(filterText:lower(), 1, true)
                                
            local matchesCategory = not categoryId or categoryId == "all" or 
                                  template.category:lower():find(categoryId:lower(), 1, true) or
                                  (template.tags and table.find(template.tags, categoryId))
            
            if matchesSearch and matchesCategory then
                table.insert(filteredTemplates, template)
            end
        end
        
        -- Sort templates by name
        table.sort(filteredTemplates, function(a, b)
            return a.name:lower() < b.name:lower()
        end)
        
        -- Create template buttons
        for _, template in ipairs(filteredTemplates) do
            local templateButton = Instance.new("TextButton")
            templateButton.Name = template.id
            templateButton.Size = UDim2.new(1, 0, 0, 120)
            templateButton.BackgroundColor3 = THEME.Card
            templateButton.BorderSizePixel = 0
            templateButton.AutoButtonColor = false
            templateButton.Parent = templatesGrid
            
            -- Add corner radius
            local corner = Instance.new("UICorner")
            corner.CornerRadius = UDim.new(0, 8)
            corner.Parent = templateButton
            
            -- Add hover effect
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
            
            -- Template icon
            local icon = Instance.new("ImageLabel")
            icon.Name = "Icon"
            icon.Size = UDim2.new(0, 32, 0, 32)
            icon.Position = UDim2.new(0, 12, 0, 12)
            icon.BackgroundTransparency = 1
            icon.Image = template.icon or "rbxassetid://6031302932"
            icon.ImageColor3 = THEME.Primary
            icon.Parent = templateButton
            
            -- Template name
            local nameLabel = Instance.new("TextLabel")
            nameLabel.Name = "Name"
            nameLabel.Size = UDim2.new(1, -56, 0, 20)
            nameLabel.Position = UDim2.new(0, 52, 0, 12)
            nameLabel.BackgroundTransparency = 1
            nameLabel.Text = template.name
            nameLabel.TextColor3 = THEME.Text
            nameLabel.TextXAlignment = Enum.TextXAlignment.Left
            nameLabel.Font = Enum.Font.SourceSansSemibold
            nameLabel.TextSize = 14
            nameLabel.TextTruncate = Enum.TextTruncate.AtEnd
            nameLabel.Parent = templateButton
            
            -- Template category
            local categoryLabel = Instance.new("TextLabel")
            categoryLabel.Name = "Category"
            categoryLabel.Size = UDim2.new(1, -56, 0, 16)
            categoryLabel.Position = UDim2.new(0, 52, 0, 34)
            categoryLabel.BackgroundTransparency = 1
            categoryLabel.Text = template.category or "General"
            categoryLabel.TextColor3 = THEME.TextSecondary
            categoryLabel.TextXAlignment = Enum.TextXAlignment.Left
            categoryLabel.Font = Enum.Font.SourceSans
            categoryLabel.TextSize = 12
            categoryLabel.Parent = templateButton
            
            -- Template description
            local descLabel = Instance.new("TextLabel")
            descLabel.Name = "Description"
            descLabel.Size = UDim2.new(1, -24, 0, 40)
            descLabel.Position = UDim2.new(0, 12, 0, 60)
            descLabel.BackgroundTransparency = 1
            descLabel.Text = template.description
            descLabel.TextColor3 = THEME.TextSecondary
            descLabel.TextWrapped = true
            descLabel.TextXAlignment = Enum.TextXAlignment.Left
            descLabel.TextYAlignment = Enum.TextYAlignment.Top
            descLabel.Font = Enum.Font.SourceSans
            descLabel.TextSize = 12
            descLabel.Parent = templateButton
            
            -- Click handler
            templateButton.MouseButton1Click:Connect(function()
                -- Show preview
                previewContainer.Visible = true
                previewTitle.Text = template.name
                previewDescription.Text = template.description
                previewPrompt.Text = "\"" .. template.prompt .. "\""
                
                -- Update use button
                useTemplateButton.MouseButton1Click:Connect(function()
                    if self.callbacks.onTemplateSelected then
                        self.callbacks.onTemplateSelected(template)
                    end
                end)
                
                -- Scroll to preview
                scrollFrame.CanvasPosition = Vector2.new(0, previewContainer.Position.Y.Offset - 20)
            end)
        end
        
        -- Update grid size
        local rowCount = math.ceil(#filteredTemplates / 2)
        local gridHeight = rowCount * 140 -- 120 height + 20 padding
        templatesGrid.Size = UDim2.new(1, 0, 0, gridHeight)
        
        -- Update canvas size
        local totalHeight = 140 + gridHeight + (previewContainer.Visible and 220 or 0)
        scrollFrame.CanvasSize = UDim2.new(0, 0, 0, totalHeight)
    end
    
    -- Create category buttons
    local function createCategoryButtons()
        local xPos = 0
        local buttonWidth = 120
        
        for i, category in ipairs(TEMPLATE_CATEGORIES) do
            local button = Instance.new("TextButton")
            button.Name = category.id
            button.Size = UDim2.new(0, buttonWidth, 0, 36)
            button.Position = UDim2.new(0, xPos, 0, 0)
            button.BackgroundColor3 = THEME.Card
            button.Text = category.name
            button.TextColor3 = THEME.Text
            button.Font = Enum.Font.SourceSansSemibold
            button.TextSize = 13
            button.AutoButtonColor = false
            button.Parent = categoriesScroller
            
            -- Add corner radius
            local corner = Instance.new("UICorner")
            corner.CornerRadius = UDim.new(0, 18)
            corner.Parent = button
            
            -- Add hover effect
            button.MouseEnter:Connect(function()
                TweenService:Create(button, TweenInfo.new(0.2), {
                    BackgroundColor3 = THEME.CardHover
                }):Play()
            end)
            
            button.MouseLeave:Connect(function()
                TweenService:Create(button, TweenInfo.new(0.2), {
                    BackgroundColor3 = button.Name == self.selectedCategory and THEME.Primary or THEME.Card
                }):Play()
            end)
            
            -- Click handler
            button.MouseButton1Click:Connect(function()
                self.selectedCategory = category.id
                
                -- Update all buttons
                for _, btn in ipairs(categoriesScroller:GetChildren()) do
                    if btn:IsA("TextButton") then
                        TweenService:Create(btn, TweenInfo.new(0.2), {
                            BackgroundColor3 = btn.Name == self.selectedCategory and THEME.Primary or THEME.Card,
                            TextColor3 = btn.Name == self.selectedCategory and THEME.Text or THEME.Text
                        }):Play()
                    end
                end
                
                -- Filter templates
                renderTemplates(searchBox.Text, category.id)
            end)
            
            xPos = xPos + buttonWidth + 10
        end
        
        -- Update scroller canvas size
        categoriesScroller.CanvasSize = UDim2.new(0, xPos, 0, 0)
        
        -- Select first category by default
        if #TEMPLATE_CATEGORIES > 0 then
            categoriesScroller:FindFirstChild(TEMPLATE_CATEGORIES[1].id).MouseButton1Click:Wait()
        end
    end
    
    -- Initialize
    self.selectedCategory = "all"
    createCategoryButtons()
    renderTemplates("", "all")
    
    -- Search functionality
    searchBox:GetPropertyChangedSignal("Text"):Connect(function()
        renderTemplates(searchBox.Text, self.selectedCategory)
    end)
    
    -- Initial render
    scrollFrame.CanvasSize = UDim2.new(0, 0, 0, 600) -- Will be updated by renderTemplates
end

function Widget:createTabs(container)
    self.tabButtons = {}
    
    -- Create tab buttons
    local tabNames = {"single", "batch", "templates"}
    local buttonWidth = 1 / #tabNames
    
    for i, tabName in ipairs(tabNames) do
        local displayName = tabName == "single" and "Single" 
                         or tabName == "batch" and "Batch" 
                         or "Templates"
        
        local button = Instance.new("TextButton")
        button.Name = tabName .. "TabButton"
        button.Size = UDim2.new(buttonWidth, -4, 0, 36)
        button.Position = UDim2.new((i-1) * buttonWidth + 0.01, 2, 0, 5)
        button.BackgroundColor3 = tabName == "single" and THEME.Primary or THEME.Background
        button.TextColor3 = tabName == "single" and THEME.Text or THEME.SubText
        button.Text = displayName
        button.Font = Enum.Font.SourceSansSemibold
        button.TextSize = 14
        button.AutoButtonColor = false
        button.Parent = container
        
        -- Add corner radius
        local corner = createCorner(4)
        corner.Parent = button
        
        -- Add hover effect
        button.MouseEnter:Connect(function()
            if button ~= self.currentTabButton then
                TweenService:Create(button, TweenInfo.new(0.2), {
                    BackgroundColor3 = THEME.CardHover,
                    TextColor3 = THEME.Text
                }):Play()
            end
        end)
        
        button.MouseLeave:Connect(function()
            if button ~= self.currentTabButton then
                TweenService:Create(button, TweenInfo.new(0.2), {
                    BackgroundColor3 = THEME.Background,
                    TextColor3 = THEME.SubText
                }):Play()
            end
        end)
        
        -- Store reference
        self.tabButtons[tabName] = button
        
        -- Connect click event
        button.MouseButton1Click:Connect(function()
            self:switchTab(tabName)
        end)
    end
    
    -- Create tab containers
    self.tabs = {
        single = self:createTab("single", container),
        batch = self:createTab("batch", container),
        templates = self:createTab("templates", container)
    }
    
    -- Create tab contents
    self:createSingleTab()
    self:createBatchTab()
    self:createTemplatesTab()
    
    -- Set default tab and store reference to the active button
    self.currentTabButton = self.tabButtons.single
    self:switchTab("single")
end

-- Helper function to update instance properties based on theme
local function updateInstanceTheme(instance, theme)
    if instance:IsA("TextLabel") or instance:IsA("TextButton") or instance:IsA("TextBox") then
        if instance:GetAttribute("ThemeTextColor") then
            instance.TextColor3 = theme[instance:GetAttribute("ThemeTextColor")] or theme.Text
        end
        if instance:GetAttribute("ThemeBackgroundColor") then
            instance.BackgroundColor3 = theme[instance:GetAttribute("ThemeBackgroundColor")]
        end
    elseif instance:IsA("Frame") or instance:IsA("ScrollingFrame") then
        if instance:GetAttribute("ThemeBackgroundColor") then
            instance.BackgroundColor3 = theme[instance:GetAttribute("ThemeBackgroundColor")]
        end
    end
    
    -- Update children recursively
    for _, child in ipairs(instance:GetChildren()) do
        updateInstanceTheme(child, theme)
    end
end

-- Function to apply theme to the entire UI
function Widget:updateTheme()
    if not self.container then return end
    
    -- Update the current theme reference
    THEME = THEMES[currentTheme]
    
    -- Update all UI elements
    updateInstanceTheme(self.container, THEME)
    
    -- Update tab buttons
    for name, button in pairs(self.tabButtons or {}) do
        if button:IsA("TextButton") then
            button.BackgroundColor3 = (self.currentTab == name) and THEME.Primary or THEME.Background
            button.TextColor3 = (self.currentTab == name) and THEME.Text or THEME.TextSecondary
        end
    end
end

function Widget:createUI()
    -- Main container with subtle gradient and shadow
    self.container = Instance.new("Frame")
    self.container.Name = "Prompt2RobloxWidget"
    self.container.Size = UDim2.new(1, 0, 1, 0)
    self.container.BackgroundColor3 = THEME.Background
    self.container.BorderSizePixel = 0
    
    -- Add corner radius
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = self.container
    
    -- Add shadow effect
    local shadow = Instance.new("ImageLabel")
    shadow.Name = "Shadow"
    shadow.Size = UDim2.new(1, 20, 1, 20)
    shadow.Position = UDim2.new(0, -10, 0, -10)
    shadow.BackgroundTransparency = 1
    shadow.Image = "rbxassetid://1316045217"
    shadow.ImageColor3 = Color3.fromRGB(0, 0, 0)
    shadow.ImageTransparency = 0.8
    shadow.ScaleType = Enum.ScaleType.Slice
    shadow.SliceCenter = Rect.new(10, 10, 118, 118)
    shadow.Parent = self.container
    
    -- Create the widget
    self.widget = plugin:CreateDockWidgetPluginGui(
        "Prompt2Roblox_Widget",
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
    self.widget.Title = "Prompt2Roblox"
    self.widget.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    self.widget.Parent = self.container
    
    -- Create tabs
    self:createTabs(self.widget)
    
    -- Set up theme
    self:updateTheme()
    self.container.BorderSizePixel = 0
    self.container:SetAttribute("ThemeBackgroundColor", "Background")
    
    -- Add subtle gradient
    local gradient = Instance.new("UIGradient")
    gradient.Color = ColorSequence.new({
        ColorSequenceKeypoint.new(0, THEME.Background),
        ColorSequenceKeypoint.new(1, THEME.Surface)
    })
    gradient.Rotation = 45
    gradient.Parent = self.container
    
    -- Add subtle shadow effect
    local shadow = Instance.new("ImageLabel")
    shadow.Name = "Shadow"
    shadow.BackgroundTransparency = 1
    shadow.Size = UDim2.new(1, 0, 1, 0)
    shadow.ZIndex = 0
    shadow.Image = "rbxassetid://5554236805"
    shadow.ImageColor3 = THEME.Shadow
    shadow.ImageTransparency = 0.8
    shadow.ScaleType = Enum.ScaleType.Slice
    shadow.SliceCenter = Rect.new(10, 10, 90, 90)
    shadow.Parent = self.container
    self.container.BorderSizePixel = 0
    self.container.Parent = self.widget
    
    -- Add padding
    local padding = Instance.new("UIPadding")
    padding.PaddingLeft = UDim.new(0, 12)
    padding.PaddingRight = UDim.new(0, 12)
    padding.PaddingTop = UDim.new(0, 12)
    padding.PaddingBottom = UDim.new(0, 12)
    padding.Parent = self.container
    
    -- Create tabs
    self:createTabs(self.container)
    
    -- Add theme toggle button
    self:addThemeToggleButton()
    
    -- Setup keyboard shortcuts
    self:setupKeyboardShortcuts()
    
    -- Apply initial theme
    self:updateTheme()
end

function Widget:addThemeToggleButton()
    -- Create theme toggle button
    local themeButton = Instance.new("TextButton")
    themeButton.Name = "ThemeToggle"
    themeButton.Size = UDim2.new(0, 32, 0, 32)
    themeButton.Position = UDim2.new(1, -40, 0, 8)
    themeButton.BackgroundColor3 = THEME.Card
    themeButton.Text = currentTheme == "dark" and "🌞" or "🌙"
    themeButton.TextSize = 18
    themeButton.ZIndex = 100
    themeButton:SetAttribute("ThemeBackgroundColor", "Card")
    themeButton:SetAttribute("ThemeTextColor", "Text")
    
    -- Style the button
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0.5, 0)
    corner.Parent = themeButton
    
    -- Add tooltip
    local tooltip = Instance.new("TextLabel")
    tooltip.Name = "Tooltip"
    tooltip.Size = UDim2.new(0, 120, 0, 28)
    tooltip.Position = UDim2.new(0, -124, 0.5, -14)
    tooltip.BackgroundColor3 = THEME.Card
    tooltip.TextColor3 = THEME.Text
    tooltip.Text = "Toggle Theme (Ctrl+T)"
    tooltip.TextSize = 12
    tooltip.Visible = false
    tooltip.ZIndex = 101
    tooltip:SetAttribute("ThemeBackgroundColor", "Card")
    tooltip:SetAttribute("ThemeTextColor", "Text")
    
    -- Style tooltip
    local tooltipCorner = Instance.new("UICorner")
    tooltipCorner.CornerRadius = UDim.new(0, 4)
    tooltipCorner.Parent = tooltip
    
    local tooltipPadding = Instance.new("UIPadding")
    tooltipPadding.PaddingLeft = UDim.new(0, 8)
    tooltipPadding.PaddingRight = UDim.new(0, 8)
    tooltipPadding.PaddingTop = UDim.new(0, 4)
    tooltipPadding.PaddingBottom = UDim.new(0, 4)
    tooltipPadding.Parent = tooltip
    
    tooltip.Parent = themeButton
    
    -- Show/hide tooltip on hover
    themeButton.MouseEnter:Connect(function()
        tooltip.Visible = true
    end)
    
    themeButton.MouseLeave:Connect(function()
        tooltip.Visible = false
    end)
    
    -- Toggle theme on click
    themeButton.MouseButton1Click:Connect(function()
        self.themeService:ToggleTheme()
        currentTheme = self.themeService:GetCurrentTheme()
        themeButton.Text = currentTheme == "dark" and "🌞" or "🌙"
        self:updateTheme()
    end)
    
    themeButton.Parent = self.container
end

function Widget:setupKeyboardShortcuts()
    -- Connect input handling for keyboard shortcuts
    self.inputBegan = UserInputService.InputBegan:Connect(function(input, gameProcessed)
        if gameProcessed then return end
        
        -- Check for Ctrl+T to toggle theme
        if input.KeyCode == Enum.KeyCode.T and UserInputService:IsKeyDown(Enum.KeyCode.LeftControl) then
            self.themeService:ToggleTheme()
            currentTheme = self.themeService:GetCurrentTheme()
            self:updateTheme()
            
            -- Update theme button icon
            local themeButton = self.container:FindFirstChild("ThemeToggle")
            if themeButton then
                themeButton.Text = currentTheme == "dark" and "🌞" or "🌙"
            end
        end
        
        -- Add more keyboard shortcuts here
    end)
end
end

function Widget:Show()
    self.widget.Enabled = true
    self.widget:Activate()
end

function Widget:Hide()
    self.widget.Enabled = false
end

-- Add batch processing callback if not provided
function Widget:setCallbacks(callbacks)
    self.callbacks = callbacks or {}
    
    -- Add default batch processing if not provided
    if not self.callbacks.onBatchProcess and self.callbacks.onProcess then
        self.callbacks.onBatchProcess = function(urls, prompt)
            local results = {success = 0}
            
            for _, url in ipairs(urls) do
                local success = self.callbacks.onProcess(url, prompt)
                if success then
                    results.success = results.success + 1
                end
                
                -- Small delay between requests
                task.wait(0.5)
            end
            
            return results
        end
    end
end

return Widget
