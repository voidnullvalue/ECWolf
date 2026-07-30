#ifndef __ECWOLF_ANAGLYPH_H__
#define __ECWOLF_ANAGLYPH_H__

#include "wl_def.h"
#include "v_palette.h"

extern bool r_anaglyph;
extern int r_anaglyph_strength;
extern bool r_anaglyph_swap_eyes;

void AnaglyphInitializeSettings();
void AnaglyphStoreSettings();
fixed AnaglyphGetHalfEyeSeparation();

void AnaglyphCancelFrame();
void AnaglyphCaptureEye(bool leftEye, const BYTE *buffer, int pitch, int width, int height);
void AnaglyphSubmitFrame();

bool AnaglyphConvertFrame(
	BYTE *currentFrame,
	int currentPitch,
	void *destination,
	int destinationPitch,
	int width,
	int height,
	fixed_t xstep,
	fixed_t ystep,
	fixed_t xfrac,
	fixed_t yfrac,
	const PalEntry palette[256],
	int bits,
	uint32 redMask,
	uint32 greenMask,
	uint32 blueMask);

#endif
