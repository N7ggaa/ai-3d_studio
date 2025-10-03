-- FilePicker: A component for selecting files with a modern UI

local Plugin = script:FindFirstAncestorWhichIsA("Plugin")
local Components = script.Parent
local Roact = require(Components.Parent.Vendor.Roact)
local RoactRodux = require(Components.Parent.Vendor.RoactRodux)
local Flipper = require(Components.Parent.Vendor.Flipper)

local Theme = require(Components.Parent.Theme)
local Icons = require(Components.Parent.Utils.Icons)
local Path = require(Components.Parent.Utils.Path)
local Logger = require(Components.Parent.Utils.Logger)

local FilePicker = Roact.PureComponent:extend("FilePicker")

FilePicker.defaultProps = {
    AnchorPoint = Vector2.new(0, 0),
    Position = UDim2.new(0, 0, 0, 0),
    Size = UDim2.new(1, 0, 0, 100),
    LayoutOrder = 1,
    
    -- Callbacks
    OnFileSelected = function() end,
    OnError = function() end,
    
    -- Styling
    Theme = "dark",
    AccentColor = Color3.fromRGB(0, 162, 255),
    
    -- Options
    FileTypes = {
        {name = "Videos", extensions = {"mp4", "webm", "mov", "avi", "mkv"}},
        {name = "Images", extensions = {"png", "jpg", "jpeg", "webp", "bmp"}},
    },
    AllowMultiple = false,
    Title = "Select Files",
    ButtonText = "Browse Files..."
}

function FilePicker:init()
    self.motor = Flipper.GroupMotor.new({
        hover = 0,
        active = 0,
    })
    
    self.motorBinding = Roact.createBinding(self.motor:getValue())
    self.motor:onStep(function(value)
        self.motorBinding:setValue(value)
    end)
    
    -- State
    self.state = {
        isHovered = false,
        isActive = false,
        isDragging = false,
        files = {}
    }
    
    -- Refs
    self.dropZoneRef = Roact.createRef()
    
    -- Bindings
    self.hoverBinding = Roact.createBinding(0)
    self.activeBinding = Roact.createBinding(0)
    
    -- Create filter string for file dialog
    self.filterString = self:createFilterString()
end

function FilePicker:createFilterString()
    local parts = {}
    for _, filter in ipairs(self.props.FileTypes) do
        local extensions = {}
        for _, ext in ipairs(filter.extensions) do
            table.insert(extensions, string.format("*.%s", ext))
        end
        table.insert(parts, string.format("%s (%s)|%s", 
            filter.name, 
            table.concat(extensions, ","),
            table.concat(extensions, ";")
        ))
    end
    return table.concat(parts, "|\0") .. "|\0"
end

function FilePicker:didMount()
    -- Set up drag and drop
    self.dropZone = self.dropZoneRef:getValue()
    if self.dropZone then
        self.dropZone.InputBegan:Connect(function(input)
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
        end)
        
        self.dropZone.InputEnded:Connect(function(input)
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
                self:openFileDialog()
            elseif input.UserInputType == Enum.UserInputType.MouseMovement then
                self:setState({
                    isHovered = false
                })
                self.motor:setGoal({
                    hover = Flipper.Spring.new(0, {
                        frequency = 6,
                        dampingRatio = 0.7
                    })
                })
            end
        end)
        
        self.dropZone.MouseEnter:Connect(function()
            self:setState({
                isHovered = true
            })
            self.motor:setGoal({
                hover = Flipper.Spring.new(1, {
                    frequency = 6,
                    dampingRatio = 0.7
                })
            })
        end)
        
        self.dropZone.MouseLeave:Connect(function()
            self:setState({
                isHovered = false,
                isActive = false
            })
            self.motor:setGoal({
                hover = Flipper.Spring.new(0, {
                    frequency = 6,
                    dampingRatio = 0.7
                }),
                active = Flipper.Spring.new(0, {
                    frequency = 6,
                    dampingRatio = 0.7
                })
            })
        end)
        
        -- Drag and drop handling
        self.dropZone.InputBegan:Connect(function(input)
            if input.UserInputType == Enum.UserInputType.MouseMovement then
                -- Check if files are being dragged
                local userInputService = game:GetService("UserInputService")
                if userInputService:IsMouseButtonPressed(Enum.UserInputType.MouseButton1) then
                    -- Handle file drop
                    self:setState({
                        isDragging = true
                    })
                end
            end
        end)
        
        self.dropZone.InputEnded:Connect(function(input)
            if input.UserInputType == Enum.UserInputType.MouseMovement then
                self:setState({
                    isDragging = false
                })
            end
        end)
    end
