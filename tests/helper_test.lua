-- Ayudante temporal para las pruebas de interfaz: el mismo bucle que 'Nube Tune - ayudante.lua' pero sin
-- agregarse al arranque de REAPER. Se apaga solo 3 minutos después del último lanzamiento (gmem[4] = plazo).
reaper.gmem_attach("NubeTune")
reaper.gmem_write(4, reaper.time_precise() + 180)
local hb = reaper.gmem_read(2)
if hb > 0 and math.abs(reaper.time_precise() - hb) < 1 then return end   -- ya corre uno: solo se extendió su plazo
local last = reaper.gmem_read(1)
local function loop()
  reaper.gmem_write(2, reaper.time_precise())
  local id = reaper.gmem_read(1)
  if id ~= last then last = id; reaper.SetEditCurPos(math.max(reaper.gmem_read(0), 0), false, true) end
  if reaper.time_precise() < reaper.gmem_read(4) then reaper.defer(loop) else reaper.gmem_write(2, 0) end
end
loop()
