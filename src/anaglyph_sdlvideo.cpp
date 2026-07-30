// Wrap the stock SDL backend and intercept only palette-to-true-color conversion.

#include <string.h>

#include "anaglyph.h"
#include "v_pfx.h"

class FAnaglyphPfxProxy
{
public:
	FAnaglyphPfxProxy()
		: Bits(0), RedMask(0), GreenMask(0), BlueMask(0), HavePalette(false)
	{
	}

	void SetFormat(int bits, uint32 redMask, uint32 greenMask, uint32 blueMask)
	{
		Bits = bits;
		RedMask = redMask;
		GreenMask = greenMask;
		BlueMask = blueMask;
		::GPfx.SetFormat(bits, redMask, greenMask, blueMask);
	}

	void SetPalette(const PalEntry *palette)
	{
		if(palette != NULL)
		{
			memcpy(Palette, palette, sizeof(Palette));
			HavePalette = true;
		}
		if(::GPfx.SetPalette != NULL)
			::GPfx.SetPalette(palette);
	}

	void Convert(
		BYTE *source,
		int sourcePitch,
		void *destination,
		int destinationPitch,
		int destinationWidth,
		int destinationHeight,
		fixed_t xstep,
		fixed_t ystep,
		fixed_t xfrac,
		fixed_t yfrac)
	{
		if(HavePalette && AnaglyphConvertFrame(
			source,
			sourcePitch,
			destination,
			destinationPitch,
			destinationWidth,
			destinationHeight,
			xstep,
			ystep,
			xfrac,
			yfrac,
			Palette,
			Bits,
			RedMask,
			GreenMask,
			BlueMask))
		{
			return;
		}

		::GPfx.Convert(
			source,
			sourcePitch,
			destination,
			destinationPitch,
			destinationWidth,
			destinationHeight,
			xstep,
			ystep,
			xfrac,
			yfrac);
	}

private:
	PalEntry Palette[256];
	int Bits;
	uint32 RedMask;
	uint32 GreenMask;
	uint32 BlueMask;
	bool HavePalette;
};

static FAnaglyphPfxProxy AnaglyphPfx;

#define GPfx AnaglyphPfx
#include "sdlvideo.cpp"
#undef GPfx
