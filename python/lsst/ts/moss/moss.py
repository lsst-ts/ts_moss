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

import types

from lsst.ts import salobj

from .config_schema import CONFIG_SCHEMA


class MOSS(salobj.ConfigurableCsc):
    """Class that implements the CSC for the
    Multi-Beam Optical Seein Sensor (MOSS).

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

    def __init__(
        self,
        index: int,
        config_dir: str | None = None,
        initial_state: salobj.State = salobj.State.STANDBY,
        simulation_mode: int = 0,
    ) -> None:
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

    async def configure(self, config: types.SimpleNamespace) -> None:
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