end

function FilePicker:openFileDialog()
    local success, result = pcall(function()
        local fileDialog = Instance.new("FileOpenDialog")
        fileDialog.Name = "VideoTo3DFilePicker"
        fileDialog.Title = self.props.Title
        fileDialog.InitialDirectory = ""
        fileDialog.Filter = self.filterString
        fileDialog.MultiSelect = self.props.AllowMultiple
        
        -- Position the dialog near the plugin
        local pluginGui = Plugin:GetPluginGui("VideoTo3D")
        if pluginGui then
            local viewportSize = workspace.CurrentCamera.ViewportSize
            fileDialog.Position = UDim2.new(0.5, -200, 0.5, -150)
        end
        
        fileDialog.Parent = game:GetService("CoreGui")
        fileDialog.Visible = true
        
        -- Handle file selection
        fileDialog.FileSelected:Connect(function(filePath)
            self:processSelectedFiles({filePath})
        end)
        
        if self.props.AllowMultiple then
            fileDialog.FilesSelected:Connect(function(filePaths)
                self:processSelectedFiles(filePaths)
            end)
        end
        
        fileDialog.Destroying:Connect(function()
            self:setState({
                isActive = false
            })
            self.motor:setGoal({
                active = Flipper.Spring.new(0, {
                    frequency = 6,
                    dampingRatio = 0.7
                })
            })
        end)
        
        return true
    end)
    
    if not success then
        Logger.error("Failed to open file dialog:", result)
        if self.props.OnError then
            self.props.OnError("Failed to open file dialog: " .. tostring(result))
        end
    end
end

function FilePicker:processSelectedFiles(filePaths)
    local validFiles = {}
    
    for _, filePath in ipairs(filePaths) do
        -- Validate file type
        local extension = Path.getExtension(filePath):lower()
        local isValid = false
        
        for _, filter in ipairs(self.props.FileTypes) do
            for _, ext in ipairs(filter.extensions) do
                if extension == ext then
                    isValid = true
                    break
                end
            end
            if isValid then break end
        end
        
        if isValid then
            table.insert(validFiles, {
                path = filePath,
                name = Path.getFilename(filePath),
                extension = extension,
                size = Path.getSize(filePath)
            })
        end
    end
    
    if #validFiles > 0 then
        self:setState({
            files = validFiles
        })
        
        if self.props.OnFileSelected then
            if self.props.AllowMultiple then
                self.props.OnFileSelected(validFiles)
            else
                self.props.OnFileSelected(validFiles[1])
            end
        end
    else
        if self.props.OnError then
            self.props.OnError("No valid files selected")
        end
    end
end

