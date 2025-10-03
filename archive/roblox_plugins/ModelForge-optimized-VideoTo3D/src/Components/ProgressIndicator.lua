-- ProgressIndicator: A component for showing processing progress

local Roact = require(script.Parent.Parent.Vendor.Roact)
local RoactRodux = require(script.Parent.Parent.Vendor.RoactRodux)
local Flipper = require(script.Parent.Parent.Vendor.Flipper)

local Theme = require(script.Parent.Parent.Theme)
local Icons = require(script.Parent.Parent.Utils.Icons)

local ProgressIndicator = Roact.PureComponent:extend("ProgressIndicator")

ProgressIndicator.defaultProps = {
    Size = UDim2.new(1, 0, 0, 4),
    Position = UDim2.new(0, 0, 1, -4),
    AnchorPoint = Vector2.new(0, 1),
    LayoutOrder = 1,
    
    -- Progress (0-1)
    Progress = 0,
    
    -- Optional
    ShowPercentage = true,
    ShowSpinner = true,
    ShowLabel = true,
    Label = "Processing...",
    
    -- Styling
    Theme = "dark",
    Color = nil, -- Will use accent color if not specified
    
    -- Animation
    Animate = true,
    AnimationSpeed = 1,
    
    -- Callbacks
    OnCancel = nil
}

function ProgressIndicator:init()
    -- Animation motor for indeterminate progress
    self.motor = Flipper.SingleMotor.new(0)
    self.motorBinding = Roact.createBinding(0)
    self.motor:onStep(self.motorBinding:getUpdater())
    
    -- State
    self.state = {
        isHovered = false,
        isActive = false,
        isIndeterminate = self.props.Progress == nil
    }
    
    -- Refs
    self.progressBarRef = Roact.createRef()
    self.indeterminateBarRef = Roact.createRef()
    
    -- Animation loop for indeterminate progress
    self.animationConnection = nil
end

function ProgressIndicator:didMount()
    if self.props.Animate and self.state.isIndeterminate then
        self:startIndeterminateAnimation()
    end
end

function ProgressIndicator:didUpdate(prevProps)
    -- Handle progress changes
    if self.props.Progress ~= prevProps.Progress then
        local isIndeterminate = self.props.Progress == nil
        
        if isIndeterminate ~= self.state.isIndeterminate then
            self:setState({
                isIndeterminate = isIndeterminate
            })
            
            if isIndeterminate and self.props.Animate then
                self:startIndeterminateAnimation()
            elseif not isIndeterminate and self.animationConnection then
                self.animationConnection:Disconnect()
                self.animationConnection = nil
            end
        end
    end
end

function ProgressIndicator:startIndeterminateAnimation()
    if self.animationConnection then
        self.animationConnection:Disconnect()
    end
    
    local startTime = tick()
    local duration = 2 / (self.props.AnimationSpeed or 1)
    
    self.animationConnection = game:GetService("RunService").RenderStepped:Connect(function()
        if not self.motor or self.motor._state == Flipper.MotorState.Complete then
            return
        end
        
        local elapsed = (tick() - startTime) % duration
        local progress = elapsed / duration
        
        -- Ease in-out sine function for smooth animation
        local value = -0.5 * (math.cos(math.pi * progress) - 1)
        self.motor:setGoal(Flipper.Instant.new(value))
    end)
end

function ProgressIndicator:willUnmount()
    if self.animationConnection then
        self.animationConnection:Disconnect()
        self.animationConnection = nil
    end
    
    if self.motor then
        self.motor:destroy()
    end
end

