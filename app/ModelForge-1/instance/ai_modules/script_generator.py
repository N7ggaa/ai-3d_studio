import os
import logging
import openai
from typing import Dict, List, Optional

# Set up OpenAI client if API key is available
openai_client = None
if os.environ.get("OPENAI_API_KEY"):
    openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_lua_script(prompt: str, script_type: str = "general") -> str:
    """
    Generate Lua scripts for Roblox based on natural language prompts
    
    Args:
        prompt: Natural language description of desired functionality
        script_type: Type of script (npc, quest, interaction, etc.)
    
    Returns:
        Generated Lua script content
    """
    try:
        if openai_client:
            return generate_with_ai(prompt, script_type)
        else:
            return generate_template_script(prompt, script_type)
    except Exception as e:
        logging.error(f"Error generating Lua script: {e}")
        return generate_fallback_script(prompt, script_type)

def generate_with_ai(prompt: str, script_type: str) -> str:
    """Generate script using OpenAI API"""
    system_prompt = f"""You are an expert Roblox Lua script generator. Generate clean, functional Lua code for Roblox Studio based on the user's description.

Rules:
1. Use proper Roblox API syntax
2. Include error handling
3. Add helpful comments
4. Follow Roblox scripting best practices
5. Make scripts modular and reusable

Script type: {script_type}
Target: Roblox Studio environment
"""

    user_prompt = f"Generate a Roblox Lua script for: {prompt}"
    
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return generate_template_script(prompt, script_type)

def generate_template_script(prompt: str, script_type: str) -> str:
    """Generate script using templates based on keywords"""
    prompt_lower = prompt.lower()
    
    if script_type == "npc" or "npc" in prompt_lower:
        return generate_npc_script(prompt)
    elif script_type == "quest" or "quest" in prompt_lower:
        return generate_quest_script(prompt)
    elif script_type == "interaction" or "interact" in prompt_lower:
        return generate_interaction_script(prompt)
    elif script_type == "movement" or "move" in prompt_lower:
        return generate_movement_script(prompt)
    else:
        return generate_general_script(prompt)

def generate_npc_script(prompt: str) -> str:
    """Generate NPC behavior script"""
    return '''-- NPC Controller Script
-- Generated from prompt: ''' + prompt + '''

local NPCController = {}
local npc = script.Parent
local humanoid = npc:WaitForChild("Humanoid")
local rootPart = npc:WaitForChild("HumanoidRootPart")

-- NPC Configuration
local DIALOGUE_LINES = {
    "Hello there, traveler!",
    "Welcome to our village!",
    "How can I help you today?"
}

local PATROL_POINTS = {
    Vector3.new(0, 0, 0),
    Vector3.new(10, 0, 0),
    Vector3.new(10, 0, 10),
    Vector3.new(0, 0, 10)
}

-- State management
local currentState = "patrol"
local currentPatrolIndex = 1
local lastInteraction = 0

-- Functions
function NPCController.startDialogue(player)
    if tick() - lastInteraction < 2 then return end
    lastInteraction = tick()
    
    local randomLine = DIALOGUE_LINES[math.random(1, #DIALOGUE_LINES)]
    
    -- Create dialogue GUI
    local playerGui = player:FindFirstChild("PlayerGui")
    if playerGui then
        local dialogueGui = Instance.new("ScreenGui")
        dialogueGui.Name = "NPCDialogue"
        dialogueGui.Parent = playerGui
        
        local frame = Instance.new("Frame")
        frame.Size = UDim2.new(0.6, 0, 0.2, 0)
        frame.Position = UDim2.new(0.2, 0, 0.7, 0)
        frame.BackgroundColor3 = Color3.new(0, 0, 0)
        frame.BackgroundTransparency = 0.3
        frame.Parent = dialogueGui
        
        local textLabel = Instance.new("TextLabel")
        textLabel.Size = UDim2.new(1, 0, 1, 0)
        textLabel.BackgroundTransparency = 1
        textLabel.Text = randomLine
        textLabel.TextColor3 = Color3.new(1, 1, 1)
        textLabel.TextScaled = true
        textLabel.Parent = frame
        
        -- Auto-remove after 3 seconds
        wait(3)
        dialogueGui:Destroy()
    end
end

function NPCController.patrol()
    if currentState ~= "patrol" then return end
    
    local targetPoint = PATROL_POINTS[currentPatrolIndex]
    humanoid:MoveTo(targetPoint)
    
    -- Wait for arrival or timeout
    local connection
    local timeoutCounter = 0
    connection = humanoid.MoveToFinished:Connect(function(reached)
        connection:Disconnect()
        if reached then
            currentPatrolIndex = currentPatrolIndex + 1
            if currentPatrolIndex > #PATROL_POINTS then
                currentPatrolIndex = 1
            end
        end
    end)
    
    -- Timeout after 10 seconds
    spawn(function()
        wait(10)
        if connection then
            connection:Disconnect()
        end
    end)
end

-- Event connections
local clickDetector = Instance.new("ClickDetector")
clickDetector.MaxActivationDistance = 10
clickDetector.Parent = rootPart

clickDetector.MouseClick:Connect(function(player)
    currentState = "talking"
    humanoid:MoveTo(rootPart.Position) -- Stop moving
    NPCController.startDialogue(player)
    
    wait(5) -- Talk for 5 seconds
    currentState = "patrol"
end)

-- Start patrol loop
spawn(function()
    while npc.Parent do
        if currentState == "patrol" then
            NPCController.patrol()
        end
        wait(2)
    end
end)

return NPCController'''

