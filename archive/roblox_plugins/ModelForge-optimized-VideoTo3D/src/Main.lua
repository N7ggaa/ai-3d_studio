-- Main module for the VideoTo3D plugin

local Plugin = script.Parent.Parent

-- Services
local HttpService = game:GetService("HttpService")
local ContentProvider = game:GetService("ContentProvider")
local RunService = game:GetService("RunService")
local Selection = game:GetService("Selection")
local TweenService = game:GetService("TweenService")

-- Vendor
local Roact = require(script.Parent.Vendor.Roact)
local RoactRodux = require(script.Parent.Vendor.RoactRodux)
local Flipper = require(script.Parent.Vendor.Flipper)

-- Config
local Config = require(script.Parent.Config)
local Theme = require(script.Parent.Theme)

-- Utils
local Logger = require(script.Parent.Utils.Logger)
local Utils = require(script.Parent.Utils.Utils)
local Icons = require(script.Parent.Utils.Icons)
local Path = require(script.Parent.Utils.Path)

-- Services
local VideoProcessor = require(script.Parent.Services.VideoProcessor)
local ModelGenerator = require(script.Parent.Services.ModelGenerator)
local AssetImporter = require(script.Parent.Services.AssetImporter)
local NotificationService = require(script.Parent.Services.NotificationService)

-- Components
local FilePicker = require(script.Parent.Components.FilePicker)
local ProgressIndicator = require(script.Parent.Components.ProgressIndicator)

-- Store
local Store = require(script.Parent.Store)

local Main = {}
Main.__index = Main

-- Create a new instance of the Main module
function Main.new(toolbar, pluginWidget)
    local self = setmetatable({}, Main)
    
    -- Services
    self.logger = Logger.new("Main")
    self.store = Store
    self.notificationService = NotificationService.new(self.store)
    
    -- Initialize services with store and notification service
    self.videoProcessor = VideoProcessor.new({
        store = self.store,
        notificationService = self.notificationService
    })
    
    self.modelGenerator = ModelGenerator.new({
        store = self.store,
        notificationService = self.notificationService
    })
    
    self.assetImporter = AssetImporter.new(nil, {
        store = self.store,
        notificationService = self.notificationService,
        tempDir = Path.join(Path.getTempDir(), "VideoTo3D")
    })
    
    -- UI
    self.toolbar = toolbar
    self.pluginWidget = pluginWidget
    self.widget = nil
    
    -- State
    self.isEnabled = false
    self.isProcessing = false
    self.currentVideo = nil
    self.currentFrames = {}
    self.generatedModel = nil
    
    -- Initialize the plugin
    self:init()
    
    self.logger:info("Plugin initialized")
    return self
end

-- Initialize the plugin
function Main:init()
    self.logger:info("Initializing VideoTo3D plugin")
    
    -- Create the toolbar button
    self.toggleButton = self.toolbar:CreateButton(
        "VideoTo3D",
        "Convert videos to 3D models",
        Icons.getIcon("film")
    )
    
    -- Connect the button click event
    self.toggleButton.Click:Connect(function()
        self:toggle()
    end)
    
    -- Create the widget
    self:createWidget()
    
    -- Connect plugin unload event
    self.plugin.Unloading:Connect(function()
        self:destroy()
    end)
    
    -- Show welcome notification
    task.delay(1, function()
        self.notificationService:info("Welcome to VideoTo3D! Click 'Select Video' to get started.")
    end)
end

