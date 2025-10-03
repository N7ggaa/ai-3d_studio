-- Theme: Centralized theming system for the plugin

local Theme = {}

-- Default color palette
Theme.palette = {
    -- Primary colors
    primary = Color3.fromRGB(0, 120, 215),
    primaryDark = Color3.fromRGB(0, 90, 158),
    primaryLight = Color3.fromRGB(100, 181, 246),
    
    -- Accent colors
    accent = Color3.fromRGB(0, 188, 212),
    
    -- Background colors
    background = Color3.fromRGB(30, 30, 30),
    surface = Color3.fromRGB(40, 40, 40),
    surface2 = Color3.fromRGB(60, 60, 60),
    surface3 = Color3.fromRGB(80, 80, 80),
    
    -- Text colors
    text = Color3.fromRGB(255, 255, 255),
    textDim = Color3.fromRGB(180, 180, 180),
    textDisabled = Color3.fromRGB(120, 120, 120),
    
    -- Status colors
    success = Color3.fromRGB(56, 161, 105),
    onSuccess = Color3.fromRGB(255, 255, 255),
    warning = Color3.fromRGB(255, 180, 0),
    onWarning = Color3.fromRGB(0, 0, 0),
    error = Color3.fromRGB(232, 17, 35),
    onError = Color3.fromRGB(255, 255, 255),
    info = Color3.fromRGB(0, 113, 197),
    onInfo = Color3.fromRGB(255, 255, 255),
    
    -- Border colors
    border = Color3.fromRGB(90, 90, 90),
    borderLight = Color3.fromRGB(120, 120, 120),
    
    -- Other UI elements
    divider = Color3.fromRGB(60, 60, 60),
    hover = Color3.fromRGB(255, 255, 255),
    hoverAlpha = 0.1,
    active = Color3.fromRGB(255, 255, 255),
    activeAlpha = 0.2,
    
    -- Scrollbar
    scrollbar = Color3.fromRGB(100, 100, 100),
    scrollbarHover = Color3.fromRGB(120, 120, 120),
    scrollbarActive = Color3.fromRGB(150, 150, 150),
    
    -- Selection
    selection = Color3.fromRGB(0, 120, 215),
    selectionAlpha = 0.4,
    
    -- Tooltip
    tooltipBackground = Color3.fromRGB(50, 50, 50),
    tooltipText = Color3.fromRGB(255, 255, 255),
    
    -- Shadow
    shadow = Color3.fromRGB(0, 0, 0),
    shadowAlpha = 0.3
}

-- Light theme overrides
Theme.light = {
    background = Color3.fromRGB(240, 240, 240),
    surface = Color3.fromRGB(255, 255, 255),
    surface2 = Color3.fromRGB(245, 245, 245),
    surface3 = Color3.fromRGB(235, 235, 235),
    
    text = Color3.fromRGB(30, 30, 30),
    textDim = Color3.fromRGB(100, 100, 100),
    textDisabled = Color3.fromRGB(180, 180, 180),
    
    border = Color3.fromRGB(200, 200, 200),
    borderLight = Color3.fromRGB(220, 220, 220),
    
    divider = Color3.fromRGB(230, 230, 230),
    hover = Color3.fromRGB(0, 0, 0),
    hoverAlpha = 0.05,
    active = Color3.fromRGB(0, 0, 0),
    activeAlpha = 0.1,
    
    scrollbar = Color3.fromRGB(180, 180, 180),
    scrollbarHover = Color3.fromRGB(160, 160, 160),
    scrollbarActive = Color3.fromRGB(140, 140, 140),
    
    tooltipBackground = Color3.fromRGB(250, 250, 250),
    tooltipText = Color3.fromRGB(30, 30, 30),
    
    shadowAlpha = 0.15
}

-- Dark theme (default)
Theme.dark = {
    -- Uses the default palette
}

-- High contrast theme
Theme.highContrast = {
    background = Color3.fromRGB(0, 0, 0),
    surface = Color3.fromRGB(0, 0, 0),
    surface2 = Color3.fromRGB(30, 30, 30),
    surface3 = Color3.fromRGB(60, 60, 60),
    
    text = Color3.fromRGB(255, 255, 255),
    textDim = Color3.fromRGB(200, 200, 200),
    textDisabled = Color3.fromRGB(120, 120, 120),
    
    border = Color3.fromRGB(255, 255, 255),
    borderLight = Color3.fromRGB(200, 200, 200),
    
    divider = Color3.fromRGB(100, 100, 100),
    hover = Color3.fromRGB(255, 255, 255),
    hoverAlpha = 0.2,
    active = Color3.fromRGB(255, 255, 255),
    activeAlpha = 0.3,
    
    scrollbar = Color3.fromRGB(150, 150, 150),
    scrollbarHover = Color3.fromRGB(180, 180, 180),
    scrollbarActive = Color3.fromRGB(210, 210, 210),
    
    tooltipBackground = Color3.fromRGB(0, 0, 0),
    tooltipText = Color3.fromRGB(255, 255, 255),
    
    shadowAlpha = 0.5
}

