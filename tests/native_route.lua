-- Loaded through native mGBA's Scripting window. Only controller input is written.
-- Game address and navigation tiles are generated from this build by native_check.py.
-- Official API: https://mgba.io/docs/scripting.html
local elapsed = 0
local callback
local function byte(offset) return emu:read8(gameAddress + offset) end
local function flag(mask) return (emu:read16(gameAddress + 20) & mask) ~= 0 end
local function choose(cursor, desired) return cursor == desired and 1 or 128 end
local function walk(map,x,y,tx,ty)
    if x == tx and y == ty then return 1 end
    local queue = {{x,y,0}}
    local seen = {[y*24+x] = true}
    local head = 1
    while head <= #queue do
        local node = queue[head]; head = head + 1
        for _, delta in ipairs({{1,0,16},{-1,0,32},{0,1,128},{0,-1,64}}) do
            local nx, ny = node[1]+delta[1], node[2]+delta[2]
            local key = ny*24+nx
            if nx >= 0 and nx < 24 and ny >= 0 and ny < 18 and not seen[key] then
                local tile = maps[map+1][ny+1][nx+1]
                if tile ~= 2 and tile ~= 4 then
                    seen[key] = true
                    local first = node[3] == 0 and delta[3] or node[3]
                    if nx == tx and ny == ty then return first end
                    queue[#queue+1] = {nx,ny,first}
                end
            end
        end
    end
    error('No controller route to the next quest location')
end
local function input()
    local scene,cursor = byte(360),byte(362)
    if scene == 0 or scene == 1 or scene == 3 then return 1 end
    if scene == 4 then
        if byte(373) ~= 0 then return 1 end
        if byte(366) == 0 and byte(40 + byte(365)*10) <= 22 and byte(37) == 0 then
            return choose(cursor,4) -- Retreat to a clinic when supplies run out.
        end
        local hp = byte(40 + byte(365)*10)
        return choose(cursor,(hp <= 22 and byte(37) > 0) and 3 or 0)
    end
    if scene == 5 then
        local burstPP = byte(42 + byte(365)*10)
        return choose(cursor,burstPP > 0 and 1 or 0)
    end
    if scene ~= 2 then return 2 end
    local map,x,y = byte(30),byte(31),byte(32)
    local tx,ty
    if map == 0 then
        if not flag(2) then tx,ty = 4,3
        elseif not flag(4) then tx,ty = 6,9
        else tx,ty = 18,13 end
    elseif map == 1 then
        local level,hp = byte(39),byte(40)
        local coins = emu:read16(gameAddress + 26)
        if hp < (28 + level*3)*3/4 then tx,ty = 6,8
        elseif byte(37) < 4 and coins >= 30 then tx,ty = 10,12
        elseif level < 8 then
            tx,ty = (x == 18 and y == 10) and 19 or 18,10
        else tx,ty = 14,7 end
    else
        if not flag(8) then tx,ty = 11,2
        elseif not flag(16) then tx,ty = 5,6
        elseif not flag(32) then tx,ty = 17,10
        else tx,ty = 11,2 end
    end
    return walk(map,x,y,tx,ty)
end
callback = callbacks:add('frame',function()
    elapsed = elapsed + 1
    if elapsed % 20 == 1 then
        if flag(64) then
            emu:setKeys(0); callbacks:remove(callback)
            console:log('PASS: fresh native cartridge, starter, courier route, Muni, both relays, and Cognition gym.')
        elseif elapsed > 18000 then
            emu:setKeys(0); callbacks:remove(callback)
            console:error('Native route check timed out. Inspect the current screen.')
        else emu:setKeys(input()) end
    elseif elapsed % 20 == 6 then emu:setKeys(0) end
end)
emu:setKeys(0)
console:log('Fresh-cartridge route check started. Input only; no progress, stats, or RAM writes.')
