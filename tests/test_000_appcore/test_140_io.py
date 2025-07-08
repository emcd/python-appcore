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


''' I/O utilities tests. '''


import tempfile
import pytest
from pathlib import Path

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.io"
module = cache_import_module( MODULE_QNAME )


@pytest.mark.asyncio
async def test_100_acquire_text_file_async_without_deserializer( ):
    ''' Text file acquisition returns raw text, no deserializer. '''
    content = 'test content\nline 2'
    with tempfile.NamedTemporaryFile(
        mode = 'w', delete = False ) as temp_file:
        temp_file.write( content )
        temp_file_path = Path( temp_file.name )
    try:
        result = await module.acquire_text_file_async( temp_file_path )
        assert result == content
        assert isinstance( result, str )
    finally:
        temp_file_path.unlink( )


@pytest.mark.asyncio
async def test_110_acquire_text_file_async_with_deserializer( ):
    ''' Text file acquisition applies deserializer when provided. '''
    import json
    data = { 'name': 'test', 'value': 42 }
    content = json.dumps( data )
    with tempfile.NamedTemporaryFile(
        mode = 'w', delete = False ) as temp_file:
        temp_file.write( content )
        temp_file_path = Path( temp_file.name )
    try:
        result = await module.acquire_text_file_async(
            temp_file_path,
            deserializer = json.loads
        )
        assert result == data
        assert isinstance( result, dict )
    finally:
        temp_file_path.unlink( )


@pytest.mark.asyncio
async def test_120_acquire_text_file_async_with_charset( ):
    ''' Text file acquisition respects charset parameter. '''
    content = 'test content'
    with tempfile.NamedTemporaryFile(
        mode = 'w', delete = False ) as temp_file:
        temp_file.write( content )
        temp_file_path = Path( temp_file.name )
    try:
        result = await module.acquire_text_file_async(
            temp_file_path,
            charset = 'utf-8'
        )
        assert result == content
    finally:
        temp_file_path.unlink( )


@pytest.mark.asyncio
async def test_130_acquire_text_files_async( ):
    ''' Text files acquisition handles multiple files. '''
    content1 = 'file 1 content'
    content2 = 'file 2 content'
    from contextlib import ExitStack
    with ExitStack() as stack:
        temp1 = stack.enter_context(
            tempfile.NamedTemporaryFile( mode = 'w', delete = False ) )
        temp2 = stack.enter_context(
            tempfile.NamedTemporaryFile( mode = 'w', delete = False ) )
        temp1.write( content1 )
        temp2.write( content2 )
        temp1_path = Path( temp1.name )
        temp2_path = Path( temp2.name )
    try:
        results = await module.acquire_text_files_async(
            temp1_path,
            temp2_path
        )
        assert len( results ) == 2
        assert results[ 0 ] == content1
        assert results[ 1 ] == content2
    finally:
        temp1_path.unlink( )
        temp2_path.unlink( )