def generate_quest_script(prompt: str) -> str:
    """Generate quest management script"""
    return '''-- Quest Manager Script
-- Generated from prompt: ''' + prompt + '''

local QuestManager = {}
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

-- Quest Configuration
local QUESTS = {
    {
        id = "collect_coins",
        name = "Coin Collector",
        description = "Collect 10 gold coins",
        objectives = {
            {type = "collect", item = "GoldCoin", amount = 10, current = 0}
        },
        rewards = {
            {type = "item", item = "Sword", amount = 1},
            {type = "experience", amount = 100}
        },
        isActive = false,
        isCompleted = false
    },
    {
        id = "defeat_enemies",
        name = "Monster Hunter",
        description = "Defeat 5 monsters",
        objectives = {
            {type = "defeat", enemy = "Monster", amount = 5, current = 0}
        },
        rewards = {
            {type = "item", item = "Shield", amount = 1},
            {type = "experience", amount = 200}
        },
        isActive = false,
        isCompleted = false
    }
}

-- Player quest data
local playerQuests = {}

-- Functions
function QuestManager.getPlayerQuests(player)
    if not playerQuests[player.UserId] then
        playerQuests[player.UserId] = {}
        -- Initialize with default quests
        for _, quest in pairs(QUESTS) do
            local playerQuest = {}
            for key, value in pairs(quest) do
                if type(value) == "table" then
                    playerQuest[key] = {}
                    for k, v in pairs(value) do
                        if type(v) == "table" then
                            playerQuest[key][k] = {}
                            for subKey, subValue in pairs(v) do
                                playerQuest[key][k][subKey] = subValue
                            end
                        else
                            playerQuest[key][k] = v
                        end
                    end
                else
                    playerQuest[key] = value
                end
            end
            table.insert(playerQuests[player.UserId], playerQuest)
        end
    end
    return playerQuests[player.UserId]
end

function QuestManager.startQuest(player, questId)
    local quests = QuestManager.getPlayerQuests(player)
    
    for _, quest in pairs(quests) do
        if quest.id == questId and not quest.isActive and not quest.isCompleted then
            quest.isActive = true
            
            -- Notify player
            QuestManager.notifyPlayer(player, "Quest Started: " .. quest.name)
            return true
        end
    end
    return false
end

function QuestManager.updateProgress(player, objectiveType, item, amount)
    local quests = QuestManager.getPlayerQuests(player)
    
    for _, quest in pairs(quests) do
        if quest.isActive and not quest.isCompleted then
            for _, objective in pairs(quest.objectives) do
                if objective.type == objectiveType and 
                   (not objective.item or objective.item == item) and
                   (not objective.enemy or objective.enemy == item) then
                    
                    objective.current = math.min(objective.current + amount, objective.amount)
                    
                    -- Check if quest is completed
                    local allCompleted = true
                    for _, obj in pairs(quest.objectives) do
                        if obj.current < obj.amount then
                            allCompleted = false
                            break
                        end
                    end
                    
                    if allCompleted then
                        QuestManager.completeQuest(player, quest.id)
                    else
                        QuestManager.notifyPlayer(player, 
                            string.format("Progress: %s (%d/%d)", 
                                quest.name, objective.current, objective.amount))
                    end
                end
            end
        end
    end
end

function QuestManager.completeQuest(player, questId)
    local quests = QuestManager.getPlayerQuests(player)
    
    for _, quest in pairs(quests) do
        if quest.id == questId and quest.isActive then
            quest.isActive = false
            quest.isCompleted = true
            
            -- Give rewards
            for _, reward in pairs(quest.rewards) do
                QuestManager.giveReward(player, reward)
            end
            
            QuestManager.notifyPlayer(player, "Quest Completed: " .. quest.name)
            return true
        end
    end
    return false
end

function QuestManager.giveReward(player, reward)
    if reward.type == "item" then
        -- Add item to player inventory (implement based on your inventory system)
        print("Giving " .. reward.amount .. " " .. reward.item .. " to " .. player.Name)
    elseif reward.type == "experience" then
        -- Add experience (implement based on your progression system)
        print("Giving " .. reward.amount .. " experience to " .. player.Name)
    end
end

function QuestManager.notifyPlayer(player, message)
    -- Create notification GUI
    local playerGui = player:FindFirstChild("PlayerGui")
    if playerGui then
        local notification = Instance.new("ScreenGui")
        notification.Name = "QuestNotification"
        notification.Parent = playerGui
        
        local frame = Instance.new("Frame")
        frame.Size = UDim2.new(0.4, 0, 0.1, 0)
        frame.Position = UDim2.new(0.3, 0, 0.1, 0)
        frame.BackgroundColor3 = Color3.new(0.2, 0.8, 0.2)
        frame.Parent = notification
        
        local textLabel = Instance.new("TextLabel")
        textLabel.Size = UDim2.new(1, 0, 1, 0)
        textLabel.BackgroundTransparency = 1
        textLabel.Text = message
        textLabel.TextColor3 = Color3.new(1, 1, 1)
        textLabel.TextScaled = true
        textLabel.Parent = frame
        
        -- Fade out animation
        spawn(function()
            wait(3)
            for i = 1, 10 do
                frame.BackgroundTransparency = i / 10
                textLabel.TextTransparency = i / 10
                wait(0.1)
            end
            notification:Destroy()
        end)
    end
end

-- Initialize for all players
Players.PlayerAdded:Connect(function(player)
    QuestManager.getPlayerQuests(player)
    
    -- Auto-start first quest
    wait(2)
    QuestManager.startQuest(player, "collect_coins")
end)

return QuestManager'''

