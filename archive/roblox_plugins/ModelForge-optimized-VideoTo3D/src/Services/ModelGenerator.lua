-- ModelGenerator Service
-- Handles 3D model generation from video frames

local Config = require(script.Parent.Parent.Config)
local Logger = require(script.Parent.Logger)

local ModelGenerator = {}
ModelGenerator.__index = ModelGenerator

-- Constants
local DEFAULT_OPTIONS = {
    style = "standard",           -- "standard", "voxel", "low_poly"
    quality = 0.8,               -- 0.0 to 1.0
    generateCollision = true,    -- Whether to generate collision meshes
    optimize = true,             -- Whether to optimize the model
    textureAtlas = true,         -- Whether to use texture atlases
    maxTriangles = 10000,        -- Maximum triangles in the model
    scale = 1.0,                 -- Scale of the model
    mergeParts = true,           -- Whether to merge parts where possible
    smoothNormals = true,        -- Whether to smooth normals
    generateUVs = true,          -- Whether to generate UVs
    preserveAspectRatio = true,  -- Whether to preserve aspect ratio
    frameSelection = "keyframes"  -- "all", "keyframes", "spaced"
}

-- Initialize a new ModelGenerator
function ModelGenerator.new()
    local self = setmetatable({}, ModelGenerator)
    
    -- Initialize services
    self.logger = Logger.new("ModelGenerator")
    
    -- Initialize caches
    self.modelCache = {}
    self.textureCache = {}
    self.materialCache = {}
    
    -- Initialize random seed for consistent results
    math.randomseed(os.time())
    
    return self
end

