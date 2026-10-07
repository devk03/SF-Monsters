-- Native mGBA benchmark controls. Controller writes only; no game RAM edits.
-- API: https://mgba.io/docs/scripting.html
local code = emu:getGameCode()
assert(code == BENCH_GAME_CODE or code == 'AGB-' .. BENCH_GAME_CODE, 'Wrong cartridge for this benchmark')
Bench = {queue={}, tick=0, index=1, remaining=0, capture=nil}
local trace = assert(io.open(BENCH_OUTPUT .. '/trace.csv', 'w'))
trace:write('frame,keys,display_control,bg0_x,bg0_y,bg1_x,bg1_y,bg2_x,bg2_y\n')
function Bench.play(sequence)
    assert(not Bench.capture, 'Finish capture before replacing the controller sequence')
    Bench.queue, Bench.index, Bench.remaining = sequence, 1, 0
    for _, step in ipairs(sequence) do
        assert(step[1] >= 0 and step[1] < 1024 and step[2] > 0, 'Invalid controller step')
    end
end
function Bench.tap(mask)
    Bench.play({{mask,8},{0,30}})
end
function Bench.begin(name, frames)
    assert(BENCH_SCENARIOS[name], 'Scenario directory was not prepared')
    assert(not Bench.capture, 'A capture is already running')
    assert(frames >= 1 and frames <= 3600, 'Capture must be at most 3600 frames')
    Bench.capture = {name=name, total=frames, count=0, first=emu:currentFrame()}
    console:log('Capture started: ' .. name)
end
function Bench.finish()
    emu:setKeys(0)
    if Bench.capture then
        local capture = Bench.capture
        local meta = assert(io.open(BENCH_OUTPUT .. '/' .. capture.name .. '/capture.csv','w'))
        meta:write('first_frame,frames,frequency,cycles_per_frame\n')
        meta:write(string.format('%d,%d,%d,%d\n',capture.first,capture.count,
            emu:frequency(),emu:frameCycles()))
        meta:close()
        console:log('Capture completed: ' .. capture.name .. ' (' .. capture.count .. ' frames)')
        Bench.capture = nil
    end
    trace:flush()
end
local callback
callback = callbacks:add('frame',function()
    Bench.tick = Bench.tick + 1
    if Bench.remaining == 0 then
        local step = Bench.queue[Bench.index]
        if step then
            emu:setKeys(step[1]); Bench.remaining = step[2]
            Bench.index = Bench.index + 1
        else emu:setKeys(0) end
    end
    if Bench.remaining > 0 then Bench.remaining = Bench.remaining - 1 end
    trace:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d\n',
        emu:currentFrame(),emu:getKeys(),emu:read16(0x04000000),
        emu.memory.io:read16(0x10),emu.memory.io:read16(0x12),
        emu.memory.io:read16(0x14),emu.memory.io:read16(0x16),
        emu.memory.io:read16(0x18),emu.memory.io:read16(0x1a)))
    if Bench.capture then
        local capture = Bench.capture
        emu:screenshot(string.format('%s/%s/%06d.png',BENCH_OUTPUT,capture.name,capture.count))
        capture.count = capture.count + 1
        if capture.count == capture.total then Bench.finish() end
    end
    if Bench.tick % 60 == 0 then trace:flush() end
end)
function Bench.stop()
    Bench.finish(); callbacks:remove(callback); trace:close()
    console:log('Benchmark controller stopped')
end
console:log('Benchmark ready: Bench.tap(mask), Bench.play({{mask,frames},...}), Bench.begin(name,frames)')
