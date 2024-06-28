from typing import List, Callable
from BaseClasses import MultiWorld, Region
from ..GameID import jak1_name
from ..JakAndDaxterOptions import JakAndDaxterOptions
from ..Locations import JakAndDaxterLocation, location_table
from ..locs import (OrbLocations as Orbs,
                    CellLocations as Cells,
                    ScoutLocations as Scouts,
                    SpecialLocations as Specials,
                    OrbCacheLocations as Caches)


class JakAndDaxterRegion(Region):
    """
    Holds region information such as name, level name, number of orbs available, etc.
    We especially need orb counts to be tracked because we need to know when you can
    afford the 90-orb and 120-orb payments for more checks.
    """
    game: str = jak1_name
    level_name: str
    orb_count: int

    def __init__(self, name: str, player: int, multiworld: MultiWorld, level_name: str = "", orb_count: int = 0):
        formatted_name = f"{level_name} {name}".strip()
        super().__init__(formatted_name, player, multiworld)
        self.level_name = level_name
        self.orb_count = orb_count

    def add_cell_locations(self, locations: List[int], access_rule: Callable = None):
        """
        Adds a Power Cell Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            ap_id = Cells.to_ap_id(loc)
            self.add_jak_locations(ap_id, location_table[ap_id], access_rule)

    def add_fly_locations(self, locations: List[int], access_rule: Callable = None):
        """
        Adds a Scout Fly Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            ap_id = Scouts.to_ap_id(loc)
            self.add_jak_locations(ap_id, location_table[ap_id], access_rule)

    def add_special_locations(self, locations: List[int], access_rule: Callable = None):
        """
        Adds a Special Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        Special Locations should be matched alongside their respective
        Power Cell Locations, so you get 2 unlocks for these rather than 1.
        """
        for loc in locations:
            ap_id = Specials.to_ap_id(loc)
            self.add_jak_locations(ap_id, location_table[ap_id], access_rule)

    def add_cache_locations(self, locations: List[int],  access_rule: Callable = None):
        """
        Adds an Orb Cache Location to this region with the given access rule.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            ap_id = Caches.to_ap_id(loc)
            self.add_jak_locations(ap_id, location_table[ap_id], access_rule)

    def add_orb_locations(self, locations: List[int], access_rule: Callable = None):
        """
        Adds an Orb Location to this region with the given access rule. Used only when Orbsanity is enabled.
        Converts Game ID's to AP ID's for you.
        """
        for loc in locations:
            ap_id = Orbs.to_ap_id(loc)
            self.add_jak_locations(ap_id, f"{self.name} Orb Bundle {loc + 1}", access_rule)

    def add_jak_locations(self, ap_id: int, name: str, access_rule: Callable = None):
        """
        Helper function to add Locations. Not to be used directly.
        """
        location = JakAndDaxterLocation(self.player, name, ap_id, self)
        if access_rule:
            location.access_rule = access_rule
        self.locations.append(location)
