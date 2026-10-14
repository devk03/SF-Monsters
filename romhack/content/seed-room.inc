@ Optional community seed room. Existing state is read; no rewards or new flags.
OldaleTown_House1_MapScripts::
	.byte 0

SF_SeedFieldNotes::
	lockall
	goto_if_set FLAG_BADGE01_GET, SF_SeedBadgeNotes
	goto_if_ge VAR_GIFT_UNUSED_3, 2, SF_SeedBeaconNotes
	goto_if_ge VAR_UNUSED_0x40F7, 3, SF_SeedRecoveredNotes
	msgbox SF_SeedTextFieldNotes, MSGBOX_DEFAULT
	goto SF_SeedDone
SF_SeedBadgeNotes::
	goto_if_ge VAR_GIFT_UNUSED_3, 2, SF_SeedBadgeBeaconNotes
	msgbox SF_SeedTextBadgeNotes, MSGBOX_DEFAULT
	goto SF_SeedDone
SF_SeedBadgeBeaconNotes::
	msgbox SF_SeedTextBadgeBeaconNotes, MSGBOX_DEFAULT
	goto SF_SeedDone
SF_SeedBeaconNotes::
	msgbox SF_SeedTextBeaconNotes, MSGBOX_DEFAULT
	goto SF_SeedDone
SF_SeedRecoveredNotes::
	msgbox SF_SeedTextRecoveredNotes, MSGBOX_DEFAULT
	goto SF_SeedDone

SF_SeedCareNotes::
	lockall
	goto_if_unset FLAG_SYS_POKEMON_GET, SF_SeedBeforeCompanion
	goto_if_set FLAG_UNUSED_0x041, SF_SeedAfterBench
	msgbox SF_SeedTextCareNotes, MSGBOX_DEFAULT
	goto SF_SeedDone
SF_SeedBeforeCompanion::
	msgbox SF_SeedTextBeforeCompanion, MSGBOX_DEFAULT
	goto SF_SeedDone
SF_SeedAfterBench::
	msgbox SF_SeedTextAfterBench, MSGBOX_DEFAULT
SF_SeedDone::
	releaseall
	end

SF_SeedTextFieldNotes::
	.string "SEED ROOM / FIELD NOTES\nThe margin says: CHECK THE WINDOW.\pROON left a spare beacon in your\nSUNSET room. Compare it with fog.\pA copied forecast can look perfect\nand still describe the wrong day.$"
SF_SeedTextRecoveredNotes::
	.string "FIELD NOTE: PROTOTYPE RECOVERED.\nOne reading is not the whole story.\pThe spare beacon in your SUNSET\nroom can be checked at the window.\pTwo readings are more useful than\none very confident pitch deck.$"
SF_SeedTextBeaconNotes::
	.string "FIELD NOTE: TWO SIGNALS.\nYour home beacon now reads FOG.\pA faint second pulse sits under it.\nKeep the main delivery first.\pCompare COGNITION'S relay lights.\nLabel the reading, not the hype.$"
SF_SeedTextBadgeNotes::
	.string "FIELD NOTE: BUILD BADGE EARNED.\nThe park's relays are steady.\pA pencil arrow points back to the\nspare beacon in your SUNSET room.\pCheck it against the window.\nThe quieter signal is worth a look.$"
SF_SeedTextBadgeBeaconNotes::
	.string "FIELD NOTE: BUILD BADGE EARNED.\nTwo signals still share a frequency.\pYou found the quieter pulse at home.\nThe relay work did not erase it.\pThe notebook's last line is simple:\nGood questions survive the demo.$"
SF_SeedTextCareNotes::
	.string "SEED ROOM / COMPANION CARE\nA held ORAN BERRY helps in battle.\pCheck the park's west-side bench.\nSomeone left a few ORAN BERRIES.\pBAG, BERRIES, GIVE equips one.\nIt activates when HP runs low.$"
SF_SeedTextBeforeCompanion::
	.string "SEED ROOM / COMPANION CARE\nFirst, find someone to travel with.\pKARPATHY can help in the SUNSET.\nChoose a field companion there.\pThen give it a berry to hold.\nA little care can help in battle.$"
SF_SeedTextAfterBench::
	.string "SEED ROOM / COMPANION CARE\nThe bench notes mentioned berries.\pBAG, BERRIES, GIVE lets a companion\nhold an ORAN BERRY for battle.\pIt activates when HP runs low.\nSmall preparations beat big pitches.$"
