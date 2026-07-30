// Wrap the stock renderer so upstream code remains intact while stereo capture is added.

#define ThreeDRefresh ECWolf_OriginalThreeDRefresh
#include "wl_draw.cpp"
#undef ThreeDRefresh

#include "anaglyph.h"

void ThreeDRefresh(void)
{
	// Ensure we have a valid camera.
	if(players[ConsolePlayer].camera == NULL)
		players[ConsolePlayer].camera = players[ConsolePlayer].mo;

	map->ClearVisibility();
	AnaglyphInitializeSettings();
	AnaglyphCancelFrame();

	BYTE *frameBuffer = VL_LockSurface();
	if(frameBuffer == NULL)
	{
		VL_UnlockSurface();
		return;
	}

	vbuf = frameBuffer + screenofs;
	vbufPitch = SCREENPITCH;

	// Transitions intentionally remain monoscopic. Their incremental screen
	// mutation is incompatible with a stable pair of eye images.
	const bool renderStereo = r_anaglyph && !fizzlein;
	AActor *camera = players[ConsolePlayer].camera;
	const fixed originalX = camera->x;
	const fixed originalY = camera->y;

	if(renderStereo)
	{
		const angle_t cameraAngle = camera->angle;
		const fixed eyeSin = finesine[cameraAngle >> ANGLETOFINESHIFT];
		const fixed eyeCos = finecosine[cameraAngle >> ANGLETOFINESHIFT];
		const fixed halfSeparation = AnaglyphGetHalfEyeSeparation();
		const fixed xOffset = FixedMul(halfSeparation, eyeSin);
		const fixed yOffset = FixedMul(halfSeparation, eyeCos);

		// Parallel cameras preserve zero parallax at infinity. The lateral
		// displacement alone creates physically meaningful binocular disparity.
		camera->x = originalX - xOffset;
		camera->y = originalY - yOffset;
		R_RenderView();
		AnaglyphCaptureEye(true, frameBuffer, SCREENPITCH, SCREENWIDTH, SCREENHEIGHT);

		camera->x = originalX + xOffset;
		camera->y = originalY + yOffset;
		R_RenderView();
		AnaglyphCaptureEye(false, frameBuffer, SCREENPITCH, SCREENWIDTH, SCREENHEIGHT);
		AnaglyphSubmitFrame();
	}
	else
	{
		R_RenderView();
	}

	camera->x = originalX;
	camera->y = originalY;

	VL_UnlockSurface();
	vbuf = NULL;

	if(player_t *player = players[ConsolePlayer].camera->player)
	{
		if(player->ScreenFader)
			player->ScreenFader->Update();
	}

	if(fizzlein)
	{
		while(!fizzlein->Update())
			VH_UpdateScreen();
		VH_UpdateScreen();
		fizzlein.Reset();
		ResetTimeCount();
	}
	else if(fpscounter)
	{
		FString fpsDisplay;
		fpsDisplay.Format("%2u fps", fps);

		word x = 0;
		word y = 0;
		word width, height;
		VW_MeasurePropString(ConFont, fpsDisplay, width, height);
		MenuToRealCoords(x, y, width, height, MENU_TOP);
		VWB_Clear(GPalette.BlackIndex, x, y, x+width+1, y+height+1);
		px = 0;
		py = 0;
		pa = MENU_TOP;
		VWB_DrawPropString(ConFont, fpsDisplay, CR_WHITE);
		pa = MENU_CENTER;
	}

	if(fpscounter)
	{
		fps_frames++;
		fps_time += tics;

		if(fps_time > 35)
		{
			fps_time -= 35;
			fps = fps_frames << 1;
			fps_frames = 0;
		}
	}
}
