"""District-specific ordinary frontage rhythm and coordinated house paint."""
FORMS={
 'presidio':('gable','duplex','walkup','gable','flats','duplex','workshop','arcade','deco','shophouse','walkup','gable'),
 'dogpatch':('workshop','flats','workshop','arcade','workshop','shophouse','flats','workshop','walkup','gable','deco','duplex','workshop','arcade','flats','shophouse'),
 'potrero_hill':('gable','walkup','duplex','gable','flats','walkup','duplex','shophouse','workshop','deco','arcade','walkup'),
 'mission':('shophouse','arcade','walkup','duplex','shophouse','workshop','arcade','walkup','flats','gable','deco','duplex'),
 'castro':('arcade','shophouse','deco','walkup','duplex','shophouse','arcade','flats','gable','workshop','deco','walkup'),
 'outer_sunset':('walkup','duplex','gable','walkup','flats','duplex','gable','shophouse','workshop','deco','arcade','duplex'),
 'marina':('shophouse','walkup','duplex','arcade','walkup','flats','shophouse','gable','deco','workshop','duplex','arcade'),
 'pacific_heights':('gable','duplex','walkup','deco','gable','flats','duplex','walkup','arcade','shophouse','workshop','deco'),
 'noe_valley':('walkup','gable','duplex','shophouse','walkup','duplex','gable','flats','arcade','workshop','deco','shophouse'),
 'mission_bay':('deco','flats','arcade','deco','workshop','flats','arcade','deco','walkup','shophouse','gable','duplex'),
 'giants_stadium':('arcade','shophouse','workshop','arcade','flats','deco','shophouse','walkup','gable','duplex','arcade','workshop'),
 'financial_district':('deco','flats','arcade','deco','flats','workshop','arcade','deco','walkup','shophouse','gable','duplex'),
 'north_beach':('shophouse','arcade','walkup','shophouse','duplex','arcade','flats','gable','deco','workshop','walkup','arcade'),
 'treasure_island':('workshop','flats','arcade','workshop','shophouse','flats','deco','workshop','walkup','gable','duplex','arcade'),
}
PAINT={
 'presidio':(1,0,2,1,0),
 'dogpatch':(0,0,0,1),'potrero_hill':(0,2,1,0,1),
 'mission':(0,1,0,2,1),'castro':(0,1,2,0,2),
 'outer_sunset':(0,1,0,2,0),'marina':(0,0,1,0,2),
 'pacific_heights':(0,2,0,1,0),'noe_valley':(1,0,1,2,0),
 'mission_bay':(2,1,2,0,2),'giants_stadium':(0,2,0,1,0),
 'financial_district':(2,2,2,0,1),'north_beach':(0,0,2,1,0),
 'treasure_island':(0,0,1,0),
}


def frontage(identifier,index,x,y,catalog):
    rhythm=FORMS[identifier];family=rhythm[index%len(rhythm)]
    schemes=PAINT[identifier]
    paint=schemes[(x*7+y*11+index*3+len(identifier))%len(schemes)]
    style=family+('','__sage','__slate')[paint]
    return style if style in catalog else family
