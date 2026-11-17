-- Carga Nube Tune en una pestaña nueva, renderiza cada caso y cierra la pestaña.
-- Uso: REAPER -nonewinst tests/render_cases.lua   (escribe tests/out/*.wav y tests/out/log.txt)
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local FX = "JS:Nube Tune/nube_tune.jsfx"
local PRESET, DIAG, LEARN = 21, 22, 20
os.execute('mkdir -p "' .. OUT .. '"')
local logf = io.open(OUT .. "/log.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t+1] = tostring(v) end logf:write(table.concat(t, " "), "\n") logf:flush() end
-- opciones desde run.sh (REAPER no hereda las variables de entorno)
local of = io.open(OUT .. "/only.txt"); local only = of and of:read("*l") or nil; if of then of:close() end
if only == "" then only = nil end

-- slider N = parámetro N-1 (todos lineales). Base: velocidad 0 (corrección instantánea)
local function P(t) local r = {[1] = 0} for k, v in pairs(t or {}) do r[k] = v end return r end
-- caso: {nombre, señal, parámetros, opciones}  opciones: sr, midi = {{nota, t0, t1}, ...}, learn = true
local CASES = {
  {"sine430",        "sine430.wav",  P{}},
  {"v430",           "vowel430.wav", P{}},
  {"v213",           "vowel213.wav", P{}},
  {"v213_amin",      "vowel213.wav", P{[12] = 9, [13] = 2}},
  {"v213_emaj",      "vowel213.wav", P{[12] = 4, [13] = 1}},
  {"v213_custom",    "vowel213.wav", P{[13] = 12, [14] = 2 ^ 7 + 2 ^ 0}},        -- solo G y C
  {"v430_tr12",      "vowel430.wav", P{[5] = 12}},
  {"v430_trm12",     "vowel430.wav", P{[5] = -12}},
  {"v430_tr7",       "vowel430.wav", P{[5] = 7}},
  {"v430_a432",      "vowel430.wav", P{[6] = 432}},
  {"v110",           "vowel110.wav", P{[10] = 0}},
  {"v110_tr4",       "vowel110.wav", P{[5] = 4}},
  {"v110_tr4_follow","vowel110.wav", P{[5] = 4, [18] = 1}},
  {"v110_fp3",       "vowel110.wav", P{[4] = 3}},
  {"v110_fm3",       "vowel110.wav", P{[4] = -3}},
  {"v110_trm7",      "vowel110.wav", P{[5] = -7}},
  {"onset_s0",       "onset225.wav", P{}},
  {"onset_s100",     "onset225.wav", P{[1] = 100}},
  {"flex100",        "onset225.wav", P{[3] = 100}},
  {"flex50",         "onset225.wav", P{[3] = 50}},
  {"vib_s0",         "vib220.wav",   P{}},
  {"vib_s200",       "vib220.wav",   P{[1] = 200}},
  {"vib_human",      "vib220.wav",   P{[2] = 100}},
  {"vib_add",        "vowel440.wav", P{[7] = 50, [8] = 6, [9] = 0}},
  {"vib_add_delay",  "vowel440.wav", P{[7] = 50, [8] = 6, [9] = 1000}},
  {"midi_exact",     "vowel213.wav", P{[19] = 2}, {midi = {{64, 0, 3.3}}}},
  {"midi_scale",     "vowel213.wav", P{[19] = 1}, {midi = {{48, 0, 3.3}, {57, 0, 3.3}}}},
  {"midi_exact_seq", "vowel213.wav", P{[19] = 2}, {midi = {{60, 0.25, 1.5}, {67, 1.5, 3.3}}}},
  {"noise",          "noise.wav",    P{}},
  {"mix0",           "vowel213.wav", P{[10] = 0}},
  {"mix50",          "vowel213.wav", P{[10] = 50, [12] = 9, [13] = 2}},
  {"out6",           "vowel440.wav", P{[11] = 6}},
  {"intune",         "vowel440.wav", P{}},
  {"silence",        "silence.wav",  P{}},
  {"glide",          "glide.wav",    P{}},
  {"v84_bajo",       "vowel84.wav",  P{[15] = 2}},
  {"v84_soprano",    "vowel84.wav",  P{[15] = 0}},
  {"sr44",           "vowel430_44k.wav", P{}, {sr = 44100}},
  {"sr96",           "vowel430_96k.wav", P{}, {sr = 96000}},
  {"learn_em",       "melody_em.wav", P{[20] = 1}, {learn = true}},
  {"voz_seca",       "voz.wav",      P{[10] = 0}},
  {"voz_hard",       "voz.wav",      P{[21] = 3}},
  {"voz_natural",    "voz.wav",      P{[21] = 1}},
  {"voz_pop",        "voz.wav",      P{[21] = 2}},
  {"voz_tr12",       "voz.wav",      P{[21] = 8}},
  {"voz_trm12",      "voz.wav",      P{[21] = 7}},
}
for p = 4, 13 do if p ~= 7 and p ~= 8 then CASES[#CASES + 1] = {"preset" .. p, "voz.wav", P{[21] = p}} end end

local PREV = reaper.EnumProjects(-1)
reaper.Main_OnCommand(40859, 0) -- nueva pestaña
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr)
local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0)
local mtr = nil

for _, c in ipairs(CASES) do
  local name, src, params, opt = c[1], c[2], c[3], c[4] or {}
  if not only or name:find(only) then
    local sr = opt.sr or 48000
    reaper.GetSetProjectInfo(0, "PROJECT_SRATE", sr, true)
    reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
    local s = reaper.PCM_Source_CreateFromFile(ROOT .. "/signals/" .. src)
    reaper.SetMediaItemTake_Source(take, s)
    local len = reaper.GetMediaSourceLength(s)
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", len)
    reaper.SetMediaItemInfo_Value(item, "D_FADEINLEN", 0); reaper.SetMediaItemInfo_Value(item, "D_FADEOUTLEN", 0)
    reaper.UpdateItemInProject(item)
    while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
    if mtr then reaper.DeleteTrack(mtr); mtr = nil end
    local fx = reaper.TrackFX_AddByName(tr, FX, false, -1)
    if fx < 0 then log("ERROR no cargó el FX") break end
    if params[PRESET] then reaper.TrackFX_SetParam(tr, fx, PRESET - 1, params[PRESET]) end
    for s_, v in pairs(params) do if s_ ~= PRESET then reaper.TrackFX_SetParam(tr, fx, s_ - 1, v) end end
    if opt.midi then
      -- pista MIDI que manda solo MIDI a la del afinador
      reaper.InsertTrackAtIndex(1, false); mtr = reaper.GetTrack(0, 1)
      local mi = reaper.CreateNewMIDIItemInProj(mtr, 0, len, false)
      local mt = reaper.GetActiveTake(mi)
      for _, nt in ipairs(opt.midi) do
        local p0 = reaper.MIDI_GetPPQPosFromProjTime(mt, nt[2]); local p1 = reaper.MIDI_GetPPQPosFromProjTime(mt, nt[3])
        reaper.MIDI_InsertNote(mt, false, false, p0, p1, 0, nt[1], 100, true)
      end
      reaper.MIDI_Sort(mt)
      local snd = reaper.CreateTrackSend(mtr, tr)
      reaper.SetTrackSendInfo_Value(mtr, 0, snd, "I_SRCCHAN", -1)
      reaper.SetMediaTrackInfo_Value(mtr, "B_MAINSEND", 0)
    end
    local file = OUT .. "/" .. name .. ".wav"
    os.remove(file)
    reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
    reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
    reaper.GetSetProjectInfo(0, "RENDER_SRATE", sr, true)
    reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
    reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
    reaper.Main_OnCommand(42230, 0)
    local extra = ""
    if opt.learn then
      reaper.TrackFX_SetParam(tr, fx, LEARN - 1, 0)
      local _, k = reaper.TrackFX_GetFormattedParamValue(tr, fx, 11, ""); local _, e = reaper.TrackFX_GetFormattedParamValue(tr, fx, 12, "")
      extra = " | tonalidad=" .. k .. " | escala=" .. e
    end
    local vals = {}
    for _, k in ipairs({1, 2, 3, 4, 5, 10, 13, 18}) do local _, v = reaper.TrackFX_GetFormattedParamValue(tr, fx, k - 1, ""); vals[#vals + 1] = v end
    log("caso", name, table.concat(vals, " | ") .. " | diag=" .. math.floor(reaper.TrackFX_GetParam(tr, fx, DIAG - 1)) .. extra)
  end
end
if mtr then reaper.DeleteTrack(mtr) end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_test.rpp", 0)
reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_test.rpp")
reaper.Main_OnCommand(40860, 0) -- cerrar pestaña
if PREV and reaper.ValidatePtr(PREV, "ReaProject*") then reaper.SelectProjectInstance(PREV) end
log("done")
logf:close()
