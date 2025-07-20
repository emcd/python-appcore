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


''' Generic types and utilities tests. '''


import pytest

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.generics"
module = cache_import_module( MODULE_QNAME )


def test_100_value_creation( ):
    ''' Value result contains the provided value. '''
    value = module.Value( 42 )
    assert value.value == 42
    assert value.is_value( )
    assert not value.is_error( )


def test_110_error_creation( ):
    ''' Error result contains the provided error. '''
    error = ValueError( 'test error' )
    result = module.Error( error )
    assert result.error is error
    assert result.is_error( )
    assert not result.is_value( )


def test_120_value_extract( ):
    ''' Value result extract returns the contained value. '''
    value = module.Value( 'test' )
    assert value.extract( ) == 'test'


def test_130_error_extract( ):
    ''' Error result extract raises the contained error. '''
    error = ValueError( 'test error' )
    result = module.Error( error )
    with pytest.raises( ValueError, match = 'test error' ):
        result.extract( )


def test_140_value_transform( ):
    ''' Value result transform applies function to contained value. '''
    value = module.Value( 5 )
    transformed = value.transform( lambda x: x * 2 )
    assert isinstance( transformed, module.Value )
    assert transformed.extract( ) == 10


def test_150_error_transform( ):
    ''' Error result transform ignores function and returns self. '''
    error = ValueError( 'test error' )
    result = module.Error( error )
    transformed = result.transform( lambda x: x * 2 )
    assert transformed is result
    assert transformed.is_error( )


def test_160_value_match_args( ):
    ''' Value result supports pattern matching. '''
    value = module.Value( 42 )
    match value:
        case module.Value( v ):
            assert v == 42
        case _:
            pytest.fail( 'Value should match Value pattern' )


def test_170_error_match_args( ):
    ''' Error result supports pattern matching. '''
    error = ValueError( 'test' )
    result = module.Error( error )
    match result:
        case module.Error( e ):
            assert e is error
        case _:
            pytest.fail( 'Error should match Error pattern' )


def test_180_result_type_checking( ):
    ''' Result instances are proper subtypes. '''
    value = module.Value( 42 )
    error = module.Error( ValueError( 'test' ) )
    assert isinstance( value, module.Result )
    assert isinstance( error, module.Result )


def test_190_value_chaining( ):
    ''' Value results can be chained through multiple transforms. '''
    value = module.Value( 10 )
    result = value.transform( lambda x: x + 5 ).transform( lambda x: x * 2 )
    assert result.extract( ) == 30


def test_200_error_chaining( ):
    ''' Error results remain errors through multiple transforms. '''
    error = ValueError( 'test' )
    result = module.Error( error )
    chained = result.transform( lambda x: x + 5 ).transform( lambda x: x * 2 )
    assert chained.is_error( )
    assert chained.error is error


def test_210_different_value_types( ):
    ''' Value results work with different value types. '''
    string_value = module.Value( 'hello' )
    list_value = module.Value( [ 1, 2, 3 ] )
    dict_value = module.Value( { 'key': 'value' } )
    assert string_value.extract( ) == 'hello'
    assert list_value.extract( ) == [ 1, 2, 3 ]
    assert dict_value.extract( ) == { 'key': 'value' }


def test_220_different_error_types( ):
    ''' Error results work with different error types. '''
    value_error = module.Error( ValueError( 'value error' ) )
    type_error = module.Error( TypeError( 'type error' ) )
    runtime_error = module.Error( RuntimeError( 'runtime error' ) )
    with pytest.raises( ValueError ):
        value_error.extract( )
    with pytest.raises( TypeError ):
        type_error.extract( )
    with pytest.raises( RuntimeError ):
        runtime_error.extract( )


def test_230_transform_type_conversion( ):
    ''' Transform can convert between types. '''
    value = module.Value( 42 )
    string_result = value.transform( str )
    assert string_result.extract( ) == '42'
    assert isinstance( string_result.extract( ), str )


def test_240_transform_complex_function( ):
    ''' Transform works with complex functions. '''
    value = module.Value( [ 1, 2, 3, 4, 5 ] )
    result = value.transform( lambda lst: [ x for x in lst if x % 2 == 0 ] )
    assert result.extract( ) == [ 2, 4 ]


def test_250_generic_result_type_alias( ):
    ''' GenericResult type alias exists. '''
    assert hasattr( module, 'GenericResult' )
    # Type alias should be available for type hints


def test_260_is_error_function_with_error( ):
    ''' Type guard function correctly identifies Error instances. '''
    error = ValueError( 'test error' )
    result = module.Error( error )
    assert module.is_error( result )


def test_270_is_error_function_with_value( ):
    ''' Type guard function correctly identifies values as not errors. '''
    result = module.Value( 42 )
    assert not module.is_error( result )


def test_280_is_value_function_with_value( ):
    ''' Type guard function correctly identifies Value instances. '''
    result = module.Value( 'test' )
    assert module.is_value( result )


def test_290_is_value_function_with_error( ):
    ''' Type guard function correctly identifies errors as not values. '''
    error = RuntimeError( 'test error' )
    result = module.Error( error )
    assert not module.is_value( result )


def test_300_type_guards_with_different_types( ):
    ''' Type guard functions work with various generic types. '''
    string_value = module.Value( 'hello' )
    int_error = module.Error( ValueError( 'int error' ) )
    list_value = module.Value( [ 1, 2, 3 ] )

    assert module.is_value( string_value )
    assert not module.is_error( string_value )
    assert module.is_error( int_error )
    assert not module.is_value( int_error )
    assert module.is_value( list_value )
    assert not module.is_error( list_value )
