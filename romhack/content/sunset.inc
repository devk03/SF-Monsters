@ Original SF opening. Reserved quest state: VAR_UNUSED_0x40F7 (0–4).
LittlerootTown_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SF_Sunset_SaveIdentity
	map_script MAP_SCRIPT_ON_TRANSITION, SF_Sunset_Enter
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SF_Sunset_Frame
	.byte 0

SF_Sunset_SaveIdentity::
	goto_if_ne VAR_UNUSED_0x40F9, 0, SF_Sunset_IdentityReady
	goto_if_ne VAR_UNUSED_0x40F8, 0, SF_Sunset_IdentityReady
	setvar VAR_UNUSED_0x40F8, 0x5346
	setvar VAR_UNUSED_0x40F9, 1
SF_Sunset_IdentityReady::
	end

SF_Sunset_Enter::
	setflag FLAG_VISITED_LITTLEROOT_TOWN
	setflag FLAG_SYS_B_DASH
	setrespawn HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F
	end

SF_Sunset_Frame::
	map_script_2 VAR_UNUSED_0x40F7, 0, SF_Sunset_Opening
	.2byte 0

SF_Sunset_Opening::
	lockall
	msgbox SF_Text_Opening, MSGBOX_DEFAULT
	setvar VAR_UNUSED_0x40F7, 1
	releaseall
	end

SF_Karpathy::
	lock
	faceplayer
	goto_if_set FLAG_SYS_POKEMON_GET, SF_Karpathy_Heal
	msgbox SF_Text_Choose, MSGBOX_DEFAULT
	release
	end

SF_Karpathy_Heal::
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	msgbox SF_Text_Heal, MSGBOX_DEFAULT
	release
	end

SF_Starter_Bloom::
	lock
	goto_if_set FLAG_SYS_POKEMON_GET, SF_Starter_Done
	showmonpic SPECIES_TREECKO, 10, 3
	msgbox SF_Text_Bloom, MSGBOX_YESNO
	hidemonpic
	goto_if_eq VAR_RESULT, NO, SF_Starter_Done
	givemon SPECIES_TREECKO, 5
	setvar VAR_STARTER_MON, 0
	goto SF_Starter_Received

SF_Starter_Ember::
	lock
	goto_if_set FLAG_SYS_POKEMON_GET, SF_Starter_Done
	showmonpic SPECIES_TORCHIC, 10, 3
	msgbox SF_Text_Ember, MSGBOX_YESNO
	hidemonpic
	goto_if_eq VAR_RESULT, NO, SF_Starter_Done
	givemon SPECIES_TORCHIC, 5
	setvar VAR_STARTER_MON, 1
	goto SF_Starter_Received

SF_Starter_Tide::
	lock
	goto_if_set FLAG_SYS_POKEMON_GET, SF_Starter_Done
	showmonpic SPECIES_MUDKIP, 10, 3
	msgbox SF_Text_Tide, MSGBOX_YESNO
	hidemonpic
	goto_if_eq VAR_RESULT, NO, SF_Starter_Done
	givemon SPECIES_MUDKIP, 5
	setvar VAR_STARTER_MON, 2
	goto SF_Starter_Received

SF_Starter_Received::
	setflag FLAG_SYS_POKEMON_GET
	setflag FLAG_SYS_POKEDEX_GET
	setvar VAR_UNUSED_0x40F7, 2
	removeobject 2
	removeobject 3
	removeobject 4
	giveitem ITEM_POKE_BALL, 5
	giveitem ITEM_POTION, 3
	msgbox SF_Text_Ready, MSGBOX_DEFAULT
SF_Starter_Done::
	release
	end

SF_Prototype::
	lock
	goto_if_unset FLAG_SYS_POKEMON_GET, SF_Prototype_NotReady
	msgbox SF_Text_Prototype, MSGBOX_DEFAULT
	closemessage
	setwildbattle SPECIES_ZIGZAGOON, 3
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, SF_Prototype_Recovered
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, SF_Prototype_Recovered
	msgbox SF_Text_TryAgain, MSGBOX_DEFAULT
	release
	end

SF_Prototype_Recovered::
	setvar VAR_UNUSED_0x40F7, 3
	setflag FLAG_UNUSED_0x040
	removeobject 6
	msgbox SF_Text_Recovered, MSGBOX_DEFAULT
	release
	end

SF_Prototype_NotReady::
	msgbox SF_Text_NotReady, MSGBOX_DEFAULT
	release
	end

