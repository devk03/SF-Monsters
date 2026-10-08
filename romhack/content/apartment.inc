@ Optional Sunset adventure. Persistent beacon state: VAR_GIFT_UNUSED_3, 0-3.
LittlerootTown_BrendansHouse_1F_MapScripts::
	.byte 0

SF_AptWindow::
	lockall
	msgbox SF_AptTextWindow, MSGBOX_DEFAULT
	goto_if_ge VAR_GIFT_UNUSED_3, 1, SF_AptDone
	setvar VAR_GIFT_UNUSED_3, 1
	goto SF_AptDone

SF_AptBeacon::
	lockall
	goto_if_eq VAR_GIFT_UNUSED_3, 0, SF_AptLookOutside
	goto_if_eq VAR_GIFT_UNUSED_3, 2, SF_AptReward
	goto_if_ge VAR_GIFT_UNUSED_3, 3, SF_AptReturn
	msgbox SF_AptTextForecast, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SF_AptLeaveForecast
	setvar VAR_GIFT_UNUSED_3, 2
	msgbox SF_AptTextFixed, MSGBOX_DEFAULT
	goto SF_AptReward

SF_AptLookOutside::
	msgbox SF_AptTextLookOutside, MSGBOX_DEFAULT
	goto SF_AptDone
SF_AptLeaveForecast::
	msgbox SF_AptTextLeaveForecast, MSGBOX_DEFAULT
	goto SF_AptDone
SF_AptReward::
	giveitem ITEM_GREAT_BALL, 1
	goto_if_eq VAR_RESULT, FALSE, SF_AptBagFull
	setvar VAR_GIFT_UNUSED_3, 3
	msgbox SF_AptTextReward, MSGBOX_DEFAULT
	goto SF_AptDone
SF_AptBagFull::
	msgbox SF_AptTextBagFull, MSGBOX_DEFAULT
	goto SF_AptDone
SF_AptReturn::
	goto_if_set FLAG_BADGE01_GET, SF_AptAfterBadge
	msgbox SF_AptTextReturn, MSGBOX_DEFAULT
	goto SF_AptDone
SF_AptAfterBadge::
	msgbox SF_AptTextAfterBadge, MSGBOX_DEFAULT
	goto SF_AptDone

SF_AptBed::
	lockall
	goto_if_unset FLAG_SYS_POKEMON_GET, SF_AptEmptyBed
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	msgbox SF_AptTextRest, MSGBOX_DEFAULT
	goto SF_AptDone
SF_AptEmptyBed::
	msgbox SF_AptTextEmptyBed, MSGBOX_DEFAULT
	goto SF_AptDone
SF_AptPostcard::
	lockall
	msgbox SF_AptTextPostcard, MSGBOX_DEFAULT
SF_AptDone::
	releaseall
	end

SF_AptTextWindow::
	.string "Fog beads on the bay window.\nYou can barely see the crossing.\pThe spare beacon claims sunshine.\nOne of these readings is cached.$"
SF_AptTextLookOutside::
	.string "ROON left a spare fog beacon.\nIts forecast is SUNSHINE FOREVER.\pThe note says: Before fixing the\nworld, try looking out your window.$"
SF_AptTextForecast::
	.string "ROON: The sensor has been indoors\nfor nine months. Incredible uptime.\pUse the live window reading instead\nof its cached sunshine forecast?$"
SF_AptTextLeaveForecast::
	.string "SUNSHINE FOREVER remains online.\nThe window submits a bug report.$"
SF_AptTextFixed::
	.string "The beacon starts receiving FOG.\nA second pulse rides underneath it.\pROON: Two signals, one frequency.\nVery normal. Please stay curious.$"
SF_AptTextReward::
	.string "A spare recruiting capsule was\ntucked behind the beacon.\pThe second pulse points toward SOMA.\nYour main delivery still comes first.$"
SF_AptTextBagFull::
	.string "Make room in your BAG, then return.\nYour capsule will stay here.$"
SF_AptTextReturn::
	.string "Forecast: FOG, with a chance of\nsomeone calling it a platform.\pThe second signal is still faint.\nTake the prototype to COGNITION.$"
SF_AptTextAfterBadge::
	.string "The beacon logged your Build Badge.\nThe second pulse became stronger.\pROON: Someone is waking habitats.\nThis is bigger than a lost parcel.$"
SF_AptTextRest::
	.string "Your team settles into the blankets.\nEveryone is refreshed.\pThe lease calls this a junior suite.\nThe bed declines to comment.$"
SF_AptTextEmptyBed::
	.string "A small bed, a large monthly rent.\nChoose a companion before a team nap.$"
SF_AptTextPostcard::
	.string "An old postcard marks the N-JUDAH\nopening on OCTOBER 21, 1928.\pThe line connected downtown and\nthe beach through the Sunset Tunnel.\pSomeone wrote: A useful launch.\nNo waitlist. No subscription.$"
