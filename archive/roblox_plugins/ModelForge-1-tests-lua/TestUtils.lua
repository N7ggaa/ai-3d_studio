-- TestUtils.lua
-- Utility functions for testing

local TestUtils = {}

-- Create a temporary folder for test output
-- @param parent Parent instance (optional)
-- @param name Name of the folder (optional)
-- @return The created folder
function TestUtils.createTestFolder(parent, name)
    local folder = Instance.new("Folder")
    folder.Name = name or "TestFolder_" .. tostring(tick())
    
    if parent then
        folder.Parent = parent
    end
    
    return folder
end

-- Create a mock function that records calls
-- @return A table with the mock function and a method to get call history
function TestUtils.createMockFunction()
    local callHistory = {}
    
    local mock = function(...)
        local args = {...}
        table.insert(callHistory, {
            args = args,
            timestamp = tick(),
            callCount = #callHistory + 1
        })
        
        -- If this mock was configured to return values
        if mock.returnValues and #mock.returnValues > 0 then
            local returnValue = table.remove(mock.returnValues, 1)
            if type(returnValue) == "function" then
                return returnValue(unpack(args))
            else
                return returnValue
            end
        end
        
        return mock.defaultReturn
    end
    
    -- Add methods to the mock function
    mock.getCallHistory = function()
        return callHistory
    end
    
    mock.getCallCount = function()
        return #callHistory
    end
    
    mock.wasCalledWith = function(...)
        local expectedArgs = {...}
        
        for _, call in ipairs(callHistory) do
            local match = true
            
            for i, expected in ipairs(expectedArgs) do
                if call.args[i] ~= expected then
                    match = false
                    break
                end
            end
            
            if match then
                return true
            end
        end
        
        return false
    end
    
    -- Configure return values
    mock.returns = function(...)
        mock.returnValues = {...}
        return mock
    end
    
    mock.returnsAsync = function(delay, ...)
        local values = {...}
        mock.returnValues = {
            function()
                task.wait(delay or 0.1)
                return table.unpack(values)
            end
        }
        return mock
    end
    
    -- Reset the mock
    mock.reset = function()
        callHistory = {}
        mock.returnValues = nil
        mock.defaultReturn = nil
    end
    
    return mock
end

-- Create a mock instance with the specified properties and methods
-- @param className The class name of the instance
-- @param props Table of properties to set
-- @param methods Table of methods to add
-- @return The mock instance
function TestUtils.createMockInstance(className, props, methods)
    local mock = Instance.new(className)
    
    -- Set properties
    if props then
        for name, value in pairs(props) do
            pcall(function()
                mock[name] = value
            end)
        end
    end
    
    -- Add methods
    if methods then
        for name, func in pairs(methods) do
            if type(func) == "function" then
                mock[name] = func
            end
        end
    end
    
    return mock
end

-- Create a mock plugin
-- @return A mock plugin object
function TestUtils.createMockPlugin()
    local mock = {
        _settings = {},
        _toolbarButtons = {},
        _guiObjects = {}
    }
    
    function mock:GetSetting(key)
        return self._settings[key]
    end
    
    function mock:SetSetting(key, value)
        self._settings[key] = value
    end
    
    function mock:CreateToolbar(name)
        local toolbar = {
            Name = name,
            Buttons = {}
        }
        
        function toolbar:CreateButton(name, tooltip, icon)
            local button = {
                Name = name,
                ToolTip = tooltip,
                Icon = icon,
                Click = Instance.new("BindableEvent")
            }
            
            table.insert(self.Buttons, button)
            table.insert(mock._toolbarButtons, button)
            
            return button
        end
        
        return toolbar
    end
    
    function mock:CreateDockWidgetPluginGui(id, props)
        local widget = {
            Name = props.Name or "DockWidget",
            Title = props.Name or "Dock Widget",
            Enabled = true,
            _widgetInfo = DockWidgetPluginGuiInfo.new(
                props.InitialDockState or Enum.InitialDockState.Float,
                props.InitialEnabled or true,
                props.InitialEnabledShouldOverrideRestore or false,
                props.InitX or 0,
                props.InitY or 0,
                props.InitWidth or 400,
                props.InitHeight or 300
            )
        }
        
        -- Add to gui objects
        table.insert(mock._guiObjects, widget)
        
        return widget
    end
    
    -- Simulate plugin unload
    mock.Unloading = Instance.new("BindableEvent")
    
    return mock
end

-- Assert that a condition is true
-- @param condition The condition to check
-- @param message The message to display if the assertion fails
function TestUtils.assertTrue(condition, message)
    if not condition then
        error(message or "Assertion failed: expected true, got false", 2)
    end
end

-- Assert that a condition is false
-- @param condition The condition to check
-- @param message The message to display if the assertion fails
function TestUtils.assertFalse(condition, message)
    if condition then
        error(message or "Assertion failed: expected false, got true", 2)
    end
end

-- Assert that two values are equal
-- @param expected The expected value
-- @param actual The actual value
-- @param message The message to display if the assertion fails
function TestUtils.assertEquals(expected, actual, message)
    if expected ~= actual then
        error(string.format("%s\nExpected: %s\nActual: %s", 
            message or "Assertion failed: values are not equal",
            tostring(expected),
            tostring(actual)
        ), 2)
    end
