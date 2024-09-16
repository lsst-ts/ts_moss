# This file is part of ts_moss.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["MOSS"]

import asyncio
import types

from lsst.ts import salobj, utils

from . import __version__, controller, enums, mock_server
from .config_schema import CONFIG_SCHEMA


class MOSS(salobj.ConfigurableCsc):
    """Class that implements the CSC for the Multi-Beam Optical Seein Sensor (MOSS).

    Parameters
    ----------
    index : `int`
        The index of the CSC.
    config_dir : `str`
        Path to config directory.
        One is provided for you in another method.
    initial_state : `lsst.ts.salobj.State`
        The initial state of the CSC.
        Should be used for unit tests and development.
    simulation_mode : `int`, optional
        Simulation mode. (the default is 0: do not simulate.)
    """

    valid_simulation_modes = (0, 1)
    version = __version__

    def __init__(
        self,
        index,
        config_dir=None,
        initial_state=salobj.State.STANDBY,
        simulation_mode=0,
    ):
        super().__init__(
            name="MOSS",
            index=index,
            config_schema=CONFIG_SCHEMA,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
        )
        self.simulator = None
        self.log.debug("finished initializing")

    async def configure(self, config):
        """Configure the Electrometer CSC.

        Parameters
        ----------
        config : `types.SimpleNamespace`
            The parsed yaml object.
        """
        for instance in config.instances:
            if instance["sal_index"] == self.salinfo.index:
                break
        if instance["sal_index"] != self.salinfo.index:
            raise RuntimeError(f"No configuration found for {self.salinfo.index=}")
        self.log.debug(f"instance is {instance}")

    async def handle_summary_state(self):
        """Handle the summary of the CSC.

        If transitioning to the disabled or enabled state

        * Start the simulator if simulation_mode is true.
        * Create a bucket object for LFA support.
        * Connect to the server if it is not connected already.

        If leaving the disabled state

        * Disconnect from the server, if connected.
        * If the simulator is running, stop it.
        """
        do_mock = False
        create = False
        if self.disabled_or_enabled:
            if self.simulation_mode and self.simulator is None:
                self.simulator = mock_server.MockServer(
                    self.controller.electrometer_type
                )
                await self.simulator.start_task
                do_mock = True
                create = True
            if self.bucket is None:
                self.bucket = salobj.AsyncS3Bucket(
                    salobj.AsyncS3Bucket.make_bucket_name(
                        s3instance=self.controller.s3_instance
                    ),
                    create=create,
                    domock=do_mock,
                )
            if not self.controller.connected:
                try:
                    await self.controller.connect()
                except Exception:
                    await self.fault(
                        code=enums.Error.CONNECTION, report="Connection failed."
                    )
        else:
            if self.controller is not None:
                if self.controller.connected:
                    await self.controller.disconnect()
            if self.simulator is not None:
                await self.simulator.close()
                self.simulator = None