function ProgressIndicator:render()
    local theme = Theme.getTheme(self.props.Theme)
    local state = self.state
    local props = self.props
    
    -- Calculate colors
    local backgroundColor = theme.surface2
    local progressColor = props.Color or theme.accent
    local textColor = theme.textDim
    
    -- Calculate progress bar width
    local progress = math.clamp(props.Progress or 0, 0, 1)
    local progressText = string.format("%d%%", math.floor(progress * 100))
    
    -- Animation values
    local motorValue = self.motorBinding:getValue()
    
    -- Create children
    local children = {
        UICorner = Roact.createElement("UICorner", {
            CornerRadius = UDim.new(1, 0)
        }),
        
        Background = Roact.createElement("Frame", {
            Size = UDim2.new(1, 0, 1, 0),
            BackgroundColor3 = backgroundColor,
            BorderSizePixel = 0,
            ZIndex = 1
        }, {
            UICorner = Roact.createElement("UICorner", {
                CornerRadius = UDim.new(1, 0)
            })
        }),
        
        ProgressBar = Roact.createElement("Frame", {
            Size = UDim2.new(progress, 0, 1, 0),
            BackgroundColor3 = progressColor,
            BorderSizePixel = 0,
            ZIndex = 2,
            [Roact.Ref] = self.progressBarRef
        }, {
            UICorner = Roact.createElement("UICorner", {
                CornerRadius = UDim.new(1, 0)
            }),
            
            -- Shine effect
            Shine = Roact.createElement("Frame", {
                Size = UDim2.new(0.2, 0, 1, 0),
                Position = UDim2.new(progress - 0.2, 0, 0, 0),
                BackgroundColor3 = Color3.new(1, 1, 1),
                BackgroundTransparency = 0.8,
                BorderSizePixel = 0,
                ZIndex = 3
            }, {
                UICorner = Roact.createElement("UICorner", {
                    CornerRadius = UDim.new(1, 0)
                })
            })
        })
    }
    
    -- Add indeterminate animation if needed
    if state.isIndeterminate and props.Animate then
        local indeterminateWidth = 0.3
        local startPos = motorValue * (1 + indeterminateWidth) - indeterminateWidth
        
        children.IndeterminateBar = Roact.createElement("Frame", {
            Size = UDim2.new(indeterminateWidth, 0, 1, 0),
            Position = UDim2.new(startPos, 0, 0, 0),
            BackgroundColor3 = progressColor,
            BorderSizePixel = 0,
            ZIndex = 3,
            [Roact.Ref] = self.indeterminateBarRef
        }, {
            UICorner = Roact.createElement("UICorner", {
                CornerRadius = UDim.new(1, 0)
            }),
            
            -- Gradient effect
            UIGradient = Roact.createElement("UIGradient", {
                Color = ColorSequence.new({
                    ColorSequenceKeypoint.new(0, Color3.new(1, 1, 1)),
                    ColorSequenceKeypoint.new(0.5, progressColor),
                    ColorSequenceKeypoint.new(1, Color3.new(1, 1, 1))
                }),
                Transparency = NumberSequence.new({
                    NumberSequenceKeypoint.new(0, 0.3),
                    NumberSequenceKeypoint.new(0.5, 0),
                    NumberSequenceKeypoint.new(1, 0.3)
                }),
                Rotation = 15
            })
        })
    end
    
    -- Add label and percentage if needed
    if props.ShowLabel or props.ShowPercentage then
        children.LabelContainer = Roact.createElement("Frame", {
            Size = UDim2.new(1, -20, 1, 0),
            Position = UDim2.new(0, 10, 0, 0),
            BackgroundTransparency = 1,
            ZIndex = 4
        }, {
            UIListLayout = Roact.createElement("UIListLayout", {
                FillDirection = Enum.FillDirection.Horizontal,
                SortOrder = Enum.SortOrder.LayoutOrder,
                VerticalAlignment = Enum.VerticalAlignment.Center,
                Padding = UDim.new(0, 8)
            }),
            
            -- Spinner
            Spinner = props.ShowSpinner and Roact.createElement("ImageLabel", {
                Size = UDim2.new(0, 16, 0, 16),
                BackgroundTransparency = 1,
                Image = Icons.getIcon("spinner"),
                ImageColor3 = progressColor,
                LayoutOrder = 1,
                ZIndex = 5
            }, {
                -- Rotation animation
                Roact.createElement("UIAspectRatioConstraint"),
                
                Roact.createElement("UIRotation", {
                    Rotation = Roact.BindToSignal(game:GetService("RunService").RenderStepped, function()
                        return tick() * 180 % 360
                    end)
                })
            }) or nil,
            
            -- Label
            Label = props.ShowLabel and Roact.createElement("TextLabel", {
                Size = UDim2.new(0, 0, 1, 0),
                AutomaticSize = Enum.AutomaticSize.X,
                BackgroundTransparency = 1,
                Text = props.Label,
                TextColor3 = textColor,
                TextXAlignment = Enum.TextXAlignment.Left,
                TextTruncate = Enum.TextTruncate.AtEnd,
                Font = Enum.Font.SourceSans,
                TextSize = 12,
                LayoutOrder = 2,
                ZIndex = 5
            }) or nil,
            
            -- Spacer
            Spacer = Roact.createElement("Frame", {
                Size = UDim2.new(1, 0, 0, 0),
                BackgroundTransparency = 1,
                LayoutOrder = 3
            }),
            
            -- Percentage
            Percentage = props.ShowPercentage and Roact.createElement("TextLabel", {
                Size = UDim2.new(0, 40, 1, 0),
                BackgroundTransparency = 1,
                Text = state.isIndeterminate and "" or progressText,
                TextColor3 = textColor,
                TextXAlignment = Enum.TextXAlignment.Right,
                Font = Enum.Font.SourceSansSemibold,
                TextSize = 12,
                LayoutOrder = 4,
                ZIndex = 5
            }) or nil,
            
            -- Cancel button
            CancelButton = props.OnCancel and Roact.createElement("ImageButton", {
                Size = UDim2.new(0, 16, 0, 16),
                AnchorPoint = Vector2.new(0.5, 0.5),
                Position = UDim2.new(1, -8, 0.5, 0),
                BackgroundTransparency = 1,
                Image = Icons.getIcon("close"),
                ImageColor3 = textColor,
                LayoutOrder = 5,
                ZIndex = 5,
                [Roact.Event.MouseButton1Click] = props.OnCancel
            }, {
                HoverEffect = Roact.createElement("Frame", {
                    Size = UDim2.new(1, 4, 1, 4),
                    Position = UDim2.new(0, -2, 0, -2),
                    BackgroundColor3 = theme.error,
                    BackgroundTransparency = 0.9,
                    BorderSizePixel = 0,
                    ZIndex = -1,
                    Visible = state.isHovered
                }, {
                    UICorner = Roact.createElement("UICorner", {
                        CornerRadius = UDim.new(1, 0)
                    })
                })
            }) or nil
        })
    end
    
    return Roact.createElement("Frame", {
        Size = props.Size,
        Position = props.Position,
        AnchorPoint = props.AnchorPoint,
        BackgroundTransparency = 1,
        LayoutOrder = props.LayoutOrder,
        ZIndex = props.ZIndex or 1,
        
        [Roact.Event.MouseEnter] = function()
            self:setState({
                isHovered = true
            })
        end,
        
        [Roact.Event.MouseLeave] = function()
            self:setState({
                isHovered = false,
                isActive = false
            })
        end,
        
        [Roact.Event.InputBegan] = function(input)
            if input.UserInputType == Enum.UserInputType.MouseButton1 then
                self:setState({
                    isActive = true
                })
            end
        end,
        
        [Roact.Event.InputEnded] = function(input)
            if input.UserInputType == Enum.UserInputType.MouseButton1 then
                self:setState({
                    isActive = false
                })
            end
        end
    }, children)
end

return RoactRodux.connect(
    function(state, props)
        return {
            Theme = state.settings.theme or props.Theme
        }
    end
)(ProgressIndicator)
