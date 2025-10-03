-- Notification: A component for displaying temporary messages to the user

local Roact = require(script.Parent.Parent.Vendor.Roact)
local RoactRodux = require(script.Parent.Parent.Vendor.RoactRodux)
local Flipper = require(script.Parent.Parent.Vendor.Flipper)

local Theme = require(script.Parent.Parent.Theme)
local Icons = require(script.Parent.Parent.Utils.Icons)

local Notification = Roact.PureComponent:extend("Notification")

Notification.defaultProps = {
    -- Required
    Message = "",
    
    -- Optional
    Title = nil,
    Duration = 5, -- seconds, 0 for persistent
    Type = "info", -- "info", "success", "warning", "error"
    
    -- Styling
    Theme = "dark",
    Position = UDim2.new(1, -20, 1, -20),
    AnchorPoint = Vector2.new(1, 1),
    MaxWidth = 300,
    
    -- Callbacks
    OnDismiss = nil,
    OnClick = nil,
    
    -- Internal
    Id = nil,
    Timestamp = nil
}

function Notification:init()
    -- Animation motor for enter/exit animations
    self.motor = Flipper.GroupMotor.new({
        position = 0,
        hover = 0,
        active = 0,
        progress = 0
    })
    
    self.motorBinding = Roact.createBinding(self.motor:getValue())
    self.motor:onStep(function(value)
        self.motorBinding:setValue(value)
    end)
    
    -- State
    self.state = {
        isHovered = false,
        isActive = false,
        isDismissed = false,
        progress = 0,
        remainingTime = self.props.Duration
    }
    
    -- Refs
    self.notificationRef = Roact.createRef()
    self.progressBarRef = Roact.createRef()
    
    -- Timer for auto-dismissal
    self.dismissTimer = nil
    self.progressTimer = nil
    self.lastUpdate = tick()
    
    -- Bind methods
    self.startDismissTimer = function()
        self:stopDismissTimer()
        
        if self.props.Duration > 0 then
            self.dismissTimer = task.delay(self.props.Duration, function()
                self:dismiss()
            end)
            
            -- Start progress bar animation if duration is more than 1 second
            if self.props.Duration > 1 then
                self:startProgressTimer()
            end
        end
    end
    
    self.stopDismissTimer = function()
        if self.dismissTimer then
            task.cancel(self.dismissTimer)
            self.dismissTimer = nil
        end
        
        if self.progressTimer then
            task.cancel(self.progressTimer)
            self.progressTimer = nil
        end
    end
    
    self.startProgressTimer = function()
        self:stopDismissTimer()
        
        self.lastUpdate = tick()
        self:setState({
            progress = 0
        })
        
        local function updateProgress()
            local now = tick()
            local elapsed = now - self.lastUpdate
            self.lastUpdate = now
            
            self:setState(function(prevState)
                local newProgress = math.min(prevState.progress + (elapsed / self.props.Duration), 1)
                return {
                    progress = newProgress,
                    remainingTime = self.props.Duration * (1 - newProgress)
                }
            end)
            
            if self.state.progress < 1 then
                self.progressTimer = task.delay(0.05, updateProgress)
            end
        end
        
        self.progressTimer = task.spawn(updateProgress)
    end
end

function Notification:didMount()
    -- Animate in
    self.motor:setGoal({
        position = Flipper.Spring.new(1, {
            frequency = 6,
            dampingRatio = 1
        })
    })
    
    -- Start auto-dismiss timer if duration is set
    self.startDismissTimer()
end

function Notification:didUpdate(prevProps, prevState)
    -- Restart timer if duration changes
    if self.props.Duration ~= prevProps.Duration and not self.state.isDismissed then
        self.startDismissTimer()
    end
    
    -- Pause/resume timer on hover
    if self.state.isHovered ~= prevState.isHovered then
        if self.state.isHovered then
            self.stopDismissTimer()
        else
            self.startDismissTimer()
        end
    end
end

function Notification:willUnmount()
    self:stopDismissTimer()
    
    if self.motor then
        self.motor:destroy()
    end
end

function Notification:dismiss()
    if self.state.isDismissed then return end
    
    self:setState({
        isDismissed = true
    })
    
    -- Animate out
    self.motor:setGoal({
        position = Flipper.Spring.new(0, {
            frequency = 6,
            dampingRatio = 1
        })
    })
    
    -- Notify parent after animation completes
    task.delay(0.3, function()
        if self.props.OnDismiss then
            self.props.OnDismiss(self.props.Id)
        end
    end)
end

