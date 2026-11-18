-- Nube Tune - ayudante: deja que el plugin mueva la reproducción con un clic en el editor de notas.
-- Un JSFX no puede mover el cursor de REAPER; el plugin escribe el tiempo pedido en la memoria compartida
-- "NubeTune" (gmem[0] = segundos, gmem[1] = número de pedido) y este script, en segundo plano, lo aplica.
-- gmem[2] = latido (time_precise): así el plugin sabe si el ayudante está corriendo.
-- La primera vez se agrega a Scripts/__startup.lua para arrancar solo con REAPER.
reaper.gmem_attach("NubeTune")
local hb = reaper.gmem_read(2)
if hb > 0 and math.abs(reaper.time_precise() - hb) < 1 then return end   -- ya hay uno corriendo

local me = debug.getinfo(1, "S").source:sub(2)
local su = reaper.GetResourcePath() .. "/Scripts/__startup.lua"
local f = io.open(su); local txt = f and f:read("a") or ""; if f then f:close() end
if not txt:find("Nube Tune - ayudante", 1, true) then
  f = io.open(su, "a")
  if f then f:write("\n-- Nube Tune - ayudante (mover la reproducción desde el plugin)\ndofile([[" .. me .. "]])\n"); f:close() end
end

local last = reaper.gmem_read(1)
local function loop()
  reaper.gmem_write(2, reaper.time_precise())
  local id = reaper.gmem_read(1)
  if id ~= last then
    last = id
    reaper.SetEditCurPos(math.max(reaper.gmem_read(0), 0), false, true)   -- con reproducción: salta ahí
  end
  reaper.defer(loop)
end
loop()
