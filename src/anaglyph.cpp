#include <string.h>

#include "anaglyph.h"
#include "config.h"

bool r_anaglyph = false;
int r_anaglyph_strength = 1;
bool r_anaglyph_swap_eyes = false;

namespace
{
	BYTE *LeftEye = NULL;
	BYTE *RightEye = NULL;
	int EyePitch = 0;
	int EyeWidth = 0;
	int EyeHeight = 0;
	bool HaveLeftEye = false;
	bool HaveRightEye = false;
	bool FramePending = false;
	bool SettingsInitialized = false;

	int ClampStrength(int strength)
	{
		if(strength < 0)
			return 0;
		if(strength > 3)
			return 3;
		return strength;
	}

	void EnsureEyeBuffers(int pitch, int height)
	{
		const int size = pitch * height;
		if(EyePitch == pitch && EyeHeight == height && LeftEye != NULL && RightEye != NULL)
			return;

		delete[] LeftEye;
		delete[] RightEye;
		HaveLeftEye = false;
		HaveRightEye = false;
		FramePending = false;
		LeftEye = new BYTE[size];
		RightEye = new BYTE[size];
		EyePitch = pitch;
		EyeHeight = height;
	}

	uint32 PackChannel(BYTE value, uint32 mask)
	{
		if(mask == 0)
			return 0;

		unsigned int shift = 0;
		while((mask & 1) == 0)
		{
			mask >>= 1;
			++shift;
		}

		const uint32 maximum = mask;
		const uint32 scaled = (static_cast<uint32>(value) * maximum + 127) / 255;
		return scaled << shift;
	}

	uint32 PackColor(BYTE red, BYTE green, BYTE blue, uint32 redMask, uint32 greenMask, uint32 blueMask)
	{
		return PackChannel(red, redMask) |
			PackChannel(green, greenMask) |
			PackChannel(blue, blueMask);
	}

	void WritePixel(BYTE *destination, int bits, uint32 color)
	{
		switch(bits)
		{
			case 15:
			case 16:
				*reinterpret_cast<WORD *>(destination) = static_cast<WORD>(color);
				break;

			case 24:
#ifdef __BIG_ENDIAN__
				destination[0] = static_cast<BYTE>(color >> 16);
				destination[1] = static_cast<BYTE>(color >> 8);
				destination[2] = static_cast<BYTE>(color);
#else
				destination[0] = static_cast<BYTE>(color);
				destination[1] = static_cast<BYTE>(color >> 8);
				destination[2] = static_cast<BYTE>(color >> 16);
#endif
				break;

			case 30:
			case 32:
				*reinterpret_cast<uint32 *>(destination) = color;
				break;
		}
	}
}

void AnaglyphInitializeSettings()
{
	if(SettingsInitialized)
		return;

	config.CreateSetting("R_Anaglyph", 0);
	config.CreateSetting("R_AnaglyphStrength", 1);
	config.CreateSetting("R_AnaglyphSwapEyes", 0);

	r_anaglyph = config.GetSetting("R_Anaglyph")->GetInteger() != 0;
	r_anaglyph_strength = ClampStrength(config.GetSetting("R_AnaglyphStrength")->GetInteger());
	r_anaglyph_swap_eyes = config.GetSetting("R_AnaglyphSwapEyes")->GetInteger() != 0;
	SettingsInitialized = true;
}

void AnaglyphStoreSettings()
{
	AnaglyphInitializeSettings();
	r_anaglyph_strength = ClampStrength(r_anaglyph_strength);
	config.GetSetting("R_Anaglyph")->SetValue(r_anaglyph);
	config.GetSetting("R_AnaglyphStrength")->SetValue(r_anaglyph_strength);
	config.GetSetting("R_AnaglyphSwapEyes")->SetValue(r_anaglyph_swap_eyes);
}

fixed AnaglyphGetHalfEyeSeparation()
{
	static const int separationUnits[] = { 1, 2, 4, 8 };
	AnaglyphInitializeSettings();
	const int separation = separationUnits[ClampStrength(r_anaglyph_strength)];
	return static_cast<fixed>((separation * TILEGLOBAL) / 128);
}

void AnaglyphCancelFrame()
{
	HaveLeftEye = false;
	HaveRightEye = false;
	FramePending = false;
}

void AnaglyphCaptureEye(bool leftEye, const BYTE *buffer, int pitch, int width, int height)
{
	if(buffer == NULL || pitch < width || width <= 0 || height <= 0)
		return;

	EnsureEyeBuffers(pitch, height);
	BYTE *destination = leftEye ? LeftEye : RightEye;
	memcpy(destination, buffer, pitch * height);
	EyeWidth = width;
	if(leftEye)
		HaveLeftEye = true;
	else
		HaveRightEye = true;
}

void AnaglyphSubmitFrame()
{
	FramePending = HaveLeftEye && HaveRightEye;
}

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
	uint32 blueMask)
{
	if(!FramePending)
		return false;

	if(currentFrame == NULL || destination == NULL || palette == NULL ||
		(bits != 15 && bits != 16 && bits != 24 && bits != 30 && bits != 32) ||
		xstep != FRACUNIT || ystep != FRACUNIT || xfrac != 0 || yfrac != 0 ||
		width != EyeWidth || height != EyeHeight || currentPitch != EyePitch)
	{
		FramePending = false;
		return false;
	}

	const BYTE *left = r_anaglyph_swap_eyes ? RightEye : LeftEye;
	const BYTE *right = r_anaglyph_swap_eyes ? LeftEye : RightEye;
	const int bytesPerPixel = bits == 24 ? 3 : (bits <= 16 ? 2 : 4);

	for(int y = 0; y < height; ++y)
	{
		const BYTE *leftRow = left + y * EyePitch;
		const BYTE *rightRow = right + y * EyePitch;
		const BYTE *capturedFrameRow = RightEye + y * EyePitch;
		const BYTE *currentRow = currentFrame + y * currentPitch;
		BYTE *destinationRow = static_cast<BYTE *>(destination) + y * destinationPitch;

		for(int x = 0; x < width; ++x)
		{
			BYTE leftIndex = leftRow[x];
			BYTE rightIndex = rightRow[x];

			// Anything drawn after the stereo captures is a monoscopic overlay.
			// Feed it to both eyes so HUD text and transient UI retain full color.
			if(currentRow[x] != capturedFrameRow[x])
				leftIndex = rightIndex = currentRow[x];

			const uint32 color = PackColor(
				palette[leftIndex].r,
				palette[rightIndex].g,
				palette[rightIndex].b,
				redMask,
				greenMask,
				blueMask);
			WritePixel(destinationRow + x * bytesPerPixel, bits, color);
		}
	}

	FramePending = false;
	return true;
}
