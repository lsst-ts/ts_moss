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
__all__ = ["CONFIG_SCHEMA"]

import yaml

CONFIG_SCHEMA = yaml.safe_load(
    """
$schema: http://json-schema.org/draft-07/schema#
$id: https://github.com/lsst-ts/ts_moss/blob/main/schema/MOSS.yaml
title: MOSS v1
description: Schema for MOSS configuration files.
type: object
properties:
  instances:
    type: array
    items:
      type: object
      properties:
        sal_index:
          type: integer
          minValue: 1
        tcpip:
          type: object
          properties:
            hostname:
              type: string
            port:
              type: integer
            timeout:
              type: integer
          required:
            - hostname
            - port
            - timeout
          additionalProperties: false
        s3_instance:
          type: string
          enum:
            - tuc
            - ls
            - cp
    required:
        - sal_index
        - tcpip
        - s3_instance
    additionalProperties: false

required:
  - instances

additionalProperties: false
"""
)
