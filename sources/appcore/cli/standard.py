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


''' Standard renderers for basic CLI display presentation modes. '''


from . import __
from . import core as _core


@__.ctxl.asynccontextmanager
async def intercept_errors(
    application: _core.Application, auxdata: __.Globals
) -> __.cabc.AsyncIterator[ None ]:
    # TODO? Utilize mapping of exceptions to exit codes.
    ''' Context manager which intercepts and renders exceptions. '''
    try: yield
    except ( KeyboardInterrupt, SystemExit ): raise
    except BaseException as exc:
        await render_and_print( application, auxdata, exc )
        raise SystemExit( 1 ) from exc


async def render_and_print(
    application: _core.Application, auxdata: __.Globals, entity: object
) -> None:
    ''' Renders and prints object according to display options. '''
    exits = auxdata.exits
    printer = await application.clioptions.provide_printer( exits )
    control = printer.provide_textualization_control( )
    if not control: raise RuntimeError  # TODO: Appropriate error.
    presentation_name = application.clioptions.presentation
    try: presentation_ = _core.presentations_registry[ presentation_name ]
    except LookupError as exc:
        raise ValueError from exc  # TODO: Appropriate error.
    presentation = (
        getattr( application, presentation_ )
        if isinstance( presentation_, str )
        else presentation_( ) )
    state = __.ictrstd.LinearizerState.from_configuration(
        __.ictrstd.LinearizerConfiguration( ), control )
    text = presentation.render( state, entity )
    printer( text )