-- Create the plugin widget using Roact
function Main:createWidget()
    -- Create the main widget
    self.widget = plugin:CreateDockWidgetPluginGui(
        "VideoTo3D",
        DockWidgetPluginGuiInfo.new(
            Enum.InitialDockState.Float,
            true,
            false,
            400,
            600,
            300,
            300
        )
    )
    self.widget.Title = "VideoTo3D"
    self.widget.Name = "VideoTo3D"
    self.widget.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    
    -- Create the root component
    local function App()
        local theme = Theme.getTheme(self.store:getState().settings.theme or "dark")
        
        return Roact.createElement("Frame", {
            Size = UDim2.new(1, 0, 1, 0),
            BackgroundColor3 = theme.background,
            BorderSizePixel = 0
        }, {
            -- Main layout
            UIListLayout = Roact.createElement("UIListLayout", {
                SortOrder = Enum.SortOrder.LayoutOrder,
                HorizontalAlignment = Enum.HorizontalAlignment.Center,
                Padding = UDim.new(0, 10)
            }),
            
            -- Header
            Header = Roact.createElement("Frame", {
                Size = UDim2.new(1, 0, 0, 60),
                BackgroundTransparency = 1,
                LayoutOrder = 1
            }, {
                Title = Roact.createElement("TextLabel", {
                    Size = UDim2.new(1, -40, 1, 0),
                    Position = UDim2.new(0, 40, 0, 0),
                    BackgroundTransparency = 1,
                    Text = "VIDEO TO 3D",
                    TextColor3 = theme.text,
                    TextSize = 18,
                    Font = Enum.Font.GothamBold,
                    TextXAlignment = Enum.TextXAlignment.Left,
                    TextYAlignment = Enum.TextYAlignment.Center
                }),
                
                Logo = Roact.createElement("ImageLabel", {
                    Size = UDim2.new(0, 32, 0, 32),
                    Position = UDim2.new(0, 10, 0.5, -16),
                    BackgroundTransparency = 1,
                    Image = Icons.getIcon("videotothree"),
                    ImageColor3 = theme.accent
                })
            }),
            
            -- Divider
            Divider = Roact.createElement("Frame", {
                Size = UDim2.new(1, -20, 0, 1),
                BackgroundColor3 = theme.divider,
                BorderSizePixel = 0,
                LayoutOrder = 2
            }),
            
            -- Content
            Content = Roact.createElement("ScrollingFrame", {
                Size = UDim2.new(1, 0, 1, -200),
                BackgroundTransparency = 1,
                BorderSizePixel = 0,
                ScrollBarThickness = 6,
                ScrollBarImageColor3 = theme.scrollbar,
                ScrollBarImageTransparency = 0.5,
                CanvasSize = UDim2.new(0, 0, 0, 0),
                AutomaticCanvasSize = Enum.AutomaticSize.Y,
                LayoutOrder = 3
            }, {
                UIListLayout = Roact.createElement("UIListLayout", {
                    SortOrder = Enum.SortOrder.LayoutOrder,
                    HorizontalAlignment = Enum.HorizontalAlignment.Center,
                    Padding = UDim.new(0, 10)
                }),
                
                -- File Picker
                FilePicker = Roact.createElement(FilePicker, {
                    Size = UDim2.new(1, -20, 0, 120),
                    LayoutOrder = 1,
                    FileTypes = {
                        {name = "Videos", extensions = {"mp4", "webm", "mov", "avi"}},
                        {name = "Images", extensions = {"png", "jpg", "jpeg", "webp"}},
                    },
                    AllowMultiple = false,
                    OnFileSelected = function(files)
                        self:onFileSelected(files)
                    end,
                    OnError = function(errorMessage)
                        self.notificationService:error(errorMessage)
                    end
                })
            })
        })
    end
    
    -- Mount the Roact tree
    self.roactHandle = Roact.mount(Roact.createElement(App), self.widget)
    
    -- Connect to store changes
    self.storeConnection = self.store.changed:connect(function(newState, oldState)
        -- Re-render when theme changes
        if newState.settings.theme ~= (oldState and oldState.settings.theme) then
            self.roactHandle = Roact.update(self.roactHandle, Roact.createElement(App))
        end
    end)
end

-- Toggle the plugin window
-- Toggle the plugin window
function Main:toggle()
    if self.widget then
        self.widget.Enabled = not self.widget.Enabled
    end
end

-- Handle file selection from the file picker
function Main:onFileSelected(files)
    if not files or #files == 0 then return end
    
    -- For now, just take the first file if multiple are selected
    local filePath = files[1]
    self.currentVideo = filePath
    
    -- Show success message
    self.notificationService:success("Selected: " .. Path.getFileName(filePath))
    
    -- Update the UI state
    self.store:dispatch({
        type = "SET_SELECTED_FILE",
        payload = {
            path = filePath,
            name = Path.getFileName(filePath),
            size = Path.getSize(filePath),
            type = Path.getExtension(filePath):lower()
        }
    })
end

