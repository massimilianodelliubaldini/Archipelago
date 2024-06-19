from typing import List
from BaseClasses import CollectionState, MultiWorld
from ..Regions import JakAndDaxterRegion
from ..Rules import can_free_scout_flies, can_trade
from ..locs import ScoutLocations as Scouts


def build_regions(level_name: str, player: int, multiworld: MultiWorld) -> List[JakAndDaxterRegion]:

    # This is basically just Klaww.
    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 0)
    main_area.add_cell_locations([86])

    race = JakAndDaxterRegion("Race", player, multiworld, level_name, 50)
    race.add_cell_locations([87])

    # All scout flies can be broken with the zoomer.
    race.add_fly_locations(Scouts.locMP_scoutTable.keys())

    shortcut = JakAndDaxterRegion("Shortcut", player, multiworld, level_name, 0)
    shortcut.add_cell_locations([110])

    main_area.connect(race)
    race.connect(shortcut, rule=lambda state: state.has("Yellow Eco Switch", player))

    # TODO - This might not be required, but you can in fact NOT go backwards from Klaww.
    race.connect(main_area, rule=lambda state: False)

    multiworld.regions.append(main_area)
    multiworld.regions.append(race)
    multiworld.regions.append(shortcut)

    # Return race required for inter-level connections.
    return [main_area, race]
