// Wrap the stock menu construction and append anaglyph controls.

#define CreateMenus ECWolf_CreateMenusBase
#include "wl_menu.cpp"
#undef CreateMenus

#include "anaglyph.h"

MENU_LISTENER(StoreAnaglyphToggle)
{
	AnaglyphStoreSettings();
	return true;
}

MENU_LISTENER(SetAnaglyphStrength)
{
	r_anaglyph_strength = which;
	AnaglyphStoreSettings();
	return true;
}

void CreateMenus()
{
	ECWolf_CreateMenusBase();
	AnaglyphInitializeSettings();

	const char *depthOptions[] =
	{
		"3D depth: Low",
		"3D depth: Medium",
		"3D depth: High",
		"3D depth: Extreme"
	};

	displayMenu.addItem(new BooleanMenuItem("Red/cyan anaglyph 3D", r_anaglyph, StoreAnaglyphToggle));
	displayMenu.addItem(new MultipleChoiceMenuItem(SetAnaglyphStrength, depthOptions, 4, r_anaglyph_strength));
	displayMenu.addItem(new BooleanMenuItem("Swap anaglyph eyes", r_anaglyph_swap_eyes, StoreAnaglyphToggle));
}
