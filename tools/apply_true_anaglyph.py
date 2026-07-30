#!/usr/bin/env python3
"""Apply true binocular red/cyan rendering to a clean ECWolf master tree."""
from pathlib import Path

FILES = [
    Path('src/c_cvars.cpp'),
    Path('src/c_cvars.h'),
    Path('src/wl_draw.cpp'),
    Path('src/wl_draw.h'),
    Path('src/wl_menu.cpp'),
    Path('src/wl_parallax.cpp'),
]


def load(path):
    raw = path.read_bytes()
    eol = b'\r\n' if b'\r\n' in raw else b'\n'
    text = raw.decode('utf-8').replace('\r\n', '\n')
    if '\r' in text:
        raise RuntimeError(f'{path}: unsupported lone CR')
    return text, eol


def save(path, text, eol):
    path.write_bytes(text.replace('\n', eol.decode()).encode('utf-8'))


def replace_once(text, old, new, path, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{path}: expected one {label} anchor, found {count}')
    return text.replace(old, new, 1)


def main():
    for path in FILES:
        if not path.is_file():
            raise RuntimeError(f'missing {path}; run from ECWolf repository root')

    loaded = {path: list(load(path)) for path in FILES}
    if 'r_anaglyph_convergence' in loaded[Path('src/c_cvars.h')][0]:
        print('True anaglyph implementation is already applied.')
        return

    path = Path('src/c_cvars.cpp')
    text, eol = loaded[path]
    text = replace_once(text,
        'bool vid_fullscreen = false;\nbool vid_vsync = false;\nbool quitonescape = false;',
        'bool vid_fullscreen = false;\nbool vid_vsync = false;\n'
        'bool r_anaglyph = false;\nbool r_anaglyph_swapeyes = false;\n'
        'int r_anaglyph_separation = 8;\nint r_anaglyph_convergence = 16;\n'
        'bool quitonescape = false;', path, 'renderer globals')
    text = replace_once(text,
        '\tconfig.CreateSetting("Vid_FullScreen", false);\n'
        '\tconfig.CreateSetting("Vid_Aspect", ASPECT_NONE);\n'
        '\tconfig.CreateSetting("Vid_Vsync", false);\n'
        '\tconfig.CreateSetting("FullScreenWidth", fullScreenWidth);',
        '\tconfig.CreateSetting("Vid_FullScreen", false);\n'
        '\tconfig.CreateSetting("Vid_Aspect", ASPECT_NONE);\n'
        '\tconfig.CreateSetting("Vid_Vsync", false);\n'
        '\tconfig.CreateSetting("R_Anaglyph", false);\n'
        '\tconfig.CreateSetting("R_AnaglyphSwapEyes", false);\n'
        '\tconfig.CreateSetting("R_AnaglyphSeparation", 8);\n'
        '\tconfig.CreateSetting("R_AnaglyphConvergence", 16);\n'
        '\tconfig.CreateSetting("FullScreenWidth", fullScreenWidth);', path, 'config creation')
    text = replace_once(text,
        '\tvid_fullscreen = config.GetSetting("Vid_FullScreen")->GetInteger() != 0;\n'
        '\tvid_aspect = static_cast<Aspect>(config.GetSetting("Vid_Aspect")->GetInteger());\n'
        '\tvid_vsync = config.GetSetting("Vid_Vsync")->GetInteger() != 0;\n'
        '\tfullScreenWidth = config.GetSetting("FullScreenWidth")->GetInteger();',
        '\tvid_fullscreen = config.GetSetting("Vid_FullScreen")->GetInteger() != 0;\n'
        '\tvid_aspect = static_cast<Aspect>(config.GetSetting("Vid_Aspect")->GetInteger());\n'
        '\tvid_vsync = config.GetSetting("Vid_Vsync")->GetInteger() != 0;\n'
        '\tr_anaglyph = config.GetSetting("R_Anaglyph")->GetInteger() != 0;\n'
        '\tr_anaglyph_swapeyes = config.GetSetting("R_AnaglyphSwapEyes")->GetInteger() != 0;\n'
        '\tr_anaglyph_separation = config.GetSetting("R_AnaglyphSeparation")->GetInteger();\n'
        '\tr_anaglyph_convergence = config.GetSetting("R_AnaglyphConvergence")->GetInteger();\n'
        '\tfullScreenWidth = config.GetSetting("FullScreenWidth")->GetInteger();', path, 'config loading')
    text = replace_once(text,
        '\tif(viewsize<4) viewsize=4;\n\telse if(viewsize>21) viewsize=21;\n\n'
        '\t// Carry over the unified screenWidth/screenHeight from previous versions',
        '\tif(viewsize<4) viewsize=4;\n\telse if(viewsize>21) viewsize=21;\n\n'
        '\tif(r_anaglyph_separation < 0) r_anaglyph_separation = 0;\n'
        '\telse if(r_anaglyph_separation > 32) r_anaglyph_separation = 32;\n'
        '\tif(r_anaglyph_convergence < 1) r_anaglyph_convergence = 1;\n'
        '\telse if(r_anaglyph_convergence > 64) r_anaglyph_convergence = 64;\n\n'
        '\t// Carry over the unified screenWidth/screenHeight from previous versions', path, 'stereo clamps')
    text = replace_once(text,
        '\tconfig.GetSetting("Vid_FullScreen")->SetValue(vid_fullscreen);\n'
        '\tconfig.GetSetting("Vid_Aspect")->SetValue(vid_aspect);\n'
        '\tconfig.GetSetting("Vid_Vsync")->SetValue(vid_vsync);\n'
        '\tconfig.GetSetting("FullScreenWidth")->SetValue(fullScreenWidth);',
        '\tconfig.GetSetting("Vid_FullScreen")->SetValue(vid_fullscreen);\n'
        '\tconfig.GetSetting("Vid_Aspect")->SetValue(vid_aspect);\n'
        '\tconfig.GetSetting("Vid_Vsync")->SetValue(vid_vsync);\n'
        '\tconfig.GetSetting("R_Anaglyph")->SetValue(r_anaglyph);\n'
        '\tconfig.GetSetting("R_AnaglyphSwapEyes")->SetValue(r_anaglyph_swapeyes);\n'
        '\tconfig.GetSetting("R_AnaglyphSeparation")->SetValue(r_anaglyph_separation);\n'
        '\tconfig.GetSetting("R_AnaglyphConvergence")->SetValue(r_anaglyph_convergence);\n'
        '\tconfig.GetSetting("FullScreenWidth")->SetValue(fullScreenWidth);', path, 'config writing')
    loaded[path][0] = text

    path = Path('src/c_cvars.h')
    text, eol = loaded[path]
    text = replace_once(text,
        'extern bool\t\tvid_fullscreen;\nextern Aspect\tvid_aspect;\nextern bool\t\tvid_vsync;\nextern bool\t\tquitonescape;',
        'extern bool\t\tvid_fullscreen;\nextern Aspect\tvid_aspect;\nextern bool\t\tvid_vsync;\n'
        'extern bool\t\tr_anaglyph;\nextern bool\t\tr_anaglyph_swapeyes;\n'
        'extern int\t\tr_anaglyph_separation;\nextern int\t\tr_anaglyph_convergence;\n'
        'extern bool\t\tquitonescape;', path, 'renderer declarations')
    loaded[path][0] = text

    path = Path('src/wl_draw.h')
    text, eol = loaded[path]
    text = replace_once(text,
        'extern  fixed   viewx,viewy;                    // the focal point\nextern  fixed   viewsin,viewcos;',
        'extern  fixed   viewx,viewy;                    // the focal point\n'
        'extern  angle_t viewangle;\nextern  fixed   viewsin,viewcos;', path, 'view angle declaration')
    loaded[path][0] = text

    path = Path('src/wl_parallax.cpp')
    text, eol = loaded[path]
    text = replace_once(text,
        '\tconst int midangle = (players[ConsolePlayer].camera->angle + scroll)>>ANGLETOFINESHIFT;',
        '\t// Use the active eye angle. At finite convergence, the sky is at infinity\n'
        '\t// and therefore retains the expected uncrossed disparity.\n'
        '\tconst int midangle = (viewangle + scroll)>>ANGLETOFINESHIFT;', path, 'parallax eye angle')
    loaded[path][0] = text

    path = Path('src/wl_draw.cpp')
    text, eol = loaded[path]
    text = replace_once(text,
        '#include "r_data/colormaps.h"\n#include "v_video.h"\n#include "wl_cloudsky.h"',
        '#include "r_data/colormaps.h"\n#include "v_video.h"\n#include "v_palette.h"\n#include "wl_cloudsky.h"', path, 'palette include')
    text = replace_once(text,
        '/*static*/ byte *vbuf = NULL;\nunsigned vbufPitch = 0;\n\nint32_t\tlasttimecount;',
        '''/*static*/ byte *vbuf = NULL;
unsigned vbufPitch = 0;

static fixed anaglyphEyeOffset = 0;
static angle_t anaglyphEyeYaw = 0;
static TUniquePtr<byte[]> anaglyphLeftEye;
static unsigned int anaglyphLeftEyeSize = 0;
static byte anaglyphColorMap[256][256];
static uint32_t anaglyphPaletteHash = 0;
static bool anaglyphColorMapValid = false;

static uint32_t GetAnaglyphPaletteHash()
{
\tuint32_t hash = 2166136261u;
\tfor(unsigned int i = 0;i < 256;++i)
\t{
\t\thash ^= GPalette.BaseColors[i].d;
\t\thash *= 16777619u;
\t}
\treturn hash;
}

static void BuildAnaglyphColorMap()
{
\tconst uint32_t *palette = reinterpret_cast<const uint32_t *>(GPalette.BaseColors);
\tfor(unsigned int redEye = 0;redEye < 256;++redEye)
\t{
\t\tfor(unsigned int cyanEye = 0;cyanEye < 256;++cyanEye)
\t\t{
\t\t\tconst PalEntry &red = GPalette.BaseColors[redEye];
\t\t\tconst PalEntry &cyan = GPalette.BaseColors[cyanEye];
\t\t\tanaglyphColorMap[redEye][cyanEye] = BestColor(palette, red.r, cyan.g, cyan.b, 0, 256);
\t\t}
\t}
\tanaglyphPaletteHash = GetAnaglyphPaletteHash();
\tanaglyphColorMapValid = true;
}

static void ComposeAnaglyph(byte *target, unsigned int targetPitch, const byte *leftEye)
{
\tconst uint32_t paletteHash = GetAnaglyphPaletteHash();
\tif(!anaglyphColorMapValid || paletteHash != anaglyphPaletteHash)
\t\tBuildAnaglyphColorMap();

\tfor(int y = 0;y < viewheight;++y)
\t{
\t\tbyte *rightRow = target + y*targetPitch;
\t\tconst byte *leftRow = leftEye + y*viewwidth;
\t\tfor(int x = 0;x < viewwidth;++x)
\t\t{
\t\t\tconst byte left = leftRow[x];
\t\t\tconst byte right = rightRow[x];
\t\t\trightRow[x] = r_anaglyph_swapeyes ? anaglyphColorMap[right][left] : anaglyphColorMap[left][right];
\t\t}
\t}
}

static angle_t CalculateAnaglyphToeAngle(fixed halfEyeSeparation, fixed convergenceDistance)
{
\tconst double radians = atan2(static_cast<double>(halfEyeSeparation),
\t\tstatic_cast<double>(MAX<fixed>(convergenceDistance, 1)));
\treturn static_cast<angle_t>(radians * static_cast<double>(ANGLE_180) / PI);
}

int32_t\tlasttimecount;''', path, 'stereo state and compositor')
    text = replace_once(text,
        '''unsigned int CalcRotate (AActor *ob)
{
\tangle_t angle, viewangle;

\t// this isn't exactly correct, as it should vary by a trig value,
\t// but it is close enough with only eight rotations

\tviewangle = players[ConsolePlayer].camera->angle + (centerx - ob->viewx)/8;

\tangle = viewangle - ob->angle;''',
        '''unsigned int CalcRotate (AActor *ob)
{
\tangle_t angle;

\t// Use the active eye orientation so rotated sprites agree with the wall and
\t// billboard projection during converged stereo rendering.
\tconst angle_t spriteViewAngle = viewangle + (centerx - ob->viewx)/8;

\tangle = spriteViewAngle - ob->angle;''', path, 'sprite eye orientation')
    text = replace_once(text,
        '''\tviewangle = players[ConsolePlayer].camera->angle;
\tmidangle = viewangle>>ANGLETOFINESHIFT;
\tviewsin = finesine[viewangle>>ANGLETOFINESHIFT];
\tviewcos = finecosine[viewangle>>ANGLETOFINESHIFT];
\tviewx = players[ConsolePlayer].camera->x - FixedMul(focallength,viewcos);
\tviewy = players[ConsolePlayer].camera->y + FixedMul(focallength,viewsin);

\tfocaltx = (short)(viewx>>TILESHIFT);
\tfocalty = (short)(viewy>>TILESHIFT);

\tviewtx = (short)(players[ConsolePlayer].camera->x >> TILESHIFT);
\tviewty = (short)(players[ConsolePlayer].camera->y >> TILESHIFT);''',
        '''\tconst angle_t baseViewAngle = players[ConsolePlayer].camera->angle;
\tconst fixed baseViewSin = finesine[baseViewAngle>>ANGLETOFINESHIFT];
\tconst fixed baseViewCos = finecosine[baseViewAngle>>ANGLETOFINESHIFT];

\t// Translate each eye along the head's right axis, then rotate that eye
\t// toward the shared convergence point. This is actual binocular geometry:
\t// near, convergence-plane, and far geometry produce different disparities.
\tviewangle = baseViewAngle + anaglyphEyeYaw;
\tmidangle = viewangle>>ANGLETOFINESHIFT;
\tviewsin = finesine[viewangle>>ANGLETOFINESHIFT];
\tviewcos = finecosine[viewangle>>ANGLETOFINESHIFT];

\tconst fixed cameraX = players[ConsolePlayer].camera->x + FixedMul(anaglyphEyeOffset, baseViewSin);
\tconst fixed cameraY = players[ConsolePlayer].camera->y + FixedMul(anaglyphEyeOffset, baseViewCos);

\tviewx = cameraX - FixedMul(focallength,viewcos);
\tviewy = cameraY + FixedMul(focallength,viewsin);

\tfocaltx = (short)(viewx>>TILESHIFT);
\tfocalty = (short)(viewy>>TILESHIFT);

\tviewtx = (short)(cameraX >> TILESHIFT);
\tviewty = (short)(cameraY >> TILESHIFT);''', path, 'binocular camera geometry')
    text = replace_once(text,
        'void R_RenderView()\n{\n\tCalcViewVariables();',
        'static void R_RenderWorld()\n{\n\tCalcViewVariables();', path, 'world render split')
    text = replace_once(text,
        '''\tif(GetFeatureFlags() & FF_SNOW)
\t\tDrawSnow(vbuf, vbufPitch);
#endif

\tDrawPlayerWeapon ();    // draw player's hands''',
        '''\tif(GetFeatureFlags() & FF_SNOW)
\t\tDrawSnow(vbuf, vbufPitch);
#endif
}

static void R_DrawViewOverlay()
{
\tDrawPlayerWeapon ();    // draw player's hands''', path, 'overlay extraction')
    text = replace_once(text,
        '''\t// Always mark the current spot as visible in the automap
\tmap->GetSpot(players[ConsolePlayer].mo->tilex, players[ConsolePlayer].mo->tiley, 0)->amFlags |= AM_Visible;
}

/*
========================
=
= ThreeDRefresh''',
        '''\t// Always mark the current spot as visible in the automap
\tmap->GetSpot(players[ConsolePlayer].mo->tilex, players[ConsolePlayer].mo->tiley, 0)->amFlags |= AM_Visible;
}

void R_RenderView()
{
\tR_RenderWorld();
\tR_DrawViewOverlay();
}

/*
========================
=
= ThreeDRefresh''', path, 'monoscopic wrapper')
    text = replace_once(text,
        '''\tvbuf += screenofs;
\tvbufPitch = SCREENPITCH;

\tR_RenderView();

\tVL_UnlockSurface();''',
        '''\tvbuf += screenofs;
\tvbufPitch = SCREENPITCH;

\tif(r_anaglyph && r_anaglyph_separation > 0)
\t{
\t\tbyte * const screenVbuf = vbuf;
\t\tconst unsigned int screenPitch = vbufPitch;
\t\tconst unsigned int requiredSize = viewwidth*viewheight;
\t\tif(requiredSize != anaglyphLeftEyeSize)
\t\t{
\t\t\tanaglyphLeftEye = new byte[requiredSize];
\t\t\tanaglyphLeftEyeSize = requiredSize;
\t\t}

\t\t// Separation is half-IPD in 1/256 tile units. Convergence is in
\t\t// quarter-tile units, allowing a useful range without floating CVARs.
\t\tconst fixed halfEyeSeparation = r_anaglyph_separation*(TILEGLOBAL/256);
\t\tconst fixed convergenceDistance = MAX(r_anaglyph_convergence, 1)*(TILEGLOBAL/4);
\t\tconst angle_t toeAngle = CalculateAnaglyphToeAngle(halfEyeSeparation, convergenceDistance);

\t\tvbuf = anaglyphLeftEye.Get();
\t\tvbufPitch = viewwidth;
\t\tanaglyphEyeOffset = -halfEyeSeparation;
\t\tanaglyphEyeYaw = ANGLE_NEG(toeAngle);
\t\tmap->ClearVisibility();
\t\tR_RenderWorld();

\t\tvbuf = screenVbuf;
\t\tvbufPitch = screenPitch;
\t\tanaglyphEyeOffset = halfEyeSeparation;
\t\tanaglyphEyeYaw = toeAngle;
\t\tmap->ClearVisibility();
\t\tR_RenderWorld();

\t\tComposeAnaglyph(screenVbuf, screenPitch, anaglyphLeftEye.Get());

\t\tanaglyphEyeOffset = 0;
\t\tanaglyphEyeYaw = 0;
\t\tCalcViewVariables();
\t\tR_DrawViewOverlay();
\t}
\telse
\t{
\t\tanaglyphEyeOffset = 0;
\t\tanaglyphEyeYaw = 0;
\t\tR_RenderView();
\t}

\tVL_UnlockSurface();''', path, 'dual-eye renderer')
    loaded[path][0] = text

    path = Path('src/wl_menu.cpp')
    text, eol = loaded[path]
    text = replace_once(text,
        '''#if SDL_VERSION_ATLEAST(2,0,0)
\tdisplayMenu.addItem(new BooleanMenuItem(language["STR_VSYNC"], vid_vsync, ToggleVsync));
#endif
\tdisplayMenu.addItem(new MultipleChoiceMenuItem(SetAspectRatio, aspectOptions, 8, vid_aspect));''',
        '''#if SDL_VERSION_ATLEAST(2,0,0)
\tdisplayMenu.addItem(new BooleanMenuItem(language["STR_VSYNC"], vid_vsync, ToggleVsync));
#endif
\tdisplayMenu.addItem(new BooleanMenuItem("Anaglyph 3D", r_anaglyph));
\tdisplayMenu.addItem(new BooleanMenuItem("Swap anaglyph eyes", r_anaglyph_swapeyes));
\tdisplayMenu.addItem(new LabelMenuItem("3D eye separation"));
\tdisplayMenu.addItem(new SliderMenuItem(r_anaglyph_separation, 110, 32, "Low", "High"));
\tdisplayMenu.addItem(new LabelMenuItem("3D convergence distance"));
\tdisplayMenu.addItem(new SliderMenuItem(r_anaglyph_convergence, 110, 64, "Near", "Far"));
\tdisplayMenu.addItem(new MultipleChoiceMenuItem(SetAspectRatio, aspectOptions, 8, vid_aspect));''', path, 'display controls')
    loaded[path][0] = text

    for path, (text, eol) in loaded.items():
        save(path, text, eol)
    print('Applied true depth-dependent red/cyan stereo rendering.')

if __name__ == '__main__':
    main()
