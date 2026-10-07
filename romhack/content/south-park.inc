OldaleTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SF_SouthPark_Enter
	.byte 0
SF_SouthPark_Enter::
	setflag FLAG_VISITED_OLDALE_TOWN
	end
SF_Muni_Return::
	lock
	faceplayer
	msgbox SF_Text_MuniReturn, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SF_Muni_ReturnDone
	closemessage
	warp MAP_LITTLEROOT_TOWN, 28, 22
	waitstate
SF_Muni_ReturnDone::
	release
	end
SF_DylanField::
	msgbox SF_Text_Dylan, MSGBOX_NPC
	end
SF_GarryTan::
	msgbox SF_Text_Garry, MSGBOX_NPC
	end
SF_ParkHistory::
	msgbox SF_Text_ParkHistory, MSGBOX_SIGN
	end
SF_CognitionSign::
	msgbox SF_Text_CognitionSign, MSGBOX_SIGN
	end
SF_ServiceSign::
	msgbox SF_Text_ServiceSign, MSGBOX_SIGN
	end
SF_ParkDiscovery::
	lockall
	goto_if_set FLAG_UNUSED_0x041, SF_ParkDiscovery_Empty
	giveitem ITEM_ORAN_BERRY, 3
	goto_if_eq VAR_RESULT, FALSE, SF_ParkDiscovery_BagFull
	setflag FLAG_UNUSED_0x041
	msgbox SF_Text_Discovery, MSGBOX_DEFAULT
	releaseall
	end
SF_ParkDiscovery_BagFull::
	msgbox SF_Text_BenchBagFull, MSGBOX_DEFAULT
	releaseall
	end
SF_ParkDiscovery_Empty::
	msgbox SF_Text_EmptyBench, MSGBOX_DEFAULT
	releaseall
	end
SF_Text_MuniReturn::
	.string "JONATHAN: Back to the SUNSET?\pI scheduled this train to arrive\none minute before we need it.\pRide back to JUDAH?$"
SF_Text_Dylan::
	.string "DYLAN FIELD: SOUTH PARK is oval.\nThe pitch decks are rectangular.\pSomehow, everybody still wants\na circle around their idea.\pCOGNITION is west of the park,\nnear THIRD STREET.$"
SF_Text_Garry::
	.string "GARRY TAN: Talk to people. Build a team.\nTry something before your next pitch.\pThe garden grass has wild companions.\nThe clinic beside it has a terminal.$"
SF_Text_ParkHistory::
	.string "SOUTH PARK\pAn old city garden with paths,\nmeadows and places to stop and talk.\pThe park was planned as an English\nstrolling garden.\pThe park outlasted the business plans.$"
SF_Text_CognitionSign::
	.string "COGNITION\nSCOTT WU'S BUILD CHALLENGE\pDeliveries, team practice and\nhabitat safety relays.$"
SF_Text_ServiceSign::
	.string "SOUTH PARK FIELD CLINIC\nHealing, supplies and team storage.$"
SF_Text_Discovery::
	.string "Someone left berries beside a\nnotebook full of startup names.\pNone of the names have vowels.$"
SF_Text_EmptyBench::
	.string "A sunny bench. The notebook says:\nREBRAND BEFORE DEMO DAY.$"

SF_Text_BenchBagFull::
	.string "The berries are still here.\nMake room in your BAG and come back.$"