def generate_interaction_script(prompt: str) -> str:
    """Generate interaction script"""
    return '''-- Interaction System Script
-- Generated from prompt: ''' + prompt + '''

local InteractionSystem = {}
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")

-- Configuration
local INTERACTION_KEY = Enum.KeyCode.E
local INTERACTION_DISTANCE = 10

-- Current interactable object
local currentInteractable = nil
local player = Players.LocalPlayer
local character = player.CharacterAdded:Wait()
local humanoidRootPart = character:WaitForChild("HumanoidRootPart")

-- GUI Elements
local playerGui = player:WaitForChild("PlayerGui")
local interactionGui = Instance.new("ScreenGui")
interactionGui.Name = "InteractionGUI"
interactionGui.Parent = playerGui

local promptFrame = Instance.new("Frame")
promptFrame.Size = UDim2.new(0.3, 0, 0.1, 0)
promptFrame.Position = UDim2.new(0.35, 0, 0.8, 0)
promptFrame.BackgroundColor3 = Color3.new(0, 0, 0)
promptFrame.BackgroundTransparency = 0.3
promptFrame.Visible = false
promptFrame.Parent = interactionGui

local promptLabel = Instance.new("TextLabel")
promptLabel.Size = UDim2.new(1, 0, 1, 0)
promptLabel.BackgroundTransparency = 1
promptLabel.Text = "Press E to interact"
promptLabel.TextColor3 = Color3.new(1, 1, 1)
promptLabel.TextScaled = true
promptLabel.Parent = promptFrame

-- Functions
function InteractionSystem.registerInteractable(object, interactionFunction, promptText)
    if not object:FindFirstChild("InteractionData") then
        local interactionData = Instance.new("ObjectValue")
        interactionData.Name = "InteractionData"
        interactionData.Parent = object
        
        -- Store interaction function and prompt
        object:SetAttribute("InteractionFunction", tostring(interactionFunction))
        object:SetAttribute("PromptText", promptText or "Press E to interact")
        
        -- Add click detector as backup
        local clickDetector = Instance.new("ClickDetector")
        clickDetector.MaxActivationDistance = INTERACTION_DISTANCE
        clickDetector.Parent = object
        
        clickDetector.MouseClick:Connect(function(clickingPlayer)
            if clickingPlayer == player then
                InteractionSystem.executeInteraction(object)
            end
        end)
    end
end

function InteractionSystem.executeInteraction(object)
    local functionName = object:GetAttribute("InteractionFunction")
    
    if functionName == "openChest" then
        InteractionSystem.openChest(object)
    elseif functionName == "openDoor" then
        InteractionSystem.openDoor(object)
    elseif functionName == "collectItem" then
        InteractionSystem.collectItem(object)
    elseif functionName == "activateSwitch" then
        InteractionSystem.activateSwitch(object)
    else
        print("Unknown interaction: " .. tostring(functionName))
    end
end

function InteractionSystem.openChest(chest)
    if chest:GetAttribute("IsOpen") then return end
    
    chest:SetAttribute("IsOpen", true)
    
    -- Animation (simple rotation)
    local lid = chest:FindFirstChild("Lid")
    if lid then
        lid.CFrame = lid.CFrame * CFrame.Angles(math.rad(-90), 0, 0)
    end
    
    -- Spawn loot
    local loot = {"Gold", "Gem", "Potion"}
    local randomLoot = loot[math.random(1, #loot)]
    
    print(player.Name .. " found " .. randomLoot .. " in the chest!")
    
    -- Create floating text
    InteractionSystem.createFloatingText(chest.Position + Vector3.new(0, 3, 0), 
        "Found " .. randomLoot .. "!", Color3.new(1, 1, 0))
end

function InteractionSystem.openDoor(door)
    local isOpen = door:GetAttribute("IsOpen") or false
    
    door:SetAttribute("IsOpen", not isOpen)
    
    -- Simple door animation
    if isOpen then
        -- Close door
        door.CFrame = door.CFrame * CFrame.Angles(0, math.rad(-90), 0)
    else
        -- Open door
        door.CFrame = door.CFrame * CFrame.Angles(0, math.rad(90), 0)
    end
    
    print("Door " .. (isOpen and "closed" or "opened"))
end

function InteractionSystem.collectItem(item)
    -- Add to inventory (implement based on your inventory system)
    local itemName = item.Name
    print(player.Name .. " collected " .. itemName)
    
    -- Remove item from world
    item:Destroy()
    
    -- Create collection effect
    InteractionSystem.createFloatingText(item.Position, 
        "+" .. itemName, Color3.new(0, 1, 0))
end

function InteractionSystem.activateSwitch(switch)
    local isActivated = switch:GetAttribute("IsActivated") or false
    
    switch:SetAttribute("IsActivated", not isActivated)
    
    -- Change switch color
    if switch:FindFirstChild("SwitchPart") then
        switch.SwitchPart.Color = isActivated and Color3.new(1, 0, 0) or Color3.new(0, 1, 0)
    end
    
    print("Switch " .. (isActivated and "deactivated" or "activated"))
end

function InteractionSystem.createFloatingText(position, text, color)
    local part = Instance.new("Part")
    part.Size = Vector3.new(0.1, 0.1, 0.1)
    part.Position = position
    part.Anchored = true
    part.CanCollide = false
    part.Transparency = 1
    part.Parent = workspace
    
    local billboardGui = Instance.new("BillboardGui")
    billboardGui.Size = UDim2.new(4, 0, 2, 0)
    billboardGui.Parent = part
    
    local textLabel = Instance.new("TextLabel")
    textLabel.Size = UDim2.new(1, 0, 1, 0)
    textLabel.BackgroundTransparency = 1
    textLabel.Text = text
    textLabel.TextColor3 = color
    textLabel.TextScaled = true
    textLabel.Font = Enum.Font.GothamBold
    textLabel.Parent = billboardGui
    
    -- Floating animation
    spawn(function()
        for i = 1, 60 do
            part.Position = part.Position + Vector3.new(0, 0.05, 0)
            textLabel.TextTransparency = i / 60
            wait(0.05)
        end
        part:Destroy()
    end)
end

function InteractionSystem.checkNearbyInteractables()
    local nearestDistance = math.huge
    local nearestInteractable = nil
    
    for _, object in pairs(workspace:GetDescendants()) do
        if object:FindFirstChild("InteractionData") and object:FindFirstChild("Position") then
            local distance = (humanoidRootPart.Position - object.Position).Magnitude
            
            if distance <= INTERACTION_DISTANCE and distance < nearestDistance then
                nearestDistance = distance
                nearestInteractable = object
            end
        end
    end
    
    if nearestInteractable ~= currentInteractable then
        currentInteractable = nearestInteractable
        
        if currentInteractable then
            promptLabel.Text = currentInteractable:GetAttribute("PromptText") or "Press E to interact"
            promptFrame.Visible = true
        else
            promptFrame.Visible = false
        end
    end
end

-- Input handling
UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    
    if input.KeyCode == INTERACTION_KEY and currentInteractable then
        InteractionSystem.executeInteraction(currentInteractable)
    end
end)

-- Main loop
spawn(function()
    while true do
        if character and humanoidRootPart then
            InteractionSystem.checkNearbyInteractables()
        end
        wait(0.1)
    end
end)

-- Example usage - register some interactables
spawn(function()
    wait(2) -- Wait for game to load
    
    -- Register all parts named "Chest" as chests
    for _, object in pairs(workspace:GetDescendants()) do
        if object.Name == "Chest" and object:IsA("BasePart") then
            InteractionSystem.registerInteractable(object, "openChest", "Press E to open chest")
        elseif object.Name == "Door" and object:IsA("BasePart") then
            InteractionSystem.registerInteractable(object, "openDoor", "Press E to open/close door")
        elseif object.Name:match("Coin") and object:IsA("BasePart") then
            InteractionSystem.registerInteractable(object, "collectItem", "Press E to collect " .. object.Name)
        elseif object.Name == "Switch" and object:IsA("BasePart") then
            InteractionSystem.registerInteractable(object, "activateSwitch", "Press E to activate switch")
        end
    end
end)

return InteractionSystem'''