-- Process the selected video
function Main:processVideo()
    if not self.currentVideo or self.isProcessing then return end
    
    self.isProcessing = true
    self.store:dispatch({ type = "SET_PROCESSING", payload = true })
    
    -- Show progress notification
    local notificationId = self.notificationService:info("Processing video...", {
        duration = 0, -- Don't auto-dismiss
        showProgress = true
    })
    
    -- Process in a separate thread
    task.spawn(function()
        local success, result = pcall(function()
            -- Step 1: Extract frames
            self:updateProgress(notificationId, "Extracting frames...", 0.2)
            
            local frames = self.videoProcessor:extractFrames(self.currentVideo, {
                maxFrames = 30, -- First 30 seconds at 1 FPS
                resolution = Vector2.new(512, 512),
                onProgress = function(progress, message)
                    self:updateProgress(notificationId, message, 0.2 + progress * 0.3)
                end
            })
            
            if not frames or #frames == 0 then
                error("Failed to extract frames from video")
            end
            
            self.currentFrames = frames
            
            -- Step 2: Generate 3D model
            self:updateProgress(notificationId, "Generating 3D model...", 0.6)
            
            local model = self.modelGenerator:generateModel(frames, {
                resolution = 128,
                smoothness = 0.5,
                onProgress = function(progress, message)
                    self:updateProgress(notificationId, message, 0.6 + progress * 0.4)
                end
            })
            
            if not model then
                error("Failed to generate 3D model")
            end
            
            self.generatedModel = model
            
            -- Step 3: Position and add to workspace
            local camera = workspace.CurrentCamera
            if camera then
                local position = camera.CFrame.Position + (camera.CFrame.LookVector * 10)
                model:SetPrimaryPartCFrame(CFrame.new(position))
            end
            
            model.Parent = workspace
            Selection:Set({model})
            
            -- Show success message
            self.notificationService:success("3D model generated successfully!")
            
            return true
        end)
        
        -- Clean up
        self.isProcessing = false
        self.store:dispatch({ type = "SET_PROCESSING", payload: false })
        
        -- Update notification
        if success then
            self.notificationService:update(notificationId, {
                message = "Processing complete!",
                type = "success",
                duration = 5
            })
        else
            self.notificationService:update(notificationId, {
                message = "Error: " .. tostring(result),
                type = "error",
                duration = 10
            })
            self.logger:error("Video processing failed: " .. tostring(result))
        end
    end)
end

-- Update progress notification
function Main:updateProgress(id, message, progress)
    if not id then return end
    
    self.notificationService:update(id, {
        message = message,
        progress = progress
    })
end

-- Clean up resources
function Main:cleanup()
    -- Clean up frames
    if self.currentFrames then
        for _, frame in ipairs(self.currentFrames) do
            if frame:IsA("BasePart") then
                frame:Destroy()
            end
        end
        self.currentFrames = {}
    end
    
    -- Clean up generated model
    if self.generatedModel and self.generatedModel.Parent then
        self.generatedModel:Destroy()
        self.generatedModel = nil
    end
    
    -- Reset state
    self.currentVideo = nil
    self.isProcessing = false
    
    -- Update store
    self.store:dispatch({ type = "RESET_STATE" })
end

-- Destroy the plugin
function Main:destroy()
    self.logger:info("Destroying VideoTo3D plugin")
    
    -- Clean up resources
    self:cleanup()
    
    -- Disconnect store connection
    if self.storeConnection then
        self.storeConnection:disconnect()
        self.storeConnection = nil
    end
    
    -- Unmount Roact tree
    if self.roactHandle then
        Roact.unmount(self.roactHandle)
        self.roactHandle = nil
    end
    
    -- Remove the widget
    if self.widget then
        self.widget:Destroy()
        self.widget = nil
    end
    
    -- Remove the toolbar button
    if self.toggleButton then
        self.toggleButton:Destroy()
        self.toggleButton = nil
    end
    
    -- Clean up services
    if self.videoProcessor then
        self.videoProcessor:destroy()
        self.videoProcessor = nil
    end
    
    if self.modelGenerator then
        self.modelGenerator:destroy()
        self.modelGenerator = nil
    end
    
    if self.assetImporter then
        self.assetImporter:destroy()
        self.assetImporter = nil
    end
    
    if self.notificationService then
        self.notificationService:destroy()
        self.notificationService = nil
    end
    
    self.logger:info("Plugin destroyed")
end
-- Process video with custom options
function Main:processVideoWithOptions(url, prompt, options)
    -- Merge default options with provided options
    local processOptions = {
        maxFrames = options.maxFrames or 30,
        resolution = options.resolution or Vector2.new(512, 512),
        voxelResolution = options.voxelResolution or 128,
        smoothness = options.smoothness or 0.5,
        simplifyMesh = options.simplifyMesh ~= false -- Default to true
    }
    
    -- Set the current video and process it
    self.currentVideo = url
    self:processVideo(processOptions)
end

-- Apply a template to the model generation
function Main:applyTemplate(template)
    if not template then return end
    
    -- Update the store with template settings
    self.store:dispatch({
        type = "APPLY_TEMPLATE",
        payload = template
    })
    
    -- If we have a video, reprocess it with the new template
    if self.currentVideo then
        self:processVideo()
    else {
        self.notificationService:info("Template applied. Select a video to see the changes.")
    }
end

-- Connect the process button in the UI
function Main:connectProcessButton(button)
    if not button then return end
    
    button.MouseButton1Click:Connect(function()
        if not self.currentVideo then
            self.notificationService:warning("Please select a video first!")
            return
        end
        
        -- Get current settings from the store
        local state = self.store:getState()
        
        -- Process with current settings
        self:processVideoWithOptions(self.currentVideo, nil, {
            maxFrames = state.settings.maxFrames,
            resolution = state.settings.resolution,
            voxelResolution = state.settings.voxelResolution,
            smoothness = state.settings.smoothness,
            simplifyMesh = state.settings.simplifyMesh
        })
    end)
