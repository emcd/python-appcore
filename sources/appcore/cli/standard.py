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


import json as _json

from . import __
from . import core as _core


class Presentations( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Basic presentation modes (formats). '''

    Json        = 'json'
    Markdown    = 'markdown'
    Toml        = 'toml'


class DisplayOptions( _core.DisplayOptions ):
    ''' Display options with presentation modes. '''

    compact: __.typx.Annotated[
        bool, __.ddoc.Doc( ''' Display CLI results compactly? ''' ),
    ] = False
    presentation: __.typx.Annotated[
        Presentations,
        __.ddoc.Doc( ''' Presentation mode for CLI display. ''' ),
    ] = Presentations.Markdown


class Globals( __.Globals ):
    ''' Application state with display options. '''

    display: DisplayOptions = __.dcls.field( default_factory = DisplayOptions )


class Renderable(
    __.immut.DataclassProtocol, __.typx.Protocol,
    decorators = ( __.typx.runtime_checkable, ),
):
    ''' Base class for objects which can render themselves. '''

    @__.abc.abstractmethod
    def render_dictionary( self ) -> dict[ str, __.typx.Any ]:
        ''' Returns dictionary representation of object attributes. '''
        raise NotImplementedError

    def render_json( self, compact: bool = False, indent: int = 2 ) -> str:
        ''' Renders object as JSON into string. '''
        dictionary = self.render_dictionary( )
        if compact:
            return _json.dumps(
                dictionary, ensure_ascii = False, separators = ( ',', ':' ) )
        return _json.dumps( dictionary, ensure_ascii = False, indent = indent )

    def render_markdown( self, display: DisplayOptions ) -> tuple[ str, ... ]:
        ''' Renders object as Markdown into sequence of lines. '''
        # TODO: Implement.
        return ( )

    def render_toml( self ) -> str:
        ''' Renders object as TOML into string. '''
        return __.tomli_w.dumps( self.render_dictionary( ) )


@__.ctxl.asynccontextmanager
async def intercept_errors(
    auxdata: Globals
) -> __.cabc.AsyncIterator[ None ]:
    # TODO? Utilize mapping of exceptions to exit codes.
    ''' Context manager which intercepts and renders exceptions. '''
    try: yield
    # TODO: Handle renderable exceptions.
    except ( KeyboardInterrupt, SystemExit ): raise
    except BaseException as exc:
        # TODO: Implement.
        raise SystemExit( 1 ) from exc


async def render_and_print( auxdata: Globals, renderable: Renderable ) -> None:
    ''' Renders and prints object according to display options. '''
    display = auxdata.display
    exits = auxdata.exits
    stream = await display.provide_stream( exits )
    match display.presentation:
        case Presentations.Json:
            text = renderable.render_json( compact = display.compact )
        case Presentations.Markdown:
            text = '\n'.join( renderable.render_markdown( display ) )
        case Presentations.Toml:
            text = renderable.render_toml( )
    print( text, file = stream )