def generate_movement_script(prompt: str) -> str:
    """Generate movement/character controller script"""
    return '''-- Enhanced Movement Controller
-- Generated from prompt: ''' + prompt + '''

local MovementController = {}
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer
local character = player.CharacterAdded:Wait()
local humanoid = character:WaitForChild("Humanoid")
local rootPart = character:WaitForChild("HumanoidRootPart")

-- Movement configuration
local WALK_SPEED = 16
local RUN_SPEED = 24
local JUMP_POWER = 50
local DASH_FORCE = 100
local DASH_COOLDOWN = 2

-- State tracking
local isRunning = false
local canDash = true
local lastDashTime = 0

-- Functions
function MovementController.enableRunning()
    isRunning = true
    humanoid.WalkSpeed = RUN_SPEED
end

function MovementController.disableRunning()
    isRunning = false
    humanoid.WalkSpeed = WALK_SPEED
end

function MovementController.dash()
    if not canDash or tick() - lastDashTime < DASH_COOLDOWN then
        return
    end
    
    canDash = false
    lastDashTime = tick()
    
    -- Get movement direction
    local moveVector = humanoid.MoveDirection
    if moveVector.Magnitude == 0 then
        moveVector = rootPart.CFrame.LookVector
    end
    
    -- Create dash force
    local bodyVelocity = Instance.new("BodyVelocity")
    bodyVelocity.MaxForce = Vector3.new(4000, 0, 4000)
    bodyVelocity.Velocity = moveVector * DASH_FORCE
    bodyVelocity.Parent = rootPart
    
    -- Remove dash force after short duration
    spawn(function()
        wait(0.2)
        bodyVelocity:Destroy()
        
        wait(DASH_COOLDOWN - 0.2)
        canDash = true
    end)
    
    -- Visual effect
    MovementController.createDashEffect()
end

function MovementController.createDashEffect()
    local effect = Instance.new("Explosion")
    effect.Position = rootPart.Position
    effect.BlastRadius = 0
    effect.BlastPressure = 0
    effect.Visible = false
    effect.Parent = workspace
    
    -- Particle effect
    local attachment = Instance.new("Attachment")
    attachment.Parent = rootPart
    
    local particles = Instance.new("ParticleEmitter")
    particles.Texture = "rbxassetid://241650934"
    particles.Lifetime = NumberRange.new(0.3, 0.6)
    particles.Rate = 500
    particles.SpreadAngle = Vector2.new(45, 45)
    particles.Speed = NumberRange.new(10, 20)
    particles.Parent = attachment
    
    spawn(function()
        wait(0.1)
        particles.Enabled = false
        wait(1)
        attachment:Destroy()
    end)
end

function MovementController.handleInput(input, gameProcessed)
    if gameProcessed then return end
    
    if input.KeyCode == Enum.KeyCode.LeftShift then
        MovementController.enableRunning()
    elseif input.KeyCode == Enum.KeyCode.Q then
        MovementController.dash()
    end
end

function MovementController.handleInputEnded(input, gameProcessed)
    if gameProcessed then return end
    
    if input.KeyCode == Enum.KeyCode.LeftShift then
        MovementController.disableRunning()
    end
end

-- Event connections
UserInputService.InputBegan:Connect(MovementController.handleInput)
UserInputService.InputEnded:Connect(MovementController.handleInputEnded)

-- Initialize
humanoid.WalkSpeed = WALK_SPEED
humanoid.JumpPower = JUMP_POWER

-- Character respawn handling
player.CharacterAdded:Connect(function(newCharacter)
    character = newCharacter
    humanoid = character:WaitForChild("Humanoid")
    rootPart = character:WaitForChild("HumanoidRootPart")
    
    humanoid.WalkSpeed = WALK_SPEED
    humanoid.JumpPower = JUMP_POWER
    
    isRunning = false
    canDash = true
    lastDashTime = 0
end)

return MovementController'''

def generate_general_script(prompt: str) -> str:
    """Generate general purpose script"""
    return f'''-- General Script
-- Generated from prompt: {prompt}

local Script = {{}}

-- Configuration
local CONFIG = {{
    enabled = true,
    debug = false
}}

-- Services
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

-- Variables
local player = Players.LocalPlayer

-- Functions
function Script.initialize()
    if CONFIG.debug then
        print("Initializing script for: {prompt}")
    end
    
    -- Add your initialization code here
    
end

function Script.cleanup()
    if CONFIG.debug then
        print("Cleaning up script")
    end
    
    -- Add cleanup code here
end

-- Initialize the script
Script.initialize()

-- Handle player leaving (for cleanup)
Players.PlayerRemoving:Connect(function(leavingPlayer)
    if leavingPlayer == player then
        Script.cleanup()
    end
end)

return Script'''

def generate_fallback_script(prompt: str, script_type: str) -> str:
    """Generate basic fallback script when other methods fail"""
    return f'''-- Basic {script_type.title()} Script
-- Generated for: {prompt}

local {script_type.title()}Script = {{}}

-- This is a basic template script
-- Customize it based on your needs

print("Script generated for: {prompt}")

return {script_type.title()}Script'''