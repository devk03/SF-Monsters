RustboroCity_Gym_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SF_Cognition_Load
	map_script MAP_SCRIPT_ON_TRANSITION, SF_Cognition_Enter
	.byte 0

SF_Cognition_Enter::
	call_if_ge VAR_UNUSED_0x40DB, 1, SF_Cognition_ScottStation
	end
SF_Cognition_ScottStation::
	setobjectxyperm 1, 8, 3
	return

SF_Cognition_Load::
	goto_if_ge VAR_UNUSED_0x40DB, 3, SF_Cognition_OpenGate
	end
SF_Cognition_OpenGate::
	setmetatile 8, 8, 0x202, FALSE
	end

SF_Scott::
	lock
	faceplayer
	goto_if_eq VAR_UNUSED_0x40DB, 0, SF_Scott_Delivery
	goto_if_ge VAR_UNUSED_0x40DB, 4, SF_Scott_After
	goto_if_lt VAR_UNUSED_0x40DB, 3, SF_Scott_Relays
	trainerbattle_single TRAINER_ROXANNE_1, SF_Text_ScottBattle, SF_Text_ScottDefeat, SF_Cognition_Won, NO_MUSIC
	goto SF_Scott_After
	end
SF_Scott_Delivery::
	msgbox SF_Text_Delivery, MSGBOX_DEFAULT
	setvar VAR_UNUSED_0x40DB, 1
	closemessage
	applywaitmovement 1, SF_Scott_WalkToGate
	fadescreen FADE_TO_BLACK
	setobjectxy 1, 8, 3
	setobjectxyperm 1, 8, 3
	fadescreen FADE_FROM_BLACK
	release
	end
SF_Scott_WalkToGate:
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	step_end
SF_Scott_Relays::
	msgbox SF_Text_Relays, MSGBOX_DEFAULT
	release
	end
SF_Cognition_Won::
	setflag FLAG_DEFEATED_RUSTBORO_GYM
	setflag FLAG_BADGE01_GET
	setvar VAR_UNUSED_0x40DB, 4
	message SF_Text_Badge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox SF_Text_NextLead, MSGBOX_DEFAULT
	goto SF_Scott_After
	end
SF_Scott_After::
	goto_if_set FLAG_UNUSED_0x042, SF_Scott_Repeat
	giveitem ITEM_TM_REFLECT
	goto_if_eq VAR_RESULT, FALSE, SF_Scott_BagFull
	setflag FLAG_UNUSED_0x042
SF_Scott_Repeat::
	msgbox SF_Text_After, MSGBOX_DEFAULT
	release
	end
SF_Scott_BagFull::
	msgbox SF_Text_BagFull, MSGBOX_DEFAULT
	release
	end

SF_RelayA::
	lockall
	goto_if_eq VAR_UNUSED_0x40DB, 0, SF_Relay_NoDelivery
	goto_if_ge VAR_UNUSED_0x40DB, 2, SF_Relay_Already
	playse SE_SWITCH
	setvar VAR_UNUSED_0x40DB, 2
	msgbox SF_Text_RelayA, MSGBOX_DEFAULT
	releaseall
	end
SF_RelayB::
	lockall
	goto_if_lt VAR_UNUSED_0x40DB, 2, SF_Relay_Order
	goto_if_ge VAR_UNUSED_0x40DB, 3, SF_Relay_Already
	playse SE_SWITCH
	setvar VAR_UNUSED_0x40DB, 3
	setmetatile 8, 8, 0x202, FALSE
	special DrawWholeMapView
	msgbox SF_Text_RelayB, MSGBOX_DEFAULT
	releaseall
	end
SF_Relay_NoDelivery::
	msgbox SF_Text_NoDelivery, MSGBOX_DEFAULT
	releaseall
	end
SF_Relay_Order::
	msgbox SF_Text_RelayOrder, MSGBOX_DEFAULT
	releaseall
	end
SF_Relay_Already::
	msgbox SF_Text_RelayAlready, MSGBOX_DEFAULT
	releaseall
	end

SF_WaldenYan::
	trainerbattle_single TRAINER_JOSH, SF_Text_WaldenIntro, SF_Text_WaldenDefeat
	msgbox SF_Text_WaldenAfter, MSGBOX_AUTOCLOSE
	end
SF_StevenHao::
	trainerbattle_single TRAINER_TOMMY, SF_Text_StevenIntro, SF_Text_StevenDefeat
	msgbox SF_Text_StevenAfter, MSGBOX_AUTOCLOSE
	end

SF_Text_Delivery::
	.string "SCOTT WU: That's ROON'S sensor.\pThis signal is forcing habitats\nto accelerate evolution.\pOur safety relays caught the spike.\nHelp restore them before we test it.\pBlue INPUT first, green OUTPUT second.\nThe field clinic can refresh your team.$"
SF_Text_Relays::
	.string "SCOTT: Blue INPUT, then green OUTPUT.\nThe gate opens when both are stable.\pWALDEN and STEVEN offer team practice.\nRead their move effects.$"
SF_Text_ScottBattle::
	.string "SCOTT WU: The relays are stable.\pA good plan leaves room to adapt.\nShow me how your team does it!$"
SF_Text_ScottDefeat::
	.string "SCOTT: Good teamwork.\nYou found a plan that survived contact.$"
SF_Text_Badge::
	.string "You earned COGNITION'S BUILD BADGE!$"
SF_Text_NextLead::
	.string "SCOTT: This badge grants relay access.\pThe outside signal is signed\nOVERCLOCK COLLECTIVE.\pThey want every habitat to evolve\nat once. The city can't sustain it.\pROON is tracing their network.\nYour next lead is in the MISSION.$"
SF_Text_After::
	.string "SCOTT: REFLECT protects your team\nfrom physical attacks for a while.\pSometimes the winning move is\ngiving a companion time to act.\pRest at the clinic and explore.\nThere are more people worth meeting.$"
SF_Text_BagFull::
	.string "SCOTT: Your badge is safe.\nMake room in your BAG for the move disk.\pCome back and I'll give it to you.$"
SF_Text_RelayA::
	.string "Blue INPUT stabilized.\nThe green OUTPUT relay is ready.$"
SF_Text_RelayB::
	.string "Green OUTPUT stabilized.\nThe safety gate is open!$"
SF_Text_NoDelivery::
	.string "The relay needs the recovered sensor.\nSpeak to SCOTT before changing it.$"
SF_Text_RelayOrder::
	.string "The OUTPUT has no stable input.\nRestore the blue relay first.$"
SF_Text_RelayAlready::
	.string "The relay is stable.\nA rare problem that stayed fixed.$"
SF_Text_WaldenIntro::
	.string "WALDEN YAN: Let's test your team's\nplan before the safety relay test.$"
SF_Text_WaldenDefeat::
	.string "WALDEN: Good. Keep the plan readable.$"
SF_Text_WaldenAfter::
	.string "WALDEN: The blue relay is beside me.\nPhysical moves use ATTACK and DEFENSE.$"
SF_Text_StevenIntro::
	.string "STEVEN HAO: A good team needs\nmore than one way through a problem.$"
SF_Text_StevenDefeat::
	.string "STEVEN: That approach works.$"
SF_Text_StevenAfter::
	.string "STEVEN: The green relay is beside me.\nStatus moves can create an opening.$"
