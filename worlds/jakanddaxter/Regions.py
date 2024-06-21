import typing
from BaseClasses import MultiWorld
from .Items import item_table
from .JakAndDaxterOptions import JakAndDaxterOptions
from .locs import (CellLocations as Cells,
                   ScoutLocations as Scouts)
from .regs.RegionBase import JakAndDaxterRegion
from .regs import (GeyserRockRegions as GeyserRock,
                   SandoverVillageRegions as SandoverVillage,
                   ForbiddenJungleRegions as ForbiddenJungle,
                   SentinelBeachRegions as SentinelBeach,
                   MistyIslandRegions as MistyIsland,
                   FireCanyonRegions as FireCanyon,
                   RockVillageRegions as RockVillage,
                   PrecursorBasinRegions as PrecursorBasin,
                   LostPrecursorCityRegions as LostPrecursorCity,
                   BoggySwampRegions as BoggySwamp,
                   MountainPassRegions as MountainPass,
                   VolcanicCraterRegions as VolcanicCrater,
                   SpiderCaveRegions as SpiderCave,
                   SnowyMountainRegions as SnowyMountain,
                   LavaTubeRegions as LavaTube,
                   # GolAndMaiasCitadelRegions as GolAndMaiasCitadel
                   )


def create_regions(multiworld: MultiWorld, options: JakAndDaxterOptions, player: int):

    # Always start with Menu.
    menu = JakAndDaxterRegion("Menu", player, multiworld)
    multiworld.regions.append(menu)

    # Build the special "Free 7 Scout Flies" Region. This is a virtual region always accessible to Menu.
    # The Power Cells within it are automatically checked when you receive the 7th scout fly for the corresponding cell.
    free7 = JakAndDaxterRegion("'Free 7 Scout Flies' Power Cells", player, multiworld)
    free7.add_cell_locations(Cells.loc7SF_cellTable.keys())
    for scout_fly_cell in free7.locations:

        # Translate from Cell AP ID to Scout AP ID using game ID as an intermediary.
        scout_fly_id = Scouts.to_ap_id(Cells.to_game_id(scout_fly_cell.address))
        scout_fly_cell.access_rule = lambda state, flies=scout_fly_id: state.has(item_table[flies], player, 7)

    # Build all regions. Include their intra-connecting Rules, their Locations, and their Location access rules.
    [gr] = GeyserRock.build_regions("Geyser Rock", player, multiworld)
    [sv] = SandoverVillage.build_regions("Sandover Village", player, multiworld)
    [fj] = ForbiddenJungle.build_regions("Forbidden Jungle", player, multiworld)
    [sb] = SentinelBeach.build_regions("Sentinel Beach", player, multiworld)
    [mi] = MistyIsland.build_regions("Misty Island", player, multiworld)
    [fc] = FireCanyon.build_regions("Fire Canyon", player, multiworld)
    [rv, rvc] = RockVillage.build_regions("Rock Village", player, multiworld)
    [pb] = PrecursorBasin.build_regions("Precursor Basin", player, multiworld)
    [lpc] = LostPrecursorCity.build_regions("Lost Precursor City", player, multiworld)
    [bs] = BoggySwamp.build_regions("Boggy Swamp", player, multiworld)
    [mp, mpr] = MountainPass.build_regions("Mountain Pass", player, multiworld)
    [vc] = VolcanicCrater.build_regions("Volcanic Crater", player, multiworld)
    [sc] = SpiderCave.build_regions("Spider Cave", player, multiworld)
    [sm] = SnowyMountain.build_regions("Snowy Mountain", player, multiworld)
    [lt] = LavaTube.build_regions("Lava Tube", player, multiworld)
    # [gmc, fb] = GolAndMaiasCitadel.build_regions("Gol and Maia's Citadel", player, multiworld)

    # Define the interconnecting rules.
    menu.connect(free7)
    menu.connect(gr)
    gr.connect(sv)  # Geyser Rock modified to let you leave at any time.
    sv.connect(fj)
    sv.connect(sb)
    sv.connect(mi, rule=lambda state: state.has("Fisherman's Boat", player))
    sv.connect(fc, rule=lambda state: state.has("Power Cell", player, 20))
    fc.connect(rv)
    rv.connect(pb)
    rv.connect(lpc)
    rvc.connect(bs)  # rv->rvc connection defined internally by RockVillageRegions.
    rvc.connect(mp, rule=lambda state: state.has("Power Cell", player, 45))
    mpr.connect(vc)  # mp->mpr connection defined internally by MountainPassRegions.
    vc.connect(sc)
    vc.connect(sm, rule=lambda state: state.has("Snowy Mountain Gondola", player))
    vc.connect(lt, rule=lambda state: state.has("Power Cell", player, 72))
    # lt.connect(gmc)  # gmc->fb connection defined internally by GolAndMaiasCitadelRegions.

    # Finally, set the completion condition.
    # multiworld.completion_condition[player] = lambda state: state.can_reach(fb, "Region", player)

    # Confirm the total number of orbs in each level.
    level_orbs = {
        "Geyser Rock": 50,
        "Sandover Village": 50,
        "Forbidden Jungle": 150,
        "Sentinel Beach": 150,
        "Misty Island": 150,
        "Fire Canyon": 50,
        "Rock Village": 50,
        "Precursor Basin": 200,
        "Lost Precursor City": 200,
        "Boggy Swamp": 200,
        "Mountain Pass": 50,
        "Volcanic Crater": 50,
        "Spider Cave": 200,
        "Snowy Mountain": 200,
        "Lava Tube": 50,
        # "Gol and Maia's Citadel": 200,
    }
    for level in level_orbs:
        assert_orbs(multiworld, options, player, level_orbs[level], level)

    # As a final safety precaution, confirm the total number of orbs in the entire game.
    assert_orbs(multiworld, options, player, 2000)


def assert_orbs(multiworld: MultiWorld,
                options: JakAndDaxterOptions,
                player: int,
                total_orbs: int,
                level_name: str = None):
    regs = [typing.cast(JakAndDaxterRegion, reg) for reg in multiworld.get_regions(player)]
    if level_name:
        where = level_name
        regs = [reg for reg in regs if reg.level_name == level_name]
    else:
        where = "All of Jak and Daxter"
    orb_count = sum([reg.orb_count for reg in regs])
    assert orb_count == total_orbs, f"{where} has {total_orbs} orbs, but we've accounted for {orb_count}!"
