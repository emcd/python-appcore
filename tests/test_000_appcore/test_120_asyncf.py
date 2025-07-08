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


''' Async utilities and helper functions tests. '''


import asyncio
import pytest

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.asyncf"
module = cache_import_module( MODULE_QNAME )

exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )
generics_module = cache_import_module( f"{PACKAGE_NAME}.generics" )


@pytest.mark.asyncio
async def test_100_intercept_error_async_success( ):
    ''' Error interceptor returns Value for successful awaitable. '''
    async def successful_operation( ):
        return 42
    result = await module.intercept_error_async( successful_operation( ) )
    assert isinstance( result, generics_module.Value )
    assert result.extract( ) == 42


@pytest.mark.asyncio
async def test_110_intercept_error_async_failure( ):
    ''' Error interceptor returns Error for failing awaitable. '''
    async def failing_operation( ):
        raise ValueError( 'test error' )
    result = await module.intercept_error_async( failing_operation( ) )
    assert isinstance( result, generics_module.Error )
    assert isinstance( result.error, ValueError )
    assert str( result.error ) == 'test error'


@pytest.mark.asyncio
async def test_120_intercept_error_async_preserves_non_exceptions( ):
    ''' Error interceptor allows BaseException subclasses to propagate. '''
    async def keyboard_interrupt_operation( ):
        raise KeyboardInterrupt( 'user interrupt' )
    with pytest.raises( KeyboardInterrupt ):
        await module.intercept_error_async( keyboard_interrupt_operation( ) )


@pytest.mark.asyncio
async def test_130_gather_async_all_successful( ):
    ''' Async gatherer returns tuple of results for successful operations. '''
    async def operation1( ):
        return 'result1'
    async def operation2( ):
        return 'result2'
    results = await module.gather_async( operation1( ), operation2( ) )
    assert results == ( 'result1', 'result2' )


@pytest.mark.asyncio
async def test_140_gather_async_with_failures( ):
    ''' Async gatherer raises ExceptionGroup for failing operations. '''
    async def successful_operation( ):
        return 'success'
    async def failing_operation( ):
        raise ValueError( 'failure' )
    with pytest.raises( Exception ) as exc_info:  # ExceptionGroup in 3.11+
        await module.gather_async(
            successful_operation( ), failing_operation( ) )
    # Check that it's some form of exception group
    assert 'Failure of async operations' in str( exc_info.value )


@pytest.mark.asyncio
async def test_150_gather_async_return_exceptions( ):
    ''' Async gatherer returns results and errors with return_exceptions. '''
    async def successful_operation( ):
        return 'success'
    async def failing_operation( ):
        raise ValueError( 'failure' )
    results = await module.gather_async(
        successful_operation( ),
        failing_operation( ),
        return_exceptions = True
    )
    assert len( results ) == 2
    assert isinstance( results[ 0 ], generics_module.Value )
    assert isinstance( results[ 1 ], generics_module.Error )
    assert results[ 0 ].extract( ) == 'success'
    assert isinstance( results[ 1 ].error, ValueError )


@pytest.mark.asyncio
async def test_160_gather_async_ignore_nonawaitables( ):
    ''' Async gatherer handles non-awaitables in permissive mode. '''
    async def async_operation( ):
        return 'async_result'
    non_awaitable = 'sync_result'
    results = await module.gather_async(
        async_operation( ),
        non_awaitable,
        ignore_nonawaitables = True
    )
    assert results == ( 'async_result', 'sync_result' )


@pytest.mark.asyncio
async def test_170_gather_async_strict_nonawaitables( ):
    ''' Async gatherer raises AsyncAssertionFailure for non-awaitables. '''
    async def async_operation( ):
        return 'async_result'
    non_awaitable = 'sync_result'
    with pytest.raises( exceptions_module.AsyncAssertionFailure ):
        await module.gather_async( async_operation( ), non_awaitable )


@pytest.mark.asyncio
async def test_180_gather_async_custom_error_message( ):
    ''' Async gatherer uses custom error message in ExceptionGroup. '''
    async def failing_operation( ):
        raise ValueError( 'failure' )
    custom_message = 'Custom async failure message'
    with pytest.raises( Exception ) as exc_info:
        await module.gather_async(
            failing_operation( ),
            error_message = custom_message
        )
    assert custom_message in str( exc_info.value )


@pytest.mark.asyncio
async def test_190_gather_async_empty_input( ):
    ''' Async gatherer handles empty input correctly. '''
    results = await module.gather_async( )
    assert results == ( )


@pytest.mark.asyncio
async def test_200_gather_async_mixed_results( ):
    ''' Async gatherer handles mixed successful and failing operations. '''
    async def operation1( ):
        return 1
    async def operation2( ):
        raise ValueError( 'error2' )
    async def operation3( ):
        return 3
    async def operation4( ):
        raise TypeError( 'error4' )
    results = await module.gather_async(
        operation1( ),
        operation2( ),
        operation3( ),
        operation4( ),
        return_exceptions = True
    )
    assert len( results ) == 4
    assert results[ 0 ].extract( ) == 1
    assert isinstance( results[ 1 ].error, ValueError )
    assert results[ 2 ].extract( ) == 3
    assert isinstance( results[ 3 ].error, TypeError )


@pytest.mark.asyncio
async def test_210_gather_async_permissive_mixed( ):
    ''' Async gatherer permissive mode accepts mixed input types. '''
    async def async_op( ):
        return 'async'
    results = await module.gather_async(
        async_op( ),
        'sync1',
        42,
        [ 1, 2, 3 ],
        ignore_nonawaitables = True
    )
    assert results == ( 'async', 'sync1', 42, [ 1, 2, 3 ] )


@pytest.mark.asyncio
async def test_220_intercept_error_async_with_complex_types( ):
    ''' Error interceptor works with complex return types. '''
    async def complex_operation( ):
        return { 'data': [ 1, 2, 3 ], 'status': 'success' }
    result = await module.intercept_error_async( complex_operation( ) )
    assert isinstance( result, generics_module.Value )
    extracted = result.extract( )
    assert extracted[ 'data' ] == [ 1, 2, 3 ]
    assert extracted[ 'status' ] == 'success'


@pytest.mark.asyncio
@pytest.mark.slow
async def test_230_gather_async_large_number_of_operations( ):
    ''' Async gatherer handles many concurrent operations. '''
    async def numbered_operation( n ):
        await asyncio.sleep( 0.001 )  # Simulate small delay
        return n * 2
    operations = [ numbered_operation( i ) for i in range( 10 ) ]
    results = await module.gather_async( *operations )
    expected = tuple( i * 2 for i in range( 10 ) )
    assert results == expected