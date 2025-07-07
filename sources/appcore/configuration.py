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


''' Fundamental configuration. '''
# TODO: Add configuration validation (schema validation, type checking)


from . import __
from . import dictedits as _dictedits
from . import distribution as _distribution
from . import exceptions as _exceptions
from . import io as _io


class EnablementTristate( __.enum.Enum ): # TODO: Python 3.11: StrEnum
    ''' Disable, enable, or retain the natural state? '''

    Disable = 'disable'
    Retain = 'retain'
    Enable = 'enable'

    def __bool__( self ) -> bool:
        if self.Disable is self: return False
        if self.Enable is self: return True
        raise _exceptions.OperationInvalidity( # noqa: TRY003
            'inert enablement tristate', 'boolean translation' )

    def is_retain( self ) -> bool:
        ''' Does enum indicate a retain state? '''
        return self.Retain is self


async def acquire(
    application_name: str,
    directories: __.pdirs.PlatformDirs,
    distribution: _distribution.Information,
    edits: _dictedits.Edits = ( ),
    file: __.Absential[ __.Path | __.io.TextIOBase ] = __.absent,
) -> __.accret.Dictionary[ str, __.typx.Any ]:
    ''' Loads configuration as dictionary. '''
    if __.is_absent( file ):
        file = _discover_copy_template( directories, distribution )
    if isinstance( file, __.io.TextIOBase ):
        content = file.read( )
        configuration = __.tomli.loads( content )
    else:
        configuration = await _io.acquire_text_file_async(
            file, deserializer = __.tomli.loads )
    includes = await _acquire_includes(
        application_name, directories, configuration.get( 'includes', ( ) ) )
    for include in includes: configuration.update( include )
    for edit in edits: edit( configuration )
    return __.accret.Dictionary( configuration )


async def _acquire_includes(
    application_name: str,
    directories: __.pdirs.PlatformDirs,
    specs: tuple[ str, ... ]
) -> __.cabc.Sequence[ dict[ str, __.typx.Any ] ]:
    from itertools import chain
    locations = tuple(
        __.Path( spec.format(
            user_configuration = directories.user_config_path,
            user_home = __.Path.home( ),
            application_name = application_name ) )
        for spec in specs )
    iterables = tuple(
        ( location.glob( '*.toml' ) if location.is_dir( ) else ( location, ) )
        for location in locations )
    return await _io.acquire_text_files_async(
        *( file for file in chain.from_iterable( iterables ) ),
        deserializer = __.tomli.loads )


def _discover_copy_template(
    directories: __.pdirs.PlatformDirs,
    distribution: _distribution.Information,
) -> __.Path:
    file = directories.user_config_path / 'general.toml'
    if not file.exists( ):
        __.shutil.copyfile(
            distribution.provide_data_location(
                'configuration', 'general.toml' ), file )
    return file