-- Get a theme by name
function Theme.getTheme(name)
    local theme = {}
    
    -- Start with the default palette
    for k, v in pairs(Theme.palette) do
        theme[k] = v
    end
    
    -- Apply theme overrides if it exists
    local themeOverrides = Theme[name]
    if themeOverrides then
        for k, v in pairs(themeOverrides) do
            theme[k] = v
        end
    end
    
    return theme
end

-- Convert a Color3 to a hex string
function Theme.toHex(color)
    return string.format("#%02X%02X%02X", 
        math.floor(color.r * 255 + 0.5),
        math.floor(color.g * 255 + 0.5),
        math.floor(color.b * 255 + 0.5)
    )
end

-- Lighten a color by a percentage (0-1)
function Theme.lighten(color, amount)
    amount = math.clamp(amount, 0, 1)
    return Color3.new(
        color.r + (1 - color.r) * amount,
        color.g + (1 - color.g) * amount,
        color.b + (1 - color.b) * amount
    )
end

-- Darken a color by a percentage (0-1)
function Theme.darken(color, amount)
    amount = math.clamp(amount, 0, 1)
    return Color3.new(
        color.r * (1 - amount),
        color.g * (1 - amount),
        color.b * (1 - amount)
    )
end

-- Create a color sequence for gradients
function Theme.createGradient(colors, positions)
    local colorSequence = {}
    
    if not positions then
        -- Distribute colors evenly if no positions are provided
        local step = 1 / (#colors - 1)
        for i, color in ipairs(colors) do
            table.insert(colorSequence, ColorSequenceKeypoint.new((i - 1) * step, color))
        end
    else
        -- Use provided positions
        for i, color in ipairs(colors) do
            table.insert(colorSequence, ColorSequenceKeypoint.new(positions[i], color))
        end
    end
    
    return ColorSequence.new(colorSequence)
end

-- Create a transparent version of a color
function Theme.withAlpha(color, alpha)
    return Color3.new(color.r, color.g, color.b), alpha
end

-- Get a color with a specific alpha value for use with UI elements
function Theme.getColorWithAlpha(color, alpha)
    return Color3.new(color.r, color.g, color.b), alpha
end

-- Get a text color that contrasts well with the background
function Theme.getContrastText(backgroundColor)
    -- Calculate relative luminance (perceived brightness)
    local r, g, b = backgroundColor.r, backgroundColor.g, backgroundColor.b
    local luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    
    -- Return black for light backgrounds, white for dark backgrounds
    return luminance > 0.5 and Color3.new(0, 0, 0) or Color3.new(1, 1, 1)
end

-- Get a style for a button based on its state
function Theme.getButtonStyle(theme, state)
    state = state or {}
    
    local style = {
        background = theme.surface,
        border = theme.border,
        text = theme.text,
        hover = false,
        active = false,
        disabled = false
    }
    
    -- Apply state overrides
    if state.hover then
        style.background = Theme.lighten(style.background, 0.1)
        style.hover = true
    end
    
    if state.active then
        style.background = Theme.darken(style.background, 0.1)
        style.border = theme.primary
        style.active = true
    end
    
    if state.disabled then
        style.background = Theme.darken(style.background, 0.2)
        style.text = theme.textDisabled
        style.disabled = true
    end
    
    return style
end

-- Get a style for an input field based on its state
function Theme.getInputStyle(theme, state)
    state = state or {}
    
    local style = {
        background = theme.surface,
        border = theme.border,
        text = theme.text,
        placeholder = theme.textDim,
        hover = false,
        focused = false,
        error = false
    }
    
    -- Apply state overrides
    if state.hover then
        style.border = theme.borderLight
        style.hover = true
    end
    
    if state.focused then
        style.border = theme.primary
        style.focused = true
    end
    
    if state.error then
        style.border = theme.error
        style.error = true
    end
    
    return style
end

return Theme
