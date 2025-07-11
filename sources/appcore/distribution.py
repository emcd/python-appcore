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


''' Information about package distribution. '''


from . import __
from . import exceptions as _exceptions
from . import io as _io


class Information( __.immut.DataclassObject ):
    ''' Information about a package distribution. '''

    name: str
    location: __.Path
    editable: bool

    @classmethod
    async def prepare(
        selfclass,
        exits: __.ctxl.AsyncExitStack,
        anchor: __.Absential[ __.Path ] = __.absent,
        package: __.Absential[ str ] = __.absent,
    ) -> __.typx.Self:
        ''' Acquires information about package distribution. '''
        if (    __.is_absent( anchor )
            and getattr( __.sys, 'frozen', False )
            and hasattr( __.sys, '_MEIPASS' )
        ): # pragma: no cover
            location, name = await _acquire_pyinstaller_information( )
            return selfclass(
                editable = False, location = location, name = name )
        if __.is_absent( package ):
            package, _ = _discover_invoker_location( )
        if not __.is_absent( package ):
            # TODO: Python 3.12: importlib.metadata
            from importlib_metadata import packages_distributions
            name = packages_distributions( ).get( package )
            if name:
                location = (
                    await _acquire_production_location( package, exits ) )
                return selfclass(
                    editable = False, location = location, name = name[ 0 ] )
        # https://github.com/pypa/packaging-problems/issues/609
        # Development sources rather than distribution.
        # Implies no use of importlib.resources.
        if __.is_absent( anchor ):
            _, anchor = _discover_invoker_location( )
        location, name = (
            await _acquire_development_information( anchor = anchor ) )
        return selfclass(
            editable = True, location = location, name = name )

    def provide_data_location( self, *appendages: str ) -> __.Path:
        ''' Provides location of distribution data. '''
        base = self.location / 'data'
        if appendages: return base.joinpath( *appendages )
        return base


async def _acquire_development_information(
    anchor: __.Path
) -> tuple[ __.Path, str ]:
    location = _locate_pyproject( anchor )
    pyproject = await _io.acquire_text_file_async(
        location / 'pyproject.toml', deserializer = __.tomli.loads )
    name = pyproject[ 'project' ][ 'name' ]
    return location, name


async def _acquire_production_location(
    package: str, exits: __.ctxl.AsyncExitStack
) -> __.Path:
    # TODO: Python 3.12: importlib.resources
    from importlib_resources import files, as_file # pyright: ignore
    # Extract package contents to temporary directory, if necessary.
    return exits.enter_context(
        as_file( files( package ) ) ) # pyright: ignore


async def _acquire_pyinstaller_information( # pragma: no cover
) -> tuple[ __.Path, str ]:
    anchor_ = __.Path(
        getattr( __.sys, '_MEIPASS' ) )
    # TODO: More rigorously determine package name.
    #       Currently assumes 'pyproject.toml' is present in distribution.
    return await _acquire_development_information( anchor = anchor_ )


def _discover_invoker_location( ) -> tuple[ __.Absential[ str ], __.Path ]:
    ''' Discovers file path of caller for project root detection. '''
    import inspect
    package_location = __.Path( __file__ ).parent.resolve( )
    python_location = __.Path( __.sys.executable ).parent.parent.resolve( )
    frame = inspect.currentframe( )
    if frame is None: return __.absent, __.Path.cwd( )
    # Walk up the call stack to find frame outside of this package.
    while True:
        frame = frame.f_back
        if frame is None: break # pragma: no cover
        location = __.Path( frame.f_code.co_filename).resolve( )
        # Skip frames within this package and Python installation.
        if location.is_relative_to( package_location ): # pragma: no cover
            continue
        if location.is_relative_to( python_location ): # pragma: no cover
            continue
        mname = frame.f_globals.get( '__module__' )
        if not mname: continue
        pname = mname.split( '.', maxsplit = 1 )[ 0 ]
        return pname, location.parent
    # Fallback location is current working directory.
    return __.absent, __.Path.cwd( ) # pragma: no cover


def _locate_pyproject( project_anchor: __.Path ) -> __.Path:
    ''' Finds project manifest, if it exists. Errors otherwise. '''
    initial = project_anchor.resolve( )
    current = initial if initial.is_dir( ) else initial.parent
    limits: set[ __.Path ] = set( )
    for limits_variable in ( 'GIT_CEILING_DIRECTORIES', ):
        limits_value = __.os.environ.get( limits_variable )
        if not limits_value: continue  # pragma: no cover
        limits.update(  # pragma: no cover
            __.Path( limit ).resolve( )
            for limit in limits_value.split( ':' ) if limit.strip( ) )
    while current != current.parent:  # Not at filesystem root
        if ( current / 'pyproject.toml' ).exists( ):
            return current
        if current in limits:
            raise _exceptions.FileLocateFailure(  # noqa: TRY003 # pragma: no cover
                'project root discovery', 'pyproject.toml' )
        current = current.parent
    raise _exceptions.FileLocateFailure(  # noqa: TRY003 # pragma: no cover
        'project root discovery', 'pyproject.toml' )
