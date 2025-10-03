-- test_AIModelService.lua
-- Unit tests for the AIModelService module

local AIModelService = require(script.Parent.Parent.src.services.AIModelService)

return function()
    describe("AIModelService", function()
        local service
        
        beforeAll(function()
            -- Create a test output directory
            local testOutputDir = "test_output"
            if not isfolder(testOutputDir) then
                makefolder(testOutputDir)
            end
            
            -- Create a new AIModelService instance for testing
            service = AIModelService.new({
                outputDir = testOutputDir,
                tempDir = "test_temp",
                maxConcurrentJobs = 1,
                cacheEnabled = false
            })
        end)
        
        afterEach(function()
            -- Clean up after each test
            service:stop()
        end)
        
        afterAll(function()
            -- Clean up test directories
            pcall(function() delfolder("test_output") end)
            pcall(function() delfolder("test_temp") end)
        end)
        
        it("should initialize with default values", function()
            local defaultService = AIModelService.new()
            expect(defaultService).to.be.ok()
            expect(defaultService.config.modelPreset).to.equal("medium")
            expect(defaultService.config.generateLODs).to.equal(true)
        end)
        
        it("should generate a model from text", function()
            local completed = false
            local result
            
            local jobId = service:generateFromText("a red cube", {
                preset = "low"
            }, function(success, data)
                completed = true
                result = data
            end)
            
            -- Wait for job to complete
            local startTime = os.clock()
            while not completed and os.clock() - startTime < 10 do
                wait()
            end
            
            expect(completed).to.equal(true)
            expect(result).to.be.ok()
            expect(result.success).to.equal(true)
            expect(result.modelId).to.be.a("string")
            expect(#result.modelId).to.be.above(0)
        end)
        
        it("should handle multiple generation requests", function()
            local completed = {}
            local results = {}
            local jobIds = {}
            
            -- Start multiple jobs
            for i = 1, 3 do
                local jobId = service:generateFromText("test " .. i, {
                    priority = i
                }, function(success, data)
                    table.insert(completed, i)
                    results[i] = data
                end)
                table.insert(jobIds, jobId)
            end
            
            -- Wait for jobs to complete
            local startTime = os.clock()
            while #completed < 3 and os.clock() - startTime < 20 do
                wait()
            end
            
            expect(#completed).to.equal(3)
            expect(#jobIds).to.equal(3)
            
            -- Verify all jobs completed successfully
            for i = 1, 3 do
                expect(results[i]).to.be.ok()
                expect(results[i].success).to.equal(true)
            end
        end)
        
        it("should handle job cancellation", function()
            local jobId = service:generateFromText("cancel test", {
                delay = 5 -- Simulate long-running job
            }, function()
                -- This should not be called if cancellation works
                expect(false).to.equal(true, "Job callback should not be called after cancellation")
            end)
            
            -- Cancel the job
            local success, message = service:cancelJob(jobId)
            expect(success).to.equal(true)
            
            -- Verify job status is cancelled
            local status = service:getJobStatus(jobId)
            expect(status).to.be.ok()
            expect(status.status).to.equal("cancelled")
        end)
        
        it("should provide queue statistics", function()
            local stats = service:getQueueStats()
            expect(stats).to.be.a("table")
            expect(stats.maxConcurrent).to.equal(1) -- As configured in beforeAll
            expect(stats.isRunning).to.equal(true)
        end)
        
        it("should generate models with different presets", function()
            local presets = {"low", "medium", "high", "ultra"}
            local completed = 0
            
            for _, preset in ipairs(presets) do
                service:generateFromText("test preset: " .. preset, {
                    preset = preset
                }, function(success, result)
                    if success then
                        completed = completed + 1
                        expect(result.metadata).to.be.ok()
                        expect(result.metadata.params.preset).to.equal(preset)
                    end
                end)
            end
            
            -- Wait for jobs to complete
            local startTime = os.clock()
            while completed < #presets and os.clock() - startTime < 30 do
                wait()
            end
            
            expect(completed).to.equal(#presets)
        end)
        
        it("should handle model generation errors", function()
            local completed = false
            local errorMessage
            
            -- Test with invalid parameters
            service:generateFromText("", {
                shouldFail = true -- Simulate failure
            }, function(success, result)
                completed = true
                if not success then
                    errorMessage = result.error
                end
            end)
            
            -- Wait for job to complete
            local startTime = os.clock()
            while not completed and os.clock() - startTime < 10 do
                wait()
            end
            
            expect(completed).to.equal(true)
            expect(errorMessage).to.be.a("string")
            expect(#errorMessage).to.be.above(0)
        end)
    end)
end
