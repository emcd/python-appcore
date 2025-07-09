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


''' Exception hierarchy and error handling tests. '''



from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.exceptions"
module = cache_import_module( MODULE_QNAME )


def test_100_omniexception_hierarchy( ):
    ''' Omniexception inherits from BaseException. '''
    exception = module.Omniexception( )
    assert isinstance( exception, BaseException )
    assert not isinstance( exception, Exception )


def test_110_omnierror_hierarchy( ):
    ''' Omnierror inherits from both Omniexception and Exception. '''
    error = module.Omnierror( )
    assert isinstance( error, module.Omniexception )
    assert isinstance( error, Exception )
    assert isinstance( error, BaseException )


def test_120_address_locate_failure_hierarchy( ):
    ''' AddressLocateFailure has appropriate bases. '''
    error = module.AddressLocateFailure( 'test', [ 'a', 'b' ], 'b' )
    assert isinstance( error, module.Omnierror )
    assert isinstance( error, LookupError )


def test_130_async_assertion_failure_hierarchy( ):
    ''' AsyncAssertionFailure has appropriate bases. '''
    error = module.AsyncAssertionFailure( 'not_awaitable' )
    assert isinstance( error, module.Omnierror )
    assert isinstance( error, AssertionError )
    assert isinstance( error, TypeError )


def test_140_entry_assertion_failure_hierarchy( ):
    ''' EntryAssertionFailure has appropriate bases. '''
    error = module.EntryAssertionFailure( 'test dict', 'missing_key' )
    assert isinstance( error, module.Omnierror )
    assert isinstance( error, AssertionError )
    assert isinstance( error, KeyError )


def test_150_file_locate_failure_hierarchy( ):
    ''' FileLocateFailure has appropriate bases. '''
    error = module.FileLocateFailure( 'test', 'missing.txt' )
    assert isinstance( error, module.Omnierror )
    assert isinstance( error, FileNotFoundError )


def test_160_operation_invalidity_hierarchy( ):
    ''' OperationInvalidity has appropriate bases. '''
    error = module.OperationInvalidity( 'test object', 'invalid_op' )
    assert isinstance( error, module.Omnierror )
    assert isinstance( error, RuntimeError )


def test_200_address_locate_failure_message( ):
    ''' AddressLocateFailure formats error message correctly. '''
    error = module.AddressLocateFailure(
        'configuration', [ 'app', 'database' ], 'database' )
    expected = (
        "Could not locate part 'database' of address '['app', 'database']' "
        "in configuration." )
    assert str( error ) == expected


def test_210_async_assertion_failure_message( ):
    ''' AsyncAssertionFailure formats error message correctly. '''
    error = module.AsyncAssertionFailure( 'not_awaitable' )
    expected = "Entity must be awaitable: 'not_awaitable'"
    assert str( error ) == expected


def test_220_entry_assertion_failure_message( ):
    ''' EntryAssertionFailure formats error message correctly. '''
    error = module.EntryAssertionFailure( 'configuration', 'missing_key' )
    message = str( error )
    assert "Could not find entry 'missing_key' in configuration." in message


def test_230_file_locate_failure_message( ):
    ''' FileLocateFailure formats error message correctly. '''
    error = module.FileLocateFailure( 'distribution', 'config.toml' )
    expected = "Could not locate file 'config.toml' for distribution."
    assert str( error ) == expected


def test_240_operation_invalidity_message( ):
    ''' OperationInvalidity formats error message correctly. '''
    error = module.OperationInvalidity( 'database connection', 'commit' )
    expected = "Could not perform operation 'commit' on database connection."
    assert str( error ) == expected


def test_300_all_errors_catchable_by_omnierror( ):
    ''' All package errors are catchable by Omnierror. '''
    errors = [
        module.AddressLocateFailure( 'test', [ 'a' ], 'a' ),
        module.AsyncAssertionFailure( 'test' ),
        module.EntryAssertionFailure( 'test', 'key' ),
        module.FileLocateFailure( 'test', 'file' ),
        module.OperationInvalidity( 'test', 'op' ),
    ]
    for error in errors:
        assert isinstance( error, module.Omnierror )


def test_310_omniexception_not_catchable_by_exception( ):
    ''' Omniexception is not catchable by Exception. '''
    exception = module.Omniexception( )
    assert not isinstance( exception, Exception )
    # This means bare Omniexception would not be caught by `except Exception:`
    # which is intentional design for critical errors


def test_320_error_instantiation_without_arguments( ):
    ''' Base exceptions can be instantiated without arguments. '''
    omniexception = module.Omniexception( )
    omnierror = module.Omnierror( )
    assert isinstance( omniexception, module.Omniexception )
    assert isinstance( omnierror, module.Omnierror )


def test_330_error_instantiation_with_custom_message( ):
    ''' Base exceptions accept custom messages. '''
    custom_message = 'Custom error message'
    omniexception = module.Omniexception( custom_message )
    omnierror = module.Omnierror( custom_message )
    assert str( omniexception ) == custom_message
    assert str( omnierror ) == custom_message