end

-- Assert that a function throws an error
-- @param func The function to test
-- @param expectedError Optional expected error message (partial match)
-- @return The error message if the function threw an error
function TestUtils.assertThrows(func, expectedError)
    local success, err = pcall(func)
    
    if success then
        error("Expected function to throw an error, but it didn't", 2)
    end
    
    if expectedError and not string.find(tostring(err), expectedError, 1, true) then
        error(string.format("Expected error to contain: %s\nBut got: %s", expectedError, tostring(err)), 2)
    end
    
    return err
end

-- Run a test function and capture any errors
-- @param name The name of the test
-- @param func The test function
-- @return true if the test passed, false otherwise
-- @return The error message if the test failed, or nil
function TestUtils.runTest(name, func)
    local success, err = pcall(func)
    
    if success then
        print(string.format("✅ %s: Passed", name))
        return true
    else
        print(string.format("❌ %s: Failed - %s", name, tostring(err)))
        return false, err
    end
end

-- Run a suite of tests
-- @param tests Table of test functions with names as keys
-- @return Table of test results
function TestUtils.runTestSuite(tests)
    local results = {
        passed = 0,
        failed = 0,
        tests = {}
    }
    
    print(string.format("\nRunning %d tests...\n", #tests))
    
    for name, test in pairs(tests) do
        if type(test) == "function" then
            local startTime = tick()
            local success, err = TestUtils.runTest(name, test)
            local duration = tick() - startTime
            
            table.insert(results.tests, {
                name = name,
                success = success,
                error = err,
                duration = duration
            })
            
            if success then
                results.passed = results.passed + 1
            else
                results.failed = results.failed + 1
            end
        end
    end
    
    -- Print summary
    print(string.format("\nTest Summary: %d passed, %d failed\n", results.passed, results.failed))
    
    return results
end

-- Create a test model with parts
-- @param parent Parent to put the model under
-- @param partCount Number of parts to create
-- @return The created model
function TestUtils.createTestModel(parent, partCount)
    partCount = partCount or 5
    
    local model = Instance.new("Model")
    model.Name = "TestModel"
    
    -- Create parts
    for i = 1, partCount do
        local part = Instance.new("Part")
        part.Name = "Part" .. i
        part.Size = Vector3.new(2, 2, 2)
        part.Position = Vector3.new(i * 3, 0, 0)
        part.Parent = model
        
        -- Add some variety
        if i % 2 == 0 then
            part.BrickColor = BrickColor.new("Bright blue")
        else
            part.BrickColor = BrickColor.new("Bright red")
        end
    end
    
    if parent then
        model.Parent = parent
    end
    
    return model
end

-- Create a test part with optional properties
-- @param parent Parent to put the part under
-- @param props Table of properties to set
-- @return The created part
function TestUtils.createTestPart(parent, props)
    local part = Instance.new("Part")
    
    -- Apply properties
    if props then
        for name, value in pairs(props) do
            if name ~= "Parent" then
                part[name] = value
            end
        end
    end
    
    -- Set default properties if not specified
    if not props or props.Size == nil then
        part.Size = Vector3.new(4, 1, 2)
    end
    
    if not props or props.Position == nil then
        part.Position = Vector3.new(0, 10, 0)
    end
    
    if not props or props.Anchored == nil then
        part.Anchored = true
    end
    
    -- Parent last to avoid unnecessary property updates
    if parent then
        part.Parent = parent
    end
    
    return part
end

-- Create a test character
-- @param parent Parent to put the character under
-- @return The created character model
function TestUtils.createTestCharacter(parent)
    local character = Instance.new("Model")
    character.Name = "TestCharacter"
    
    -- Create humanoid
    local humanoid = Instance.new("Humanoid")
    humanoid.Parent = character
    
    -- Create body parts
    local parts = {
        {name = "Head", size = Vector3.new(2, 1, 1), offset = Vector3.new(0, 2.5, 0)},
        {name = "Torso", size = Vector3.new(2, 2, 1), offset = Vector3.new(0, 0, 0)},
        {name = "Left Arm", size = Vector3.new(1, 2, 1), offset = Vector3.new(-1.5, 0, 0)},
        {name = "Right Arm", size = Vector3.new(1, 2, 1), offset = Vector3.new(1.5, 0, 0)},
        {name = "Left Leg", size = Vector3.new(1, 2, 1), offset = Vector3.new(-0.5, -2, 0)},
        {name = "Right Leg", size = Vector3.new(1, 2, 1), offset = Vector3.new(0.5, -2, 0)}
    }
    
    for _, partInfo in ipairs(parts) do
        local part = Instance.new("Part")
        part.Name = partInfo.name
        part.Size = partInfo.size
        part.Position = partInfo.offset
        part.BrickColor = BrickColor.new("Bright blue")
        part.Parent = character
    end
    
    -- Add humanoid root part
    local humanoidRootPart = character:FindFirstChild("Torso")
    if humanoidRootPart then
        humanoidRootPart.Name = "HumanoidRootPart"
    end
    
    if parent then
        character.Parent = parent
    end
    
    return character
end

return TestUtils
