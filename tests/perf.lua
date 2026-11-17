-- CPU: 10 instancias sobre 30 s de voz real, en tres configuraciones (rango tenor, rango grave, transponer -12 + formantes).
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
os.execute('mkdir -p "' .. OUT .. '"')
local f = io.open(OUT .. "/perf.txt", "w")
local PREV = reaper.EnumProjects(-1)
reaper.Main_OnCommand(40859, 0)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr); local take = reaper.AddTakeToMediaItem(item)
local src = reaper.PCM_Source_CreateFromFile(ROOT .. "/signals/voz.wav")
reaper.SetMediaItemTake_Source(take, src)
local LEN = reaper.GetMediaSourceLength(src)
reaper.SetMediaItemInfo_Value(item, "D_LENGTH", LEN)
local function render(name, nfx, params)
  while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
  for k = 1, nfx do
    local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Tune/nube_tune.jsfx", false, -1)
    for p, v in pairs(params) do reaper.TrackFX_SetParam(tr, fx, p - 1, v) end
  end
  os.remove(OUT .. "/" .. name .. ".wav")
  reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
  local t0 = reaper.time_precise(); reaper.Main_OnCommand(42230, 0); return reaper.time_precise() - t0
end
local t_empty = render("perf_vacio", 0, {})
for _, c in ipairs({{"tenor (por defecto)", {}}, {"rango grave", {[15] = 2}}, {"instrumento grave + transponer -12 + formantes +3", {[15] = 3, [5] = -12, [4] = 3}}}) do
  local t = render("perf_x", 10, c[2])
  f:write(string.format("%s: %.2f %% de un nucleo por instancia\n", c[1], (t - t_empty) / LEN / 10 * 100))
end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_perf.rpp", 0); reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_perf.rpp"); reaper.Main_OnCommand(40860, 0)
if PREV and reaper.ValidatePtr(PREV, "ReaProject*") then reaper.SelectProjectInstance(PREV) end
f:write("done\n"); f:close()
