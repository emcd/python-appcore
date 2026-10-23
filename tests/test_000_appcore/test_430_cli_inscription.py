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


''' CLI inscription control tests. '''


import contextlib

from absence import is_absent

from appcore import inscription as inscription_module
from appcore.cli import core as module


def test_100_inscription_control_defaults( ):
    ''' InscriptionControl defaults leave ictr fields unset. '''
    control = module.InscriptionControl( )
    assert control.active_flavors is None
    assert control.trace_levels is None
    assert control.level == 'info'


def test_110_as_control_passes_ictr_fields( ):
    ''' as_control passes active flavors and trace levels through. '''
    control = module.InscriptionControl(
        active_flavors = ( 'note', 'error' ),
        trace_levels = 2,
        level = 'debug',
    )
    with contextlib.ExitStack( ) as exits:
        result = control.as_control( exits )
    assert isinstance( result, inscription_module.Control )
    assert result.active_flavors == ( 'note', 'error' )
    assert result.trace_levels == 2
    assert result.level == 'debug'
    assert result.mode == inscription_module.Presentations.Plain


def test_120_as_control_omits_absent_ictr_fields( ):
    ''' as_control leaves ictr fields absent when CLI options unset. '''
    control = module.InscriptionControl( )
    with contextlib.ExitStack( ) as exits:
        result = control.as_control( exits )
    assert is_absent( result.active_flavors )
    assert is_absent( result.trace_levels )