function FilePicker:render()
    local theme = Theme.getTheme(self.props.Theme)
    local state = self.state
    local motorValues = self.motorBinding:getValue()
    
    -- Calculate colors based on state
    local backgroundColor = theme.background
    local borderColor = theme.border
    local textColor = theme.text
    
    if state.isHovered then
        backgroundColor = Color3.fromRGB(
            math.floor(backgroundColor.r * 255 * 0.9 + 25.5),
            math.floor(backgroundColor.g * 255 * 0.9 + 25.5),
            math.floor(backgroundColor.b * 255 * 0.9 + 25.5)
        )
    end
    
    if state.isActive then
        backgroundColor = Color3.fromRGB(
            math.floor(backgroundColor.r * 255 * 0.8 + 51),
            math.floor(backgroundColor.g * 255 * 0.8 + 51),
            math.floor(backgroundColor.b * 255 * 0.8 + 51)
        )
    end
    
    if state.isDragging then
        borderColor = self.props.AccentColor
        backgroundColor = Color3.fromRGB(
            math.floor(backgroundColor.r * 255 * 0.9 + 25.5),
            math.floor(backgroundColor.g * 255 * 0.9 + 25.5),
            math.floor(backgroundColor.b * 255 * 0.9 + 25.5)
        )
    end
    
    -- Create file previews
    local filePreviews = {}
    
    if #state.files > 0 then
        local maxFilesToShow = 3
        local filesToShow = self.props.AllowMultiple and math.min(maxFilesToShow, #state.files) or 1
        
        for i = 1, filesToShow do
            local file = state.files[i]
            local isImage = table.find({"png", "jpg", "jpeg", "webp", "bmp"}, file.extension:lower()) ~= nil
            
            table.insert(filePreviews, Roact.createElement("Frame", {
                Size = UDim2.new(1, -20, 0, 60),
                Position = UDim2.new(0, 10, 0, 10 + (i-1) * 70),
                BackgroundColor3 = theme.surface,
                BorderSizePixel = 0,
                ClipsDescendants = true
            }, {
                UICorner = Roact.createElement("UICorner", {
                    CornerRadius = UDim.new(0, 4)
                }),
                
                Thumbnail = isImage and Roact.createElement("ImageLabel", {
                    Size = UDim2.new(0, 50, 0, 50),
                    Position = UDim2.new(0, 5, 0.5, -25),
                    BackgroundTransparency = 1,
                    Image = "file://" .. file.path,
                    ScaleType = Enum.ScaleType.Crop,
                    ClipsDescendants = true
                }, {
                    UICorner = Roact.createElement("UICorner", {
                        CornerRadius = UDim.new(0, 4)
                    })
                }) or Roact.createElement("Frame", {
                    Size = UDim2.new(0, 50, 0, 50),
                    Position = UDim2.new(0, 5, 0.5, -25),
                    BackgroundColor3 = theme.surface2,
                    BorderSizePixel = 0
                }, {
                    UICorner = Roact.createElement("UICorner", {
                        CornerRadius = UDim.new(0, 4)
                    }),
                    
                    Icon = Roact.createElement("ImageLabel", {
                        Size = UDim2.new(0.6, 0, 0.6, 0),
                        Position = UDim2.new(0.5, 0, 0.5, 0),
                        AnchorPoint = Vector2.new(0.5, 0.5),
                        BackgroundTransparency = 1,
                        Image = Icons.getIcon("file")
                    })
                }),
                
                FileName = Roact.createElement("TextLabel", {
                    Size = UDim2.new(1, -70, 0, 20),
                    Position = UDim2.new(0, 60, 0, 10),
                    BackgroundTransparency = 1,
                    Text = file.name,
                    TextXAlignment = Enum.TextXAlignment.Left,
                    TextTruncate = Enum.TextTruncate.AtEnd,
                    TextColor3 = textColor,
                    Font = Enum.Font.SourceSansSemibold,
                    TextSize = 14
                }),
                
                FileInfo = RoElement.createElement("TextLabel", {
                    Size = UDim2.new(1, -70, 0, 16),
                    Position = UDim2.new(0, 60, 0, 34),
                    BackgroundTransparency = 1,
                    Text = string.format("%.2f MB • %s", file.size / (1024 * 1024), file.extension:upper()),
                    TextXAlignment = Enum.TextXAlignment.Left,
                    TextColor3 = theme.textDim,
                    Font = Enum.Font.SourceSans,
                    TextSize = 12
                }),
                
                RemoveButton = Roact.createElement("ImageButton", {
                    Size = UDim2.new(0, 20, 0, 20),
                    Position = UDim2.new(1, -25, 0.5, -10),
                    BackgroundTransparency = 1,
                    Image = Icons.getIcon("close"),
                    ImageColor3 = theme.textDim,
                    [Roact.Event.MouseButton1Click] = function()
                        local newFiles = table.clone(state.files)
                        table.remove(newFiles, i)
                        self:setState({
                            files = newFiles
                        })
                        
                        if self.props.OnFileSelected then
                            if self.props.AllowMultiple then
                                self.props.OnFileSelected(newFiles)
                            else
                                self.props.OnFileSelected(newFiles[1] or nil)
                            end
                        end
                    end
                }, {
                    HoverEffect = Roact.createElement("Frame", {
                        Size = UDim2.new(1, 4, 1, 4),
                        Position = UDim2.new(0, -2, 0, -2),
                        BackgroundColor3 = theme.error,
                        BackgroundTransparency = 0.9,
                        BorderSizePixel = 0,
                        ZIndex = -1
                    }, {
                        UICorner = Roact.createElement("UICorner", {
                            CornerRadius = UDim.new(1, 0)
                        })
                    })
                })
            }))
        end
        
        -- Show "+X more" if there are more files
        if #state.files > maxFilesToShow then
            table.insert(filePreviews, Roact.createElement("TextLabel", {
                Size = UDim2.new(1, -20, 0, 20),
                Position = UDim2.new(0, 10, 0, 10 + maxFilesToShow * 70),
                BackgroundTransparency = 1,
                Text = string.format("+%d more", #state.files - maxFilesToShow),
                TextColor3 = theme.textDim,
                Font = Enum.Font.SourceSans,
                TextSize = 12,
                TextXAlignment = Enum.TextXAlignment.Left
            }))
        end
    else
        -- Show drop zone when no files are selected
        table.insert(filePreviews, Roact.createElement("Frame", {
            Size = UDim2.new(1, -20, 1, -20),
            Position = UDim2.new(0, 10, 0, 10),
            BackgroundTransparency = 1
        }, {
            UIListLayout = Roact.createElement("UIListLayout", {
                SortOrder = Enum.SortOrder.LayoutOrder,
                HorizontalAlignment = Enum.HorizontalAlignment.Center,
                VerticalAlignment = Enum.VerticalAlignment.Center,
                Padding = UDim.new(0, 10)
            }),
            
            Icon = Roact.createElement("ImageLabel", {
                Size = UDim2.new(0, 40, 0, 40),
                BackgroundTransparency = 1,
                Image = Icons.getIcon("upload"),
                ImageColor3 = theme.textDim,
                LayoutOrder = 1
            }),
            
            Text = Roact.createElement("TextLabel", {
                Size = UDim2.new(1, 0, 0, 20),
                BackgroundTransparency = 1,
                Text = "Drag & drop files here or click to browse",
                TextColor3 = theme.textDim,
                Font = Enum.Font.SourceSans,
                TextSize = 14,
                TextWrapped = true,
                LayoutOrder = 2
            }),
            
            Hint = Roact.createElement("TextLabel", {
                Size = UDim2.new(1, 0, 0, 16),
                BackgroundTransparency = 1,
                Text = string.format("Supported formats: %s", self:getSupportedFormatsString()),
                TextColor3 = theme.textDim,
                Font = Enum.Font.SourceSans,
                TextSize = 12,
                TextWrapped = true,
                LayoutOrder = 3
            })
        }))
    end
    
    return Roact.createElement("Frame", {
        Size = self.props.Size,
        Position = self.props.Position,
        AnchorPoint = self.props.AnchorPoint,
        BackgroundTransparency = 1,
        LayoutOrder = self.props.LayoutOrder,
        ZIndex = self.props.ZIndex or 1
    }, {
        DropZone = Roact.createElement("TextButton", {
            Size = UDim2.new(1, 0, 1, 0),
            BackgroundColor3 = backgroundColor,
            BorderColor3 = borderColor,
            BorderSizePixel = 1,
            Text = "",
            AutoButtonColor = false,
            [Roact.Ref] = self.dropZoneRef,
            [Roact.Event.Activated] = function()
                self:openFileDialog()
            end
        }, {
            UICorner = Roact.createElement("UICorner", {
                CornerRadius = UDim.new(0, 4)
            }),
            
            UIPadding = Roact.createElement("UIPadding", {
                PaddingTop = UDim.new(0, 10),
                PaddingBottom = UDim.new(0, 10),
                PaddingLeft = UDim.new(0, 10),
                PaddingRight = UDim.new(0, 10)
            }),
            
            UIListLayout = Roact.createElement("UIListLayout", {
                SortOrder = Enum.SortOrder.LayoutOrder,
                HorizontalAlignment = Enum.HorizontalAlignment.Center,
                VerticalAlignment = Enum.VerticalAlignment.Top,
                Padding = UDim.new(0, 10)
            }),
            
            -- File previews
            table.unpack(filePreviews)
        }),
        
        -- Border highlight on hover/active
        BorderHighlight = Roact.createElement("UIStroke", {
            Color = self.props.AccentColor,
            Transparency = 1 - (state.isHovered and 0.5 or 0) - (state.isActive and 0.5 or 0),
            Thickness = 2,
            ApplyStrokeMode = Enum.ApplyStrokeMode.Border
        })
    })
end

function FilePicker:getSupportedFormatsString()
    local extensions = {}
    for _, filter in ipairs(self.props.FileTypes) do
        for _, ext in ipairs(filter.extensions) do
            table.insert(extensions, string.upper(ext))
        end
    end
    
    return table.concat(extensions, ", ")
end

return RoactRodux.connect(
    function(state, props)
        return {
            Theme = state.settings.theme or props.Theme
        }
    end
)(FilePicker)
