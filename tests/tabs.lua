-- Lista las pestañas abiertas en tests/out/tabs.txt; con tests/out/tabs_close.txt = "1" cierra SOLO las de las pruebas de
-- Nube Tune (proyecto guardado en esta carpeta tests/out, o primera pista "Nube Tune demo"). No toca las demás.
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local c = io.open(OUT .. "/tabs_close.txt"); local close = c and c:read("l") == "1"; if c then c:close() end
local f = io.open(OUT .. "/tabs.txt", "w")
local cur = reaper.EnumProjects(-1, "")
local list = {}
local i = 0
while true do
  local p, path = reaper.EnumProjects(i, "")
  if not p then break end
  local tr = reaper.GetTrack(p, 0); local name = ""
  if tr then _, name = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false) end
  local m = path:find(OUT, 1, true) == 1 or name == "Nube Tune demo"
  f:write(i, " | ", path == "" and "(sin guardar)" or path, " | pista 1: ", name, " | pistas: ", reaper.CountTracks(p), m and " | DE LAS PRUEBAS" or "", "\n")
  list[#list + 1] = {p = p, mine = m}
  i = i + 1
end
if close then
  for _, t in ipairs(list) do
    if t.mine then
      reaper.SelectProjectInstance(t.p); reaper.OnStopButton()
      reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_close.rpp", 0); reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_close.rpp")
      reaper.Main_OnCommand(40860, 0)
    end
  end
  f:write("cerradas\n")
end
f:write("done\n"); f:close()