end

-- Initialize the plugin UI
function Main:initUI()
    -- Create the main UI components
    local theme = Theme.getTheme("dark") -- Default to dark theme
    
    -- Create the main frame
    local mainFrame = Instance.new("Frame")
    mainFrame.Name = "MainFrame"
    mainFrame.Size = UDim2.new(1, 0, 1, 0)
    mainFrame.BackgroundColor3 = theme.background
    mainFrame.BorderSizePixel = 0
    
    -- Add UI components here (file picker, options, process button, etc.)
    -- This is a simplified version - in a real implementation, you would use Roact components
    
    -- Return the main frame
    return mainFrame
end
        self:toggle()
    end)
    
    -- Handle plugin deactivation
    self.plugin.Deactivation:Connect(function()
        self:onDeactivated()
    end)
    
    self.isEnabled = true
end

-- Clean up resources
function Main:cleanup()
    self.logger:info("Cleaning up resources")
    
    -- Clean up services
    if self.videoProcessor then
        self.videoProcessor:cleanup()
    end
    
    if self.modelGenerator then
        self.modelGenerator:cleanup()
    end
    
    -- Clean up UI
    if self.widget then
        self.widget:Destroy()
        self.widget = nil
    end
    
    if self.toggleButton then
        self.toggleButton:Destroy()
        self.toggleButton = nil
    end
    
    if self.toolbar then
        self.toolbar:Destroy()
        self.toolbar = nil
    end
    
    self.isEnabled = false
    self.logger:info("Cleanup complete")
end

-- Toggle the plugin UI
function Main:toggle()
    if self.widget:IsVisible() then
        self.widget:Hide()
    else
        self.widget:Show()
    end
end

-- Process a video URL
function Main:processVideo(url, prompt, options)
    self.logger:info("Processing video:", url)
    
    -- Validate input
    if not url or url == "" then
        local errorMsg = "Please enter a video URL"
        self.logger:error(errorMsg)
        return {
            success = false,
            message = errorMsg
        }
    end
    
    -- Merge options with defaults
    local processingOptions = {
        frameRate = options.frameRate or 1,
        maxDuration = options.duration or 30,
        quality = options.quality or 0.8,
        preset = options.preset or "default"
    }
    
    -- Process the video using VideoProcessor
    local processResult = self.videoProcessor:processFromUrl(url, processingOptions)
    
    if not processResult or not processResult.success then
        local errorMsg = processResult and processResult.error or "Failed to process video"
        self.logger:error("Video processing failed:", errorMsg)
        return {
            success = false,
            message = errorMsg,
            details = processResult and processResult.details
        }
    end
    
    -- Prepare model generation options
    local modelOptions = {
        style = options.style or "standard",
        quality = options.quality or 0.8,
        generateCollision = options.generateCollision ~= false,
        mergeParts = options.mergeParts ~= false,
        frameSelection = options.frameSelection or "keyframes"
    }
    
    -- Generate the 3D model
    local model = self.modelGenerator:generateModel(processResult.frames, modelOptions)
    
    if not model then
        local errorMsg = "Failed to generate 3D model"
        self.logger:error(errorMsg)
        return {
            success = false,
            message = errorMsg
        }
    end
    
    -- Set model name and position
    model.Name = "VideoModel_" .. os.date("%Y%m%d_%H%M%S")
    
    -- Add prompt as a model attribute
    if prompt and prompt ~= "" then
        model:SetAttribute("Prompt", prompt)
    end
    
    -- Position the model in the workspace
    local primaryPart = model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart")
    if primaryPart then
        -- Position in front of the camera if possible
        local camera = workspace.CurrentCamera
        if camera then
            local cameraCF = camera.CFrame
            local position = cameraCF.Position + cameraCF.LookVector * 20
            position = Vector3.new(position.X, 5, position.Z) -- Keep at ground level
            model:SetPrimaryPartCFrame(CFrame.new(position))
        else
            -- Fallback position
            model:SetPrimaryPartCFrame(CFrame.new(0, 10, 0))
        end
    end
    
    -- Add to workspace
    model.Parent = workspace
    
    self.logger:info("Successfully generated 3D model:", model.Name)
    return {
        success = true,
        message = "Successfully created 3D model",
        model = model,
        metadata = processResult.metadata
    }
end

-- Apply a template
function Main:applyTemplate(template)
    if not template then
        return {
            success = false,
            message = "No template provided"
        }
    end
    
    -- In a real implementation, this would apply the template settings
    return {
        success = true,
        message = "Applied template: " .. template.name,
        settings = template.settings or {}
    }
end

-- Handle plugin deactivation
function Main:onDeactivated()
    if self.widget then
        self.widget:Hide()
    end
    self.isEnabled = false
end

return Main