function Notification:render()
    local theme = Theme.getTheme(self.props.Theme)
    local state = self.state
    local props = self.props
    
    -- Get colors based on notification type
    local backgroundColor, textColor, icon, iconColor
    
    if props.Type == "success" then
        backgroundColor = theme.success
        textColor = theme.onSuccess
        icon = Icons.getIcon("check-circle")
        iconColor = theme.onSuccess
    elseif props.Type == "warning" then
        backgroundColor = theme.warning
        textColor = theme.onWarning
        icon = Icons.getIcon("alert-triangle")
        iconColor = theme.onWarning
    elseif props.Type == "error" then
        backgroundColor = theme.error
        textColor = theme.onError
        icon = Icons.getIcon("x-circle")
        iconColor = theme.onError
    else -- info
        backgroundColor = theme.surface2
        textColor = theme.text
        icon = Icons.getIcon("info")
        iconColor = theme.accent
    end
    
    -- Animation values
    local motorValues = self.motorBinding:getValue()
    local position = motorValues.position or 0
    local hover = motorValues.hover or 0
    local active = motorValues.active or 0
    
    -- Calculate transform
    local offsetX = (1 - position) * 20
    local scale = 0.9 + (position * 0.1)
    local transparency = 1 - position
    
    -- Hover/active effects
    local hoverOffset = hover * -2
    local activeOffset = active * 2
    
    -- Create children
    local children = {
        UICorner = Roact.createElement("UICorner", {
            CornerRadius = UDim.new(0, 6)
        }),
        
        -- Background
        Background = Roact.createElement("Frame", {
            Size = UDim2.new(1, 0, 1, 0),
            BackgroundColor3 = backgroundColor,
            BackgroundTransparency = 0.2 + (transparency * 0.8),
            BorderSizePixel = 0,
            ZIndex = 1
        }, {
            UICorner = Roact.createElement("UICorner", {
                CornerRadius = UDim.new(0, 6)
            }),
            
            -- Shadow
            Shadow = Roact.createElement("ImageLabel", {
                Size = UDim2.new(1, 10, 1, 10),
                Position = UDim2.new(0, -5, 0, -5),
                BackgroundTransparency = 1,
                Image = "rbxassetid://1316045217",
                ImageColor3 = Color3.new(0, 0, 0),
                ImageTransparency = 0.8,
                ScaleType = Enum.ScaleType.Slice,
                SliceCenter = Rect.new(10, 10, 118, 118),
                ZIndex = 0
            })
        }),
        
        -- Content
        Content = Roact.createElement("Frame", {
            Size = UDim2.new(1, -20, 1, -20),
            Position = UDim2.new(0, 10, 0, 10),
            BackgroundTransparency = 1,
            ZIndex = 2
        }, {
            UIListLayout = Roact.createElement("UIListLayout", {
                SortOrder = Enum.SortOrder.LayoutOrder,
                HorizontalAlignment = Enum.HorizontalAlignment.Left,
                VerticalAlignment = Enum.VerticalAlignment.Top,
                Padding = UDim.new(0, 10)
            }),
            
            -- Header
            Header = Roact.createElement("Frame", {
                Size = UDim2.new(1, 0, 0, 0),
                AutomaticSize = Enum.AutomaticSize.Y,
                BackgroundTransparency = 1,
                LayoutOrder = 1,
                ZIndex = 2
            }, {
                UIListLayout = Roact.createElement("UIListLayout", {
                    SortOrder = Enum.SortOrder.LayoutOrder,
                    FillDirection = Enum.FillDirection.Horizontal,
                    VerticalAlignment = Enum.VerticalAlignment.Center,
                    Padding = UDim.new(0, 8)
                }),
                
                -- Icon
                Icon = Roact.createElement("ImageLabel", {
                    Size = UDim2.new(0, 20, 0, 20),
                    BackgroundTransparency = 1,
                    Image = icon,
                    ImageColor3 = iconColor,
                    LayoutOrder = 1,
                    ZIndex = 2
                }, {
                    UIAspectRatioConstraint = Roact.createElement("UIAspectRatioConstraint")
                }),
                
                -- Title
                Title = props.Title and Roact.createElement("TextLabel", {
                    Size = UDim2.new(1, -60, 0, 20),
                    AutomaticSize = Enum.AutomaticSize.Y,
                    BackgroundTransparency = 1,
                    Text = props.Title,
                    TextColor3 = textColor,
                    TextXAlignment = Enum.TextXAlignment.Left,
                    TextYAlignment = Enum.TextYAlignment.Center,
                    TextTruncate = Enum.TextTruncate.AtEnd,
                    Font = Enum.Font.SourceSansSemibold,
                    TextSize = 14,
                    LayoutOrder = 2,
                    ZIndex = 2
                }) or nil,
                
                -- Spacer
                Spacer = Roact.createElement("Frame", {
                    Size = UDim2.new(1, 0, 0, 0),
                    BackgroundTransparency = 1,
                    LayoutOrder = 3
                }),
                
                -- Close button
                CloseButton = Roact.createElement("ImageButton", {
                    Size = UDim2.new(0, 16, 0, 16),
                    BackgroundTransparency = 1,
                    Image = Icons.getIcon("x"),
                    ImageColor3 = textColor,
                    ImageTransparency = 0.3,
                    LayoutOrder = 4,
                    ZIndex = 2,
                    [Roact.Event.MouseButton1Click] = function()
                        self:dismiss()
                    end
                }, {
                    HoverEffect = Roact.createElement("Frame", {
                        Size = UDim2.new(1, 4, 1, 4),
                        Position = UDim2.new(0, -2, 0, -2),
                        BackgroundColor3 = textColor,
                        BackgroundTransparency = 0.9,
                        BorderSizePixel = 0,
                        ZIndex = -1,
                        Visible = state.isHovered
                    }, {
                        UICorner = Roact.createElement("UICorner", {
                            CornerRadius = UDim.new(1, 0)
                        })
                    })
                })
            }),
            
            -- Message
            Message = Roact.createElement("TextLabel", {
                Size = UDim2.new(1, 0, 0, 0),
                AutomaticSize = Enum.AutomaticSize.Y,
                BackgroundTransparency = 1,
                Text = props.Message,
                TextColor3 = textColor,
                TextXAlignment = Enum.TextXAlignment.Left,
                TextYAlignment = Enum.TextYAlignment.Top,
                TextWrapped = true,
                Font = Enum.Font.SourceSans,
                TextSize = 13,
                LayoutOrder = 2,
                ZIndex = 2
            }, {
                UIPadding = Roact.createElement("UIPadding", {
                    PaddingLeft = UDim.new(0, 28) -- Align with icon
                })
            })
        }),
        
        -- Progress bar for auto-dismissal
        ProgressBar = props.Duration > 0 and Roact.createElement("Frame", {
            Size = UDim2.new(1, 0, 0, 2),
            Position = UDim2.new(0, 0, 1, -2),
            BackgroundTransparency = 1,
            BorderSizePixel = 0,
            ZIndex = 3,
            [Roact.Ref] = self.progressBarRef
        }, {
            Background = Roact.createElement("Frame", {
                Size = UDim2.new(1, 0, 1, 0),
                BackgroundColor3 = Color3.new(0, 0, 0),
                BackgroundTransparency = 0.8,
                BorderSizePixel = 0,
                ZIndex = 3
            }, {
                UICorner = Roact.createElement("UICorner", {
                    CornerRadius = UDim.new(0, 1)
                })
            }),
            
            Progress = Roact.createElement("Frame", {
                Size = UDim2.new(1 - state.progress, 0, 1, 0),
                AnchorPoint = Vector2.new(0, 0.5),
                Position = UDim2.new(0, 0, 0.5, 0),
                BackgroundColor3 = textColor,
                BackgroundTransparency = 0.5,
                BorderSizePixel = 0,
                ZIndex = 4
            }, {
                UICorner = Roact.createElement("UICorner", {
                    CornerRadius = UDim.new(0, 1)
                })
            })
        }) or nil
    }
    
    return Roact.createElement("TextButton", {
        Size = UDim2.new(0, props.MaxWidth, 0, 0),
        AutomaticSize = Enum.AutomaticSize.Y,
        Position = props.Position + UDim2.new(offsetX, 0, 0, 0),
        AnchorPoint = props.AnchorPoint,
        BackgroundTransparency = 1,
        Text = "",
        AutoButtonColor = false,
        ZIndex = props.ZIndex or 10,
        [Roact.Ref] = self.notificationRef,
        [Roact.Event.Activated] = function()
            if props.OnClick then
                props.OnClick()
            end
        end,
        [Roact.Event.MouseEnter] = function()
            self:setState({
                isHovered = true
            })
            
            self.motor:setGoal({
                hover = Flipper.Spring.new(1, {
                    frequency = 6,
                    dampingRatio = 0.7
                })
            })
        end,
        [Roact.Event.MouseLeave] = function()
            self:setState({
                isHovered = false,
                isActive = false
            })
            
            self.motor:setGoal({
                hover = Flipper.Spring.new(0, {
                    frequency = 6,
                    dampingRatio = 0.7
                })
            })
        end,
        [Roact.Event.InputBegan] = function(input)
            if input.UserInputType == Enum.UserInputType.MouseButton1 then
                self:setState({
                    isActive = true
                })
                
                self.motor:setGoal({
                    active = Flipper.Spring.new(1, {
                        frequency = 6,
                        dampingRatio = 0.7
                    })
                })
            end
        end,
        [Roact.Event.InputEnded] = function(input)
            if input.UserInputType == Enum.UserInputType.MouseButton1 then
                self:setState({
                    isActive = false
                })
                
                self.motor:setGoal({
                    active = Flipper.Spring.new(0, {
                        frequency = 6,
                        dampingRatio = 0.7
                    })
                })
            end
        end
    }, {
        -- Apply transform
        Roact.createElement("UIScale", {
            Scale = scale
        }),
        
        -- Apply transparency
        Roact.createElement("UIStroke", {
            Color = Color3.new(1, 1, 1),
            Transparency = 0.9,
            Thickness = 1
        }),
        
        -- Add children
        table.unpack(children)
    })
end

return RoactRodux.connect(
    function(state, props)
        return {
            Theme = state.settings.theme or props.Theme
        }
    end
)(Notification)
