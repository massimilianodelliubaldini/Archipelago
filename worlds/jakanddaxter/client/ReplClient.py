import time
import struct
from socket import socket, AF_INET, SOCK_STREAM

import pymem
from pymem.exception import ProcessNotFound, ProcessError

from CommonClient import logger
from worlds.jakanddaxter.locs import (
    CellLocations as Cells,
    ScoutLocations as Flies,
    OrbLocations as Orbs,
    SpecialLocations as Specials)
from worlds.jakanddaxter.GameID import jak1_id


class JakAndDaxterReplClient:
    ip: str
    port: int
    sock: socket
    connected: bool = False
    initiated_connect: bool = False  # Signals when user tells us to try reconnecting.

    # The REPL client needs the REPL/compiler process running, but that process
    # also needs the game running. Therefore, the REPL client needs both running.
    gk_process: pymem.process = None
    goalc_process: pymem.process = None

    item_inbox = {}
    inbox_index = 0

    def __init__(self, ip: str = "127.0.0.1", port: int = 8181):
        self.ip = ip
        self.port = port
        self.connect()

    async def main_tick(self):
        if self.initiated_connect:
            await self.connect()
            self.initiated_connect = False

        if self.connected:
            try:
                self.gk_process.read_bool(self.gk_process.base_address)  # Ping to see if it's alive.
            except ProcessError:
                logger.error("The gk process has died. Restart the game and run \"/repl connect\" again.")
                self.connected = False
            try:
                self.goalc_process.read_bool(self.goalc_process.base_address)  # Ping to see if it's alive.
            except ProcessError:
                logger.error("The goalc process has died. Restart the compiler and run \"/repl connect\" again.")
                self.connected = False
        else:
            return

        # Receive Items from AP. Handle 1 item per tick.
        if len(self.item_inbox) > self.inbox_index:
            self.receive_item()
            self.inbox_index += 1

    # This helper function formats and sends `form` as a command to the REPL.
    # ALL commands to the REPL should be sent using this function.
    # TODO - this blocks on receiving an acknowledgement from the REPL server. But it doesn't print
    #  any log info in the meantime. Is that a problem?
    def send_form(self, form: str, print_ok: bool = True) -> bool:
        header = struct.pack("<II", len(form), 10)
        self.sock.sendall(header + form.encode())
        response = self.sock.recv(1024).decode()
        if "OK!" in response:
            if print_ok:
                logger.info(response)
            return True
        else:
            logger.error(f"Unexpected response from REPL: {response}")
            return False

    async def connect(self):
        try:
            self.gk_process = pymem.Pymem("gk.exe")  # The GOAL Kernel
            logger.info("Found the gk process: " + str(self.gk_process.process_id))
        except ProcessNotFound:
            logger.error("Could not find the gk process.")
            return

        try:
            self.goalc_process = pymem.Pymem("goalc.exe")  # The GOAL Compiler and REPL
            logger.info("Found the goalc process: " + str(self.goalc_process.process_id))
        except ProcessNotFound:
            logger.error("Could not find the goalc process.")
            return

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.ip, self.port))
            time.sleep(1)
            welcome_message = self.sock.recv(1024).decode()

            # Should be the OpenGOAL welcome message (ignore version number).
            if "Connected to OpenGOAL" and "nREPL!" in welcome_message:
                logger.info(welcome_message)
            else:
                logger.error(f"Unable to connect to REPL websocket: unexpected welcome message \"{welcome_message}\"")
        except ConnectionRefusedError as e:
            logger.error(f"Unable to connect to REPL websocket: {e.strerror}")
            return

        ok_count = 0
        if self.sock:

            # Have the REPL listen to the game's internal websocket.
            if self.send_form("(lt)", print_ok=False):
                ok_count += 1

            # Show this visual cue when compilation is started.
            # It's the version number of the OpenGOAL Compiler.
            if self.send_form("(set! *debug-segment* #t)", print_ok=False):
                ok_count += 1

            # Play this audio cue when compilation is started.
            # It's the sound you hear when you press START + CIRCLE to open the Options menu.
            if self.send_form("(dotimes (i 1) "
                              "(sound-play-by-name "
                              "(static-sound-name \"start-options\") "
                              "(new-sound-id) 1024 0 0 (sound-group sfx) #t))", print_ok=False):
                ok_count += 1

            # Start compilation. This is blocking, so nothing will happen until the REPL is done.
            if self.send_form("(mi)", print_ok=False):
                ok_count += 1

            # Play this audio cue when compilation is complete.
            # It's the sound you hear when you press START + START to close the Options menu.
            if self.send_form("(dotimes (i 1) "
                              "(sound-play-by-name "
                              "(static-sound-name \"menu-close\") "
                              "(new-sound-id) 1024 0 0 (sound-group sfx) #t))", print_ok=False):
                ok_count += 1

            # Disable cheat-mode and debug (close the visual cue).
            # self.send_form("(set! *debug-segment* #f)")
            if self.send_form("(set! *cheat-mode* #f)"):
                ok_count += 1

            # Now wait until we see the success message... 6 times.
            if ok_count == 6:
                self.connected = True
            else:
                self.connected = False

        if self.connected:
            logger.info("The REPL is ready!")

    def print_status(self):
        logger.info("REPL Status:")
        logger.info("  REPL process ID: " + (str(self.goalc_process.process_id) if self.goalc_process else "None"))
        logger.info("  Game process ID: " + (str(self.gk_process.process_id) if self.gk_process else "None"))
        try:
            if self.sock:
                ip, port = self.sock.getpeername()
                logger.info("  Game websocket: " + (str(ip) + ", " + str(port) if ip else "None"))
                self.send_form("(dotimes (i 1) "
                               "(sound-play-by-name "
                               "(static-sound-name \"menu-close\") "
                               "(new-sound-id) 1024 0 0 (sound-group sfx) #t))", print_ok=False)
        except:
            logger.warn("  Game websocket not found!")
        logger.info("  Did you hear the success audio cue?")
        logger.info("  Last item received: " + (str(getattr(self.item_inbox[self.inbox_index], "item"))
                                                if self.inbox_index else "None"))

    def receive_item(self):
        ap_id = getattr(self.item_inbox[self.inbox_index], "item")

        # Determine the type of item to receive.
        if ap_id in range(jak1_id, jak1_id + Flies.fly_offset):
            self.receive_power_cell(ap_id)
        elif ap_id in range(jak1_id + Flies.fly_offset, jak1_id + Specials.special_offset):
            self.receive_scout_fly(ap_id)
        elif ap_id in range(jak1_id + Specials.special_offset, jak1_id + Orbs.orb_offset):
            self.receive_special(ap_id)
        # elif ap_id in range(jak1_id + Orbs.orb_offset, ???):
        #     pass  # TODO -- ^^.
        else:
            raise KeyError(f"Tried to receive item with unknown AP ID {ap_id}.")

    def receive_power_cell(self, ap_id: int) -> bool:
        cell_id = Cells.to_game_id(ap_id)
        ok = self.send_form("(send-event "
                            "*target* \'get-archipelago "
                            "(pickup-type fuel-cell) "
                            "(the float " + str(cell_id) + "))")
        if ok:
            logger.info(f"Received power cell {cell_id}!")
        else:
            logger.error(f"Unable to receive power cell {cell_id}!")
        return ok

    def receive_scout_fly(self, ap_id: int) -> bool:
        fly_id = Flies.to_game_id(ap_id)
        ok = self.send_form("(send-event "
                            "*target* \'get-archipelago "
                            "(pickup-type buzzer) "
                            "(the float " + str(fly_id) + "))")
        if ok:
            logger.info(f"Received scout fly {fly_id}!")
        else:
            logger.error(f"Unable to receive scout fly {fly_id}!")
        return ok

    def receive_special(self, ap_id: int) -> bool:
        special_id = Specials.to_game_id(ap_id)
        ok = self.send_form("(send-event "
                            "*target* \'get-archipelago "
                            "(pickup-type ap-special) "
                            "(the float " + str(special_id) + "))")
        if ok:
            logger.info(f"Received special unlock {special_id}!")
        else:
            logger.error(f"Unable to receive special unlock {special_id}!")
        return ok
