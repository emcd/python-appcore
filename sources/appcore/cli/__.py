# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Internal imports and utilities for CLI subpackage. '''


# ruff: noqa: F401,F403

from .. import inscription

from ..__ import *
from ..exceptions import DependencyAbsence
from ..preparation import prepare
from ..state import Globals


try: import rich
except ImportError as _error:  # pragma: no cover
    raise DependencyAbsence( 'rich', 'CLI' ) from _error
try: import tomli_w
except ImportError as _error:  # pragma: no cover
    raise DependencyAbsence( 'tomli-w', 'CLI' ) from _error
try: import tyro
except ImportError as _error:  # pragma: no cover
    raise DependencyAbsence( 'tyro', 'CLI' ) from _error