SF_Roon::
	lock
	faceplayer
	goto_if_eq VAR_UNUSED_0x40F7, 3, SF_Roon_Return
	goto_if_eq VAR_UNUSED_0x40F7, 4, SF_Roon_After
	msgbox SF_Text_RoonBefore, MSGBOX_DEFAULT
	release
	end

SF_Roon_Return::
	msgbox SF_Text_RoonReturn, MSGBOX_DEFAULT
	addmoney 500
	setvar VAR_UNUSED_0x40F7, 4
	release
	end

SF_Roon_After::
	msgbox SF_Text_RoonAfter, MSGBOX_DEFAULT
	release
	end

SF_Naval::
	msgbox SF_Text_Naval, MSGBOX_NPC
	end

SF_Jonathan::
	lock
	faceplayer
	goto_if_lt VAR_UNUSED_0x40F7, 4, SF_Jonathan_BeforeTransit
	msgbox SF_Text_MuniOutbound, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SF_Jonathan_Done
	closemessage
	warp MAP_OLDALE_TOWN, 7, 26
	waitstate
SF_Jonathan_Done::
	release
	end
SF_Jonathan_BeforeTransit::
	msgbox SF_Text_Jonathan, MSGBOX_NPC
	end

SF_Sunset_Sign::
	msgbox SF_Text_Sign, MSGBOX_SIGN
	end

SF_Text_Opening::
	.string "OUTER SUNSET. Another foggy morning.\pYour courier phone has one message:\nROON lost a prototype at OCEAN BEACH.\pKARPATHY is by the JUDAH crossing.\nAsk him for a field companion.$"
SF_Text_Choose::
	.string "KARPATHY: Training data is useful.\nSo is going outside.\pChoose one of these three companions.\nThen check the beach north of ROON.\pHold B to run. Come back here\nwhenever your team needs a rest.$"
SF_Text_Heal::
	.string "KARPATHY: Your team is refreshed.\pThe prototype washed up on the beach,\nnorth of ROON. Watch the shore grass.$"
SF_Text_Bloom::
	.string "SPROUTSLUG dreams of growing wings.\nFor now, its garden comes along.\pChoose SPROUTSLUG?$"
SF_Text_Ember::
	.string "CINDERCOY warms the Sunset with\na little fire and too much confidence.\pChoose CINDERCOY?$"
SF_Text_Tide::
	.string "BRINEPUP loves the cold waves.\nIt thinks every courier is a playmate.\pChoose BRINEPUP?$"
SF_Text_Ready::
	.string "KARPATHY: Take supplies for the beach.\nWeaken a wild monster to recruit it.\pROON is west of GREAT HIGHWAY.\nHis prototype is farther north.\pYour BAG, team and SAVE are available\nfrom the START menu.$"
SF_Text_Prototype::
	.string "A damaged habitat sensor is half\nburied in the sand.\pA wild monster is nesting beside it!$"
SF_Text_TryAgain::
	.string "The sensor is still here.\nReturn when your team is ready.$"
SF_Text_Recovered::
	.string "You recovered the prototype.\pIts display flashes an odd fog signal.\nBring it to ROON, south along the beach.$"
SF_Text_NotReady::
	.string "Something is moving beside the sensor.\nFind a companion before approaching.$"
SF_Text_RoonBefore::
	.string "ROON: I posted one mysterious photo\nand now everyone thinks it's an ARG.\pIt is a missing habitat sensor.\nLook north along this beach. Please.$"
SF_Text_RoonReturn::
	.string "ROON: You found it!\nDelivery fee: 500 coins.\pThat signal should not be there.\nSCOTT WU can read it at COGNITION.\pHis lab is near SOUTH PARK in SoMa.\nTake MUNI from the JUDAH crossing.\pAnd don't tweet the serial number.$"
SF_Text_RoonAfter::
	.string "ROON: COGNITION, near SOUTH PARK.\nShow SCOTT the sensor.\pI will investigate the signal.\nMy posts will become less helpful.$"
SF_Text_Naval::
	.string "NAVAL: The fog has no personal brand.\nIt arrives, then leaves.\pExcept here. Here it has tenure.$"
SF_Text_Jonathan::
	.string "JONATHAN: I made a scheduling tool\nfor spontaneous plans.\pIt found us a twelve-minute window\nfor spontaneity next Thursday.$"
SF_Text_Sign::
	.string "JUDAH / GREAT HIGHWAY\nOCEAN BEACH: WEST\pMUNI: EAST\nPlease give the fog right of way.$"

SF_Text_MuniOutbound::
	.string "JONATHAN: COGNITION? Take MUNI\nfrom JUDAH, then walk to SOUTH PARK.\pThe sensor is not paying a second fare.\pRide to SoMa?$"
