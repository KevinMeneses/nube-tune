-- Detiene y cierra la pestaña de demo sin preguntar. Busca SU pestaña (pista 1 = "Nube Tune demo"):
-- si hay otra sesión usando REAPER, nunca cierra la pestaña activa de otro.
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local mine = nil
local i = 0
while true do
  local p = reaper.EnumProjects(i); if not p then break end
  local tr = reaper.GetTrack(p, 0)
  if tr then local _, n = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false); if n == "Nube Tune demo" then mine = p end end
  i = i + 1
end
if mine then
  reaper.SelectProjectInstance(mine)
  reaper.OnStopButton()
  reaper.Main_SaveProjectEx(mine, OUT .. "/_tmp_ui.rpp", 0)
  reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_ui.rpp")
  reaper.Main_OnCommand(40860, 0)
end
