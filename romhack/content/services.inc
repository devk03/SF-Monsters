LittlerootTown_ProfessorBirchsLab_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SF_Clinic_Enter
	.byte 0
SF_Clinic_Enter::
	setrespawn HEAL_LOCATION_OLDALE_TOWN
	end
SF_JustineClinic::
	lock
	faceplayer
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	msgbox SF_Text_Clinic, MSGBOX_DEFAULT
	release
	end
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