-- Generate a 3D model from video frames
-- @param frames table: Table of frame data from VideoProcessor
-- @param options table: Generation options (optional)
-- @return Model: The generated 3D model
function ModelGenerator:generateModel(frames, options)
    self.logger:info("Generating 3D model from", #frames, "frames")
    
    -- Validate input
    if not frames or #frames == 0 then
        return self.logger:error("No frames provided for model generation")
    end
    
    -- Merge options with defaults
    options = self:_mergeOptions(options)
    
    -- Create a new model
    local model = Instance.new("Model")
    model.Name = string.format("VideoModel_%s_%d", os.date("%Y%m%d_%H%M%S"), #frames)
    
    -- Process frames based on selection mode
    local processedFrames = self:_processFrames(frames, options)
    
    -- Generate model based on style
    if options.style == "voxel" then
        self:_generateVoxelModel(model, processedFrames, options)
    elseif options.style == "low_poly" then
        self:_generateLowPolyModel(model, processedFrames, options)
    else
        self:_generateStandardModel(model, processedFrames, options)
    end
    
    -- Generate collision meshes if requested
    if options.generateCollision then
        self:_generateCollisionMeshes(model, options)
    end
    
    -- Optimize the model if requested
    if options.optimize then
        self:_optimizeModel(model, options)
    end
    
    -- Set model primary part
    if #model:GetChildren() > 0 then
        model.PrimaryPart = model:FindFirstChildWhichIsA("BasePart")
    end
    
    self.logger:info("Model generation complete")
    return model
end

-- Merge user options with defaults
function ModelGenerator:_mergeOptions(userOptions)
    local options = {}
    
    -- Apply defaults
    for k, v in pairs(DEFAULT_OPTIONS) do
        options[k] = v
    end
    
    -- Apply user options
    if userOptions then
        for k, v in pairs(userOptions) do
            if v ~= nil then  -- Only override if not nil
                options[k] = v
            end
        end
    end
    
    return options
end

-- Process frames based on selection mode
function ModelGenerator:_processFrames(frames, options)
    local processedFrames = {}
    
    if options.frameSelection == "keyframes" then
        -- Only use keyframes
        for _, frame in ipairs(frames) do
            if frame.isKeyframe then
                table.insert(processedFrames, frame)
            end
        end
        
        -- If no keyframes found, use first and last frame
        if #processedFrames == 0 and #frames > 0 then
            table.insert(processedFrames, frames[1])
            if #frames > 1 then
                table.insert(processedFrames, frames[#frames])
            end
        end
    elseif options.frameSelection == "spaced" then
        -- Evenly space frames (max 10 frames)
        local step = math.max(1, math.floor(#frames / 10))
        for i = 1, #frames, step do
            table.insert(processedFrames, frames[i])
        end
    else
        -- Use all frames
        processedFrames = frames
    end
    
    self.logger:debug("Selected", #processedFrames, "frames for model generation")
    return processedFrames
end

-- Generate a standard model from frames
function ModelGenerator:_generateStandardModel(model, frames, options)
    self.logger:debug("Generating standard model with", #frames, "frames")
    
    local basePosition = Vector3.new(0, 10, 0)
    local spacing = 5
    local totalWidth = (#frames - 1) * spacing
    local startX = -totalWidth / 2
    
    for i, frame in ipairs(frames) do
        -- Create a part for this frame
        local part = Instance.new("Part")
        part.Name = string.format("Frame_%03d", i)
        part.Anchored = true
        part.CanCollide = true
        part.Material = Enum.Material.Neon
        part.Color = Color3.fromRGB(255, 255, 255)
        part.Size = Vector3.new(4, 2.25, 0.1)  -- 16:9 aspect ratio
        part.Position = basePosition + Vector3.new(startX + (i-1) * spacing, 0, 0)
        part.Parent = model
        
        -- Create a decal for the frame image
        local decal = Instance.new("Decal")
        decal.Name = "FrameTexture"
        decal.Texture = frame.image or "rbxassetid://6031075926"  -- Default placeholder
        decal.Face = Enum.NormalId.Front
        decal.Parent = part
        
        -- Add frame info as attributes
        part:SetAttribute("FrameIndex", i)
        part:SetAttribute("Timestamp", frame.timestamp or i)
        part:SetAttribute("IsKeyframe", frame.isKeyframe or false)
        
        -- Add click detector for interaction
        local clickDetector = Instance.new("ClickDetector")
        clickDetector.Parent = part
        
        -- Store frame data for potential use
        part:SetAttribute("FrameData", frame.data or "")
    end
    
    self.logger:debug("Generated standard model with", #model:GetChildren(), "parts")
end

-- Generate a voxel-style model from frames
function ModelGenerator:_generateVoxelModel(model, frames, options)
    self.logger:debug("Generating voxel model with", #frames, "frames")
    
    local basePosition = Vector3.new(0, 10, 0)
    local spacing = 5
    local totalWidth = (#frames - 1) * spacing
    local startX = -totalWidth / 2
    
    for i, frame in ipairs(frames) do
        -- Create a base part for this frame
        local part = Instance.new("Part")
        part.Name = string.format("VoxelFrame_%03d", i)
        part.Anchored = true
        part.CanCollide = true
        part.Material = Enum.Material.Neon
        part.Color = Color3.fromRGB(255, 255, 255)
        part.Size = Vector3.new(2, 2, 2)  -- Base cube size
        part.Position = basePosition + Vector3.new(startX + (i-1) * spacing, 0, 0)
        part.Parent = model
        
        -- Add a decal for the frame image
        local decal = Instance.new("Decal")
        decal.Name = "FrameTexture"
        decal.Texture = frame.image or "rbxassetid://6031075926"
        decal.Face = Enum.NormalId.Front
        decal.Parent = part
        
        -- Add frame info as attributes
        part:SetAttribute("FrameIndex", i)
        part:SetAttribute("Timestamp", frame.timestamp or i)
        part:SetAttribute("IsKeyframe", frame.isKeyframe or false)
        
        -- Add click detector for interaction
        local clickDetector = Instance.new("ClickDetector")
        clickDetector.Parent = part
    end
    
    self.logger:debug("Generated voxel model with", #model:GetChildren(), "parts")
end

-- Generate a low-poly model from frames
function ModelGenerator:_generateLowPolyModel(model, frames, options)
    self.logger:debug("Generating low-poly model with", #frames, "frames")
    
    local basePosition = Vector3.new(0, 10, 0)
    local spacing = 5
    local totalWidth = (#frames - 1) * spacing
    local startX = -totalWidth / 2
    
    for i, frame in ipairs(frames) do
        -- Create a wedge part for a low-poly look
        local part = Instance.new("WedgePart")
        part.Name = string.format("LowPolyFrame_%03d", i)
        part.Anchored = true
        part.CanCollide = true
        part.Material = Enum.Material.Neon
        part.Color = Color3.fromRGB(200, 200, 200)
        part.Size = Vector3.new(3, 2, 1.5)
        part.Position = basePosition + Vector3.new(startX + (i-1) * spacing, 0, 0)
        part.Orientation = Vector3.new(0, (i % 2) * 180, 0)  -- Alternate orientation
        part.Parent = model
        
        -- Add a decal for the frame image
        local decal = Instance.new("Decal")
        decal.Name = "FrameTexture"
        decal.Texture = frame.image or "rbxassetid://6031075926"
        decal.Face = Enum.NormalId.Front
        decal.Parent = part
        
        -- Add frame info as attributes
        part:SetAttribute("FrameIndex", i)
        part:SetAttribute("Timestamp", frame.timestamp or i)
        part:SetAttribute("IsKeyframe", frame.isKeyframe or false)
        
        -- Add click detector for interaction
        local clickDetector = Instance.new("ClickDetector")
        clickDetector.Parent = part
    end
    
    self.logger:debug("Generated low-poly model with", #model:GetChildren(), "parts")
end

-- Generate collision meshes for the model
-- @param model Model: The model to generate collision for
-- @param options table: Generation options
function ModelGenerator:_generateCollisionMeshes(model, options)
    self.logger:debug("Generating collision meshes for model")
    
    -- In a real implementation, this would generate simplified collision geometry
    -- For now, we'll just enable collisions on all parts
    for _, part in ipairs(model:GetDescendants()) do
        if part:IsA("BasePart") then
            part.CanCollide = true
            part.CollisionGroup = "Default"
        end
    end
    
    self.logger:debug("Generated collision meshes")
end

-- Optimize the generated model
-- @param model Model: The model to optimize
-- @param options table: Optimization options
function ModelGenerator:_optimizeModel(model, options)
    self.logger:debug("Optimizing model")
    
    -- Only optimize if there are parts to optimize
    local parts = {}
    for _, part in ipairs(model:GetDescendants()) do
        if part:IsA("BasePart") then
            table.insert(parts, part)
        end
    end
    
    if #parts == 0 then
        self.logger:debug("No parts to optimize")
        return
    end
    
    -- Apply optimization based on options
    if options.mergeParts then
        self:_mergeParts(model, parts, options)
    end
    
    -- Apply LOD (Level of Detail) if needed
    if options.quality < 0.5 then
        self:_reduceDetail(model, options)
    end
    
    self.logger:debug("Model optimization complete")
end

-- Merge parts where possible to reduce draw calls
-- @param model Model: The model containing parts to merge
-- @param parts table: Table of parts to consider for merging
-- @param options table: Merge options
function ModelGenerator:_mergeParts(model, parts, options)
    self.logger:debug("Merging parts")
    
    -- In a real implementation, this would use CSG or other techniques to merge parts
    -- For now, we'll just group parts that are close together
    local MERGE_DISTANCE = 2.0
    local mergedParts = {}
    
    for i, part1 in ipairs(parts) do
        if not mergedParts[part1] then
            local toMerge = {part1}
            
            -- Find parts close to part1
            for j = i + 1, #parts do
                local part2 = parts[j]
                if not mergedParts[part2] then
                    local distance = (part1.Position - part2.Position).Magnitude
                    if distance < MERGE_DISTANCE then
                        table.insert(toMerge, part2)
                        mergedParts[part2] = true
                    end
                end
            end
            
            -- If we found parts to merge, group them
            if #toMerge > 1 then
                local group = Instance.new("Model")
                group.Name = "MergedGroup_" .. #model:GetChildren()
                
                for _, part in ipairs(toMerge) do
                    part.Parent = group
                end
                
                group.Parent = model
            end
            
            mergedParts[part1] = true
        end
    end
    
    self.logger:debug("Merged", #parts - #model:GetChildren(), "parts")
end

-- Reduce detail of the model
-- @param model Model: The model to reduce detail for
-- @param options table: Detail reduction options
function ModelGenerator:_reduceDetail(model, options)
    self.logger:debug("Reducing model detail")
    
    -- In a real implementation, this would use mesh simplification algorithms
    -- For now, we'll just reduce the number of parts based on quality
    local targetCount = math.max(1, math.floor(#model:GetChildren() * options.quality))
    
    while #model:GetChildren() > targetCount do
        local part = model:FindFirstChildOfClass("BasePart")
        if part then
            part:Destroy()
        else
            break
        end
    end
    
    self.logger:debug("Reduced model to", #model:GetChildren(), "parts")
end

-- Clean up resources
function ModelGenerator:cleanup()
    self.modelCache = {}
    self.textureCache = {}
    self.materialCache = {}
    self.logger:debug("Cleaned up resources")
end
            info.Size = UDim2.new(2, 0, 0.5, 0)
            info.StudsOffset = Vector3.new(0, 2, 0)
            info.Adornee = part
            
            local label = Instance.new("TextLabel")
            label.Size = UDim2.new(1, 0, 1, 0)
            label.BackgroundTransparency = 1
            label.Text = string.format("Frame %d\n%.1fs", i, frame.timestamp or 0)
            label.TextColor3 = Color3.new(1, 1, 1)
            label.TextScaled = true
            label.Parent = info
            info.Parent = part
            
            part.Parent = model
        end
    end
end

-- Generate a voxel-style model
function ModelGenerator:_generateVoxelModel(model, frames, options)
    self.logger:debug("Generating voxel model")
    
    -- This is a placeholder implementation
    -- In a real implementation, this would use voxel-based reconstruction
    
    local basePosition = Vector3.new(0, 5, 0)
    local size = 10
    local voxelSize = 1
    
    -- Create a simple voxel grid
    for x = 1, size do
        for y = 1, size do
            for z = 1, size do
                -- Simple noise function for demonstration
                local density = math.noise(x/5, y/5, z/5)
                
                if density > 0.3 then
                    local part = Instance.new("Part")
                    part.Name = string.format("Voxel_%d_%d_%d", x, y, z)
                    part.Size = Vector3.new(voxelSize, voxelSize, voxelSize)
                    part.Position = basePosition + Vector3.new(x, y, z) * voxelSize
                    part.Anchored = true
                    part.Material = Enum.Material.Neon
                    part.Color = Color3.fromHSV(density, 1, 1)
                    part.Parent = model
                end
            end
        end
    end
end

-- Generate collision meshes for the model
function ModelGenerator:_generateCollisionMeshes(model)
    self.logger:debug("Generating collision meshes")
    
    -- This is a placeholder implementation
    -- In a real implementation, this would generate simplified collision geometry
    
    for _, part in ipairs(model:GetDescendants()) do
        if part:IsA("BasePart") then
            -- Simple collision approximation
            local collision = part:Clone()
            collision.Name = part.Name .. "_Collision"
            collision.Transparency = 0.9
            collision.CanCollide = true
            collision.Anchored = false
            collision.Parent = part.Parent
        end
    end
end

-- Optimize the model for Roblox
function ModelGenerator:_optimizeModel(model, options)
    self.logger:debug("Optimizing model")
    
    -- This is a placeholder implementation
    -- In a real implementation, this would:
    -- 1. Merge parts where possible
    -- 2. Optimize textures
    -- 3. Reduce polygon count
    -- 4. Apply LOD (Level of Detail)
    
    -- For now, just set some basic properties
    model.PrimaryPart = model:FindFirstChildWhichIsA("BasePart") or model:GetChildren()[1]
end

-- Clean up resources
function ModelGenerator:cleanup()
    self.modelCache = {}
end

return ModelGenerator
