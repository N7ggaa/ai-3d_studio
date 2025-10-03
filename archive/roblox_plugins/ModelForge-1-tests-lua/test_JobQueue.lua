-- test_JobQueue.lua
-- Unit tests for the JobQueue module

local JobQueue = require(script.Parent.Parent.src.services.JobQueue)

return function()
    describe("JobQueue", function()
        local jobQueue
        
        beforeAll(function()
            -- Create a new JobQueue instance for testing
            jobQueue = JobQueue.new({
                maxConcurrentJobs = 2,
                retryAttempts = 2,
                retryDelay = 0.1,
                jobTimeout = 5,
                autoStart = false
            })
        end)
        
        afterEach(function()
            -- Clean up after each test
            jobQueue:stop()
            jobQueue = JobQueue.new({
                maxConcurrentJobs = 2,
                retryAttempts = 2,
                retryDelay = 0.1,
                jobTimeout = 5,
                autoStart = false
            })
        end)
        
        it("should initialize with default values", function()
            local queue = JobQueue.new()
            expect(queue).to.be.ok()
            expect(queue.config.maxConcurrentJobs).to.equal(3)
        end)
        
        it("should add jobs to the queue", function()
            local jobId = jobQueue:addJob({type = "test"}, 1)
            expect(jobId).to.be.a("string")
            expect(jobQueue:getJobStatus(jobId).status).to.equal(JobQueue.JOB_STATES.PENDING)
        end)
        
        it("should process jobs in priority order", function()
            local results = {}
            
            -- Add jobs with different priorities
            jobQueue:addJob({id = "low"}, 10, function(success, result)
                table.insert(results, "low")
            end)
            
            jobQueue:addJob({id = "high"}, 1, function(success, result)
                table.insert(results, "high")
            end)
            
            -- Start processing
            jobQueue:start()
            
            -- Wait for jobs to complete
            wait(2)
            
            -- High priority job should complete first
            expect(results[1]).to.equal("high")
            expect(results[2]).to.equal("low")
        end)
        
        it("should respect max concurrent jobs", function()
            local activeCount = 0
            local maxActive = 0
            
            -- Add more jobs than maxConcurrentJobs
            for i = 1, 4 do
                jobQueue:addJob({id = i}, 1, function()
                    activeCount = activeCount + 1
                    maxActive = math.max(maxActive, activeCount)
                    wait(0.5) -- Simulate work
                    activeCount = activeCount - 1
                end)
            end
            
            -- Start processing
            jobQueue:start()
            
            -- Wait for some processing
            wait(1)
            
            -- Should not exceed maxConcurrentJobs (2)
            expect(maxActive).to.equal(2)
        end)
        
        it("should retry failed jobs", function()
            local attempts = 0
            local jobId = jobQueue:addJob(
                {shouldFail = true}, 
                1, 
                function(success, result)
                    attempts = attempts + 1
                end
            )
            
            jobQueue:start()
            wait(2) -- Wait for retries
            
            -- Should have retried the max number of times
            local job = jobQueue:getJobStatus(jobId)
            expect(job.attempts).to.equal(2) -- Initial + 1 retry
            expect(job.status).to.equal(JobQueue.JOB_STATES.FAILED)
        end)
        
        it("should cancel jobs", function()
            local jobId = jobQueue:addJob({id = "to_cancel"}, 1)
            
            -- Cancel before starting
            local success, msg = jobQueue:cancelJob(jobId)
            expect(success).to.equal(true)
            
            -- Try to cancel non-existent job
            success, msg = jobQueue:cancelJob("nonexistent")
            expect(success).to.equal(false)
        end)
        
        it("should provide queue statistics", function()
            -- Add some jobs
            for i = 1, 3 do
                jobQueue:addJob({id = i}, i)
            end
            
            local stats = jobQueue:getStats()
            expect(stats.pending).to.equal(3)
            expect(stats.active).to.equal(0)
            expect(stats.completed).to.equal(0)
            
            -- Start processing
            jobQueue:start()
            wait(1) -- Let some processing happen
            
            stats = jobQueue:getStats()
            expect(stats.active).to.be.lessThanOrEqualTo(2) -- maxConcurrentJobs
        end)
        
        it("should clear completed jobs", function()
            -- Add and complete some jobs
            for i = 1, 3 do
                local jobId = jobQueue:addJob({id = i}, 1)
            end
            
            jobQueue:start()
            wait(2) -- Let jobs complete
            
            -- Clear completed jobs
            local cleared = jobQueue:clearCompleted()
            expect(cleared).to.equal(3)
            expect(#jobQueue.completedJobs).to.equal(0)
        end)
    end)
end
