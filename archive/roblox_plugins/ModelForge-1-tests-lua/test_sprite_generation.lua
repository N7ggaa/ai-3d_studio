-- test_sprite_generation.lua
-- Test script for verifying sprite generation functionality

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TestService = game:GetService("TestService")

-- Load test utilities
local TestUtils = require(script.Parent.TestUtils)

-- Load modules to test
local SpriteGenerator = require(script.Parent.Parent.src.utils.SpriteGenerator)
local Settings = require(script.Parent.Parent.src.config.Settings)

-- Mock plugin for testing
local mockPlugin = {
    _settings = {},
    GetSetting = function(self, key)
        return self._settings[key]
    end,
    SetSetting = function(self, key, value)
        self._settings[key] = value
    end
}

-- Create test suite
local TestSpriteGeneration = {}
TestSpriteGeneration.__index = TestSpriteGeneration

function TestSpriteGeneration.new()
    local self = setmetatable({}, TestSpriteGeneration)
    
    -- Initialize test environment
    self.testFolder = Instance.new("Folder")
    self.testFolder.Name = "TestSpriteGeneration"
    self.testFolder.Parent = TestService:FindFirstChild("TestResults") or workspace
    
    -- Initialize settings
    self.settings = Settings.new(mockPlugin)
    
    -- Initialize sprite generator
    self.spriteGenerator = SpriteGenerator.new({
        outputDir = "TestOutput/Sprites",
        tempDir = "TestOutput/Temp",
        defaultSpriteSize = Vector2.new(64, 64)
    })
    
    return self
end

-- Test creating a simple colored sprite
function TestSpriteGeneration:testCreateColoredSprite()
    local testName = "ColoredSprite"
    local color = Color3.fromRGB(255, 0, 0) -- Red
    local size = Vector2.new(32, 32)
    
    local success, result = pcall(function()
        return self.spriteGenerator:createColoredSprite(testName, color, size)
    end)
    
    assert(success, "Failed to create colored sprite: " .. tostring(result))
    assert(result ~= nil, "Sprite creation returned nil")
    
    -- Verify sprite properties
    assert(result.Name == testName, "Sprite name doesn't match")
    assert(result:IsA("ImageLabel"), "Sprite is not an ImageLabel")
    assert(result.Size == UDim2.fromOffset(size.X, size.Y), "Sprite size doesn't match")
    
    -- Clean up
    result:Destroy()
    
    return true
end

-- Test creating a sprite from an image file
function TestSpriteGeneration:testCreateSpriteFromImage()
    -- Create a test image first
    local testImagePath = "TestOutput/TestImage.png"
    local testImage = Instance.new("ImageLabel")
    testImage.Size = UDim2.fromOffset(64, 64)
    testImage.BackgroundColor3 = Color3.fromRGB(0, 255, 0) -- Green
    
    -- Save the test image
    -- Note: In a real test, you'd need to save this to a file
    
    local success, result = pcall(function()
        return self.spriteGenerator:createSpriteFromImage("TestSprite", testImagePath)
    end)
    
    -- In a real test, we'd verify the sprite was created correctly
    -- For now, just verify the function runs without errors
    
    return success
end

-- Test sprite sheet generation
function TestSpriteGeneration:testCreateSpriteSheet()
    -- Create test sprites
    local sprites = {}
    for i = 1, 4 do
        local sprite = self.spriteGenerator:createColoredSprite(
            "TestSprite" .. i,
            Color3.fromHSV(i/4, 1, 1),
            Vector2.new(32, 32)
        )
        table.insert(sprites, sprite)
    end
    
    -- Create sprite sheet
    local success, result = pcall(function()
        return self.spriteGenerator:createSpriteSheet("TestSpriteSheet", sprites, 2, 2)
    end)
    
    -- Clean up
    for _, sprite in ipairs(sprites) do
        sprite:Destroy()
    end
    
    return success and result ~= nil
end

-- Run all tests
function TestSpriteGeneration:runAllTests()
    local testResults = {}
    local passed = 0
    local failed = 0
    
    -- Run each test
    for name, test in pairs(TestSpriteGeneration) do
        if type(test) == "function" and name:find("^test") then
            local success, result = pcall(function()
                return test(self)
            end)
            
            testResults[name] = {
                success = success,
                result = result,
                error = not success and result or nil
            }
            
            if success and result then
                passed = passed + 1
                print("✅ Test passed: " .. name)
            else
                failed = failed + 1
                print("❌ Test failed: " .. name)
                if not success then
                    print("   Error: " .. tostring(result))
                end
            end
        end
    end
    
    -- Print summary
    print("\nTest Summary:")
    print(string.format("✅ %d tests passed", passed))
    print(string.format("❌ %d tests failed", failed))
    
    return testResults
end

-- Run tests when the script is executed
local testRunner = TestSpriteGeneration.new()
return testRunner:runAllTests()
