"""Set a Workshop item's description for one language via the Steamworks flat API.
pdx-workshop-manager only writes the default (english) description; run this from its folder
(steam_appid.txt, steam_api64.dll) with Steam running.

usage: workshop_lang.py <dll> <appid> <fileid> <lang> <description-file> [--submit] [--note FILE]
Without --submit: init Steam, open an update handle, set language + description, do NOT submit.
"""
import ctypes as C
import os
import sys
import time
from pathlib import Path

dll_path, appid, fileid, lang, desc_file = sys.argv[1:6]
submit = '--submit' in sys.argv
note = None
if '--note' in sys.argv:
    note = Path(sys.argv[sys.argv.index('--note') + 1]).read_text(encoding='utf-8')
appid, fileid = int(appid), int(fileid)
desc = Path(desc_file).read_text(encoding='utf-8')

os.environ['SteamAppId'] = str(appid)
api = C.CDLL(dll_path)
err = C.create_string_buffer(1024)
api.SteamAPI_InitFlat.restype = C.c_int
r = api.SteamAPI_InitFlat(err)
print('InitFlat:', r, err.value.decode(errors='replace'))
if r != 0:
    sys.exit(1)

api.SteamAPI_SteamUGC_v021.restype = C.c_void_p
api.SteamAPI_SteamUtils_v010.restype = C.c_void_p
ugc = C.c_void_p(api.SteamAPI_SteamUGC_v021())
utils = C.c_void_p(api.SteamAPI_SteamUtils_v010())
print('ugc/utils:', bool(ugc.value), bool(utils.value))

f = api.SteamAPI_ISteamUGC_StartItemUpdate
f.restype, f.argtypes = C.c_uint64, [C.c_void_p, C.c_uint32, C.c_uint64]
h = f(ugc, appid, fileid)
print('handle:', hex(h))

for name, arg in (('SetItemUpdateLanguage', lang), ('SetItemDescription', desc)):
    g = getattr(api, 'SteamAPI_ISteamUGC_' + name)
    g.restype, g.argtypes = C.c_bool, [C.c_void_p, C.c_uint64, C.c_char_p]
    print(name, g(ugc, h, arg.encode('utf-8')))

if not submit:
    print('dry run: not submitted')
    api.SteamAPI_Shutdown()
    sys.exit(0)

s = api.SteamAPI_ISteamUGC_SubmitItemUpdate
s.restype, s.argtypes = C.c_uint64, [C.c_void_p, C.c_uint64, C.c_char_p]
call = s(ugc, h, note.encode('utf-8') if note else None)
print('call:', hex(call))

done = api.SteamAPI_ISteamUtils_IsAPICallCompleted
done.restype, done.argtypes = C.c_bool, [C.c_void_p, C.c_uint64, C.POINTER(C.c_bool)]
res = api.SteamAPI_ISteamUtils_GetAPICallResult
res.restype = C.c_bool
res.argtypes = [C.c_void_p, C.c_uint64, C.c_void_p, C.c_int, C.c_int, C.POINTER(C.c_bool)]
failed = C.c_bool()
for _ in range(600):
    api.SteamAPI_RunCallbacks()
    if done(utils, call, C.byref(failed)):
        break
    time.sleep(0.1)
else:
    print('timeout')
    sys.exit(1)


class SubmitItemUpdateResult(C.Structure):  # k_iCallback 3404
    _pack_ = 8
    _fields_ = [('eResult', C.c_int), ('needsLegal', C.c_bool), ('fileId', C.c_uint64)]


out = SubmitItemUpdateResult()
ok = res(utils, call, C.byref(out), C.sizeof(out), 3404, C.byref(failed))
print('result:', ok, 'failed:', failed.value, 'EResult:', out.eResult, 'legal:', out.needsLegal, 'id:', out.fileId)
api.SteamAPI_Shutdown()
sys.exit(0 if ok and out.eResult == 1 else 1)
