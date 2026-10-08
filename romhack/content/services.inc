LittlerootTown_ProfessorBirchsLab_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SF_Clinic_Enter
	.byte 0
SF_Clinic_Enter::
	setrespawn HEAL_LOCATION_OLDALE_TOWN
	end
SF_JustineClinic::
	lock
	faceplayer
	applymovement 1, SF_Clinic_TurnToEquipment
	waitmovement 0
	special HealPlayerParty
	playfanfare MUS_HEAL
	call SF_Clinic_LightsWarm
	delay 24
	call SF_Clinic_LightsBright
	delay 24
	call SF_Clinic_LightsPeak
	delay 24
	call SF_Clinic_LightsBright
	delay 24
	call SF_Clinic_LightsWarm
	delay 24
	call SF_Clinic_LightsOff
	waitfanfare
	faceplayer
	msgbox SF_Text_Clinic, MSGBOX_DEFAULT
	release
	end
SF_Clinic_TurnToEquipment::
	face_left
	step_end
SF_Clinic_LightsWarm::
	setmetatile 1, 5, 606, TRUE
	setmetatile 2, 5, 607, TRUE
	setmetatile 1, 6, 608, TRUE
	setmetatile 2, 6, 609, TRUE
	special DrawWholeMapView
	return
SF_Clinic_LightsBright::
	setmetatile 1, 5, 610, TRUE
	setmetatile 2, 5, 611, TRUE
	setmetatile 1, 6, 612, TRUE
	setmetatile 2, 6, 613, TRUE
	special DrawWholeMapView
	return
SF_Clinic_LightsPeak::
	setmetatile 1, 5, 614, TRUE
	setmetatile 2, 5, 615, TRUE
	setmetatile 1, 6, 616, TRUE
	setmetatile 2, 6, 617, TRUE
	special DrawWholeMapView
	return
SF_Clinic_LightsOff::
	setmetatile 1, 5, 540, TRUE
	setmetatile 2, 5, 541, TRUE
	setmetatile 1, 6, 542, TRUE
	setmetatile 2, 6, 543, TRUE
	special DrawWholeMapView
	return
SF_ClinicCounterShop::
	setvar VAR_LAST_TALKED, 2
	goto SF_PatrickShop
SF_PatrickShop::
	lock
	faceplayer
	msgbox SF_Text_Shop, MSGBOX_DEFAULT
	closemessage
	pokemart SF_ClinicShopItems
	release
	end
	.align 2
SF_ClinicShopItems:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_NONE
SF_ClinicPC::
	goto EventScript_PC
	end
SF_ClinicNotes::
	msgbox SF_Text_ClinicNotes, MSGBOX_SIGN
	end
SF_Text_Clinic::
	.string "JUSTINE MOORE: Your team is refreshed.\pNot every problem needs a new app.\nSome need a rest and a snack.\pUse the terminal for team storage.\nPATRICK has supplies by the door.$"
SF_Text_Shop::
	.string "PATRICK MCKENZIE: Supplies have clear\nprices. Revolutionary, I know.\pA stronger team beats buying\nforty potions for the same problem.$"
SF_Text_ClinicNotes::
	.string "TEAM NOTES\pSix companions travel with you.\nThe terminal stores the others.\pRead move types and effects.\nA balanced roster gives you options.$"

SF_ClinicHistoryShelf::
	msgbox SF_Text_ClinicHistoryShelf, MSGBOX_SIGN
	end
SF_Text_ClinicHistoryShelf::
	.string "HISTORY SHELF\pSOUTH PARK began as a garden\nmodeled on London's city squares.\pUpscale homes surrounded it.\nSF had exclusive communities\lbefore invite-only group chats.$"
