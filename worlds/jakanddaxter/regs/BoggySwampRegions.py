from typing import List
from BaseClasses import CollectionState, MultiWorld
from .RegionBase import JakAndDaxterRegion
from ..Rules import can_fight


def build_regions(level_name: str, player: int, multiworld: MultiWorld) -> List[JakAndDaxterRegion]:

    # This level is full of short-medium gaps that cannot be crossed by single jump alone.
    # These helper functions list out the moves that can cross all these gaps (painting with a broad brush but...)
    def can_jump_farther(state: CollectionState, p: int) -> bool:
        return (state.has("Double Jump", p)
                or state.has("Jump Kick", p)
                or state.has("Punch Uppercut", p))

    def can_jump_higher(state: CollectionState, p: int) -> bool:
        return (state.has("Double Jump", p)
                or state.has("Crouch Jump", p)
                or state.has("Crouch Uppercut", p)
                or state.has("Punch Uppercut", p))

    # Orb crates and fly box in this area can be gotten with yellow eco and goggles.
    main_area = JakAndDaxterRegion("Main Area", player, multiworld, level_name, 23)
    main_area.add_fly_locations([43])

    # Includes 4 orbs collectable with the blue eco vent.
    first_bats = JakAndDaxterRegion("First Bats Area", player, multiworld, level_name, 4)

    first_jump_pad = JakAndDaxterRegion("First Jump Pad", player, multiworld, level_name, 0)
    first_jump_pad.add_fly_locations([393259])

    # First tether cell is collectable with yellow eco and goggles.
    first_tether = JakAndDaxterRegion("First Tether", player, multiworld, level_name, 7)
    first_tether.add_cell_locations([39])

    # This rat colony has 3 orbs on top of it, requires special movement.
    first_tether_rat_colony = JakAndDaxterRegion("First Tether Rat Colony", player, multiworld, level_name, 3)

    # If quick enough, combat not required.
    second_jump_pad = JakAndDaxterRegion("Second Jump Pad", player, multiworld, level_name, 0)
    second_jump_pad.add_fly_locations([65579])

    first_pole_course = JakAndDaxterRegion("First Pole Course", player, multiworld, level_name, 28)

    # You can break this tether with a yellow eco vent and goggles,
    # but you can't reach the platform unless you can jump high.
    second_tether = JakAndDaxterRegion("Second Tether", player, multiworld, level_name, 0)
    second_tether.add_cell_locations([40], access_rule=lambda state: can_jump_higher(state, player))

    # Fly and orbs are collectable with nearby blue eco cluster.
    second_bats = JakAndDaxterRegion("Second Bats Area", player, multiworld, level_name, 27)
    second_bats.add_fly_locations([262187], access_rule=lambda state: can_jump_farther(state, player))

    third_jump_pad = JakAndDaxterRegion("Third Jump Pad (Arena)", player, multiworld, level_name, 0)
    third_jump_pad.add_cell_locations([38], access_rule=lambda state: can_fight(state, player))

    # The platform for the third tether might look high, but you can get a boost from the yellow eco vent.
    fourth_jump_pad = JakAndDaxterRegion("Fourth Jump Pad (Third Tether)", player, multiworld, level_name, 9)
    fourth_jump_pad.add_cell_locations([41])

    # Orbs collectable here with yellow eco and goggles.
    flut_flut_pad = JakAndDaxterRegion("Flut Flut Pad", player, multiworld, level_name, 36)

    flut_flut_course = JakAndDaxterRegion("Flut Flut Course", player, multiworld, level_name, 23)
    flut_flut_course.add_cell_locations([37])
    flut_flut_course.add_fly_locations([327723, 131115])

    # Includes some orbs on the way to the cabin, blue+yellow eco to collect.
    farthy_snacks = JakAndDaxterRegion("Farthy's Snacks", player, multiworld, level_name, 7)
    farthy_snacks.add_cell_locations([36])

    # Scout fly in this field can be broken with yellow eco.
    box_field = JakAndDaxterRegion("Field of Boxes", player, multiworld, level_name, 10)
    box_field.add_fly_locations([196651])

    last_tar_pit = JakAndDaxterRegion("Last Tar Pit", player, multiworld, level_name, 12)

    fourth_tether = JakAndDaxterRegion("Fourth Tether", player, multiworld, level_name, 11)
    fourth_tether.add_cell_locations([42], access_rule=lambda state: can_jump_higher(state, player))

    main_area.connect(first_bats, rule=lambda state: can_jump_farther(state, player))

    first_bats.connect(main_area)
    first_bats.connect(first_jump_pad)
    first_bats.connect(first_tether)

    first_tether.connect(first_bats)
    first_tether.connect(first_tether_rat_colony, rule=lambda state:
                         state.has("Roll Jump", player)
                         or (state.has("Double Jump", player)
                             and state.has("Jump Kick", player)))
    first_tether.connect(second_jump_pad)
    first_tether.connect(first_pole_course)

    first_pole_course.connect(first_tether)
    first_pole_course.connect(second_tether)

    second_tether.connect(first_pole_course, rule=lambda state: can_jump_higher(state, player))
    second_tether.connect(second_bats)

    second_bats.connect(second_tether)
    second_bats.connect(third_jump_pad)
    second_bats.connect(fourth_jump_pad)
    second_bats.connect(flut_flut_pad)

    flut_flut_pad.connect(second_bats)
    flut_flut_pad.connect(flut_flut_course, rule=lambda state: state.has("Flut Flut", player))  # Naturally.
    flut_flut_pad.connect(farthy_snacks)

    farthy_snacks.connect(flut_flut_pad)
    farthy_snacks.connect(box_field, rule=lambda state: can_jump_higher(state, player))

    box_field.connect(farthy_snacks, rule=lambda state: can_jump_higher(state, player))
    box_field.connect(last_tar_pit, rule=lambda state: can_jump_farther(state, player))

    last_tar_pit.connect(box_field, rule=lambda state: can_jump_farther(state, player))
    last_tar_pit.connect(fourth_tether, rule=lambda state: can_jump_farther(state, player))

    fourth_tether.connect(last_tar_pit, rule=lambda state: can_jump_farther(state, player))
    fourth_tether.connect(main_area)  # Fall down.

    multiworld.regions.append(main_area)
    multiworld.regions.append(first_bats)
    multiworld.regions.append(first_jump_pad)
    multiworld.regions.append(first_tether)
    multiworld.regions.append(first_tether_rat_colony)
    multiworld.regions.append(second_jump_pad)
    multiworld.regions.append(first_pole_course)
    multiworld.regions.append(second_tether)
    multiworld.regions.append(second_bats)
    multiworld.regions.append(third_jump_pad)
    multiworld.regions.append(fourth_jump_pad)
    multiworld.regions.append(flut_flut_pad)
    multiworld.regions.append(flut_flut_course)
    multiworld.regions.append(farthy_snacks)
    multiworld.regions.append(box_field)
    multiworld.regions.append(last_tar_pit)
    multiworld.regions.append(fourth_tether)

    return [main_area]
