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


''' Dictionary editing and nested configuration tests. '''


import pytest

from . import PACKAGE_NAME, cache_import_module


MODULE_QNAME = f"{PACKAGE_NAME}.dictedits"
module = cache_import_module( MODULE_QNAME )

exceptions_module = cache_import_module( f"{PACKAGE_NAME}.exceptions" )


def test_100_simple_edit_creation( ):
    ''' Dictionary editor creates with address and value. '''
    edit = module.SimpleEdit( address = [ 'app', 'name' ], value = 'test-app' )
    assert edit.address == [ 'app', 'name' ]
    assert edit.value == 'test-app'


def test_110_simple_edit_inject_new_key( ):
    ''' Dictionary editor injects value at new address. '''
    config = { }
    edit = module.SimpleEdit( address = [ 'app', 'name' ], value = 'test-app' )
    edit( config )
    assert config == { 'app': { 'name': 'test-app' } }


def test_120_simple_edit_replace_existing( ):
    ''' Dictionary editor replaces existing value at address. '''
    config = { 'app': { 'name': 'old-app', 'version': '1.0' } }
    edit = module.SimpleEdit( address = [ 'app', 'name' ], value = 'new-app' )
    edit( config )
    assert config[ 'app' ][ 'name' ] == 'new-app'
    assert config[ 'app' ][ 'version' ] == '1.0'  # Unchanged


def test_130_simple_edit_deep_nesting( ):
    ''' Dictionary editor creates deep nested structure. '''
    config = { }
    edit = module.SimpleEdit(
        address = [ 'app', 'database', 'connection', 'host' ],
        value = 'localhost'
    )
    edit( config )
    expected = {
        'app': { 'database': { 'connection': { 'host': 'localhost' } } } }
    assert config == expected


def test_140_edit_dereference_existing( ):
    ''' Edit dereference returns value at address. '''
    config = { 'app': { 'name': 'test-app', 'version': '1.0' } }
    edit = module.SimpleEdit( address = [ 'app', 'name' ], value = 'ignored' )
    value = edit.dereference( config )
    assert value == 'test-app'


def test_150_edit_dereference_missing_key( ):
    ''' Edit dereference raises AddressLocateFailure for missing key. '''
    config = { 'app': { 'name': 'test-app' } }
    edit = module.SimpleEdit(
        address = [ 'app', 'missing' ], value = 'ignored' )
    with pytest.raises( exceptions_module.AddressLocateFailure ) as exc_info:
        edit.dereference( config )
    assert 'missing' in str( exc_info.value )
    assert 'configuration dictionary' in str( exc_info.value )


def test_160_edit_dereference_partial_path( ):
    ''' Edit dereference raises AddressLocateFailure for missing path. '''
    config = { 'app': { 'name': 'test-app' } }
    edit = module.SimpleEdit(
        address = [ 'app', 'database', 'host' ], value = 'ignored' )
    with pytest.raises( exceptions_module.AddressLocateFailure ) as exc_info:
        edit.dereference( config )
    assert 'database' in str( exc_info.value )


def test_170_elements_entry_edit_creation( ):
    ''' ElementsEntryEdit creates with address and editee. '''
    edit = module.ElementsEntryEdit(
        address = [ 'servers' ],
        editee = ( 'enabled', True )
    )
    assert edit.address == [ 'servers' ]
    assert edit.editee == ( 'enabled', True )
    assert edit.identifier is None


def test_180_elements_entry_edit_all_elements( ):
    ''' ElementsEntryEdit applies edit to all elements in array. '''
    config = {
        'servers': [
            { 'name': 'server1', 'enabled': False },
            { 'name': 'server2', 'enabled': False },
            { 'name': 'server3', 'enabled': False }
        ]
    }
    edit = module.ElementsEntryEdit(
        address = [ 'servers' ],
        editee = ( 'enabled', True )
    )
    edit( config )
    for server in config[ 'servers' ]:
        assert server[ 'enabled' ] is True


def test_190_elements_entry_edit_with_identifier( ):
    ''' ElementsEntryEdit applies edit only to matching elements. '''
    config = {
        'servers': [
            { 'name': 'web-server', 'type': 'web', 'enabled': False },
            { 'name': 'db-server', 'type': 'database', 'enabled': False },
            { 'name': 'cache-server', 'type': 'web', 'enabled': False }
        ]
    }
    edit = module.ElementsEntryEdit(
        address = [ 'servers' ],
        editee = ( 'enabled', True ),
        identifier = ( 'type', 'web' )
    )
    edit( config )
    # Only web servers should be enabled
    assert config[ 'servers' ][ 0 ][ 'enabled' ] is True   # web-server
    assert config[ 'servers' ][ 1 ][ 'enabled' ] is False  # db-server
    assert config[ 'servers' ][ 2 ][ 'enabled' ] is True   # cache-server


def test_200_elements_entry_edit_missing_identifier( ):
    ''' Elements entry editor raises EntryAssertionFailure for missing key. '''
    config = {
        'servers': [
            { 'name': 'server1' },  # Missing 'type' key
            { 'name': 'server2', 'type': 'web' }
        ]
    }
    edit = module.ElementsEntryEdit(
        address = [ 'servers' ],
        editee = ( 'enabled', True ),
        identifier = ( 'type', 'web' )
    )
    with pytest.raises( exceptions_module.EntryAssertionFailure ) as exc_info:
        edit( config )
    assert 'type' in str( exc_info.value )
    assert 'configuration array element' in str( exc_info.value )


def test_210_elements_entry_edit_preserves_other_fields( ):
    ''' Elements entry editor preserves other fields during edits. '''
    config = {
        'users': [
            {
                'name': 'alice', 'role': 'admin', 'active': False,
                'created': '2023-01-01'
            },
            {
                'name': 'bob', 'role': 'user', 'active': False,
                'created': '2023-01-02'
            }
        ]
    }
    edit = module.ElementsEntryEdit(
        address = [ 'users' ],
        editee = ( 'active', True ),
        identifier = ( 'role', 'admin' )
    )
    edit( config )
    # Alice should be activated, other fields preserved
    alice = config[ 'users' ][ 0 ]
    assert alice[ 'active' ] is True
    assert alice[ 'name' ] == 'alice'
    assert alice[ 'role' ] == 'admin'
    assert alice[ 'created' ] == '2023-01-01'
    # Bob should be unchanged
    bob = config[ 'users' ][ 1 ]
    assert bob[ 'active' ] is False


def test_220_edit_chain_application( ):
    ''' Multiple edits can be applied in sequence. '''
    config = { }
    edits = [
        module.SimpleEdit( address = [ 'app', 'name' ], value = 'test-app' ),
        module.SimpleEdit( address = [ 'app', 'version' ], value = '1.0' ),
        module.SimpleEdit(
            address = [ 'database', 'host' ], value = 'localhost' )
    ]
    for edit in edits:
        edit( config )
    expected = {
        'app': { 'name': 'test-app', 'version': '1.0' },
        'database': { 'host': 'localhost' }
    }
    assert config == expected


def test_230_edit_protocol_compliance( ):
    ''' Edit types implement the Edit protocol. '''
    simple_edit = module.SimpleEdit( address = [ 'test' ], value = 'value' )
    elements_edit = module.ElementsEntryEdit(
        address = [ 'items' ],
        editee = ( 'status', 'active' )
    )
    # Protocol compliance check
    assert isinstance( simple_edit, module.Edit )
    assert isinstance( elements_edit, module.Edit )
    assert callable( simple_edit )
    assert callable( elements_edit )


def test_240_edit_with_complex_values( ):
    ''' Edits work with complex value types. '''
    config = { }
    complex_value = {
        'database': { 'host': 'localhost', 'port': 5432 },
        'redis': { 'host': 'localhost', 'port': 6379 },
        'features': [ 'auth', 'cache', 'logging' ]
    }
    edit = module.SimpleEdit( address = [ 'services' ], value = complex_value )
    edit( config )
    assert config[ 'services' ] == complex_value


def test_250_dereference_with_different_types( ):
    ''' Edit dereference works with different nested value types. '''
    config = {
        'string_value': 'test',
        'number_value': 42,
        'list_value': [ 1, 2, 3 ],
        'dict_value': { 'nested': 'value' }
    }
    for key, expected in config.items( ):
        edit = module.SimpleEdit( address = [ key ], value = 'ignored' )
        assert edit.dereference( config ) == expected


def test_260_edits_type_alias( ):
    ''' Edits type alias is available. '''
    assert hasattr( module, 'Edits' )
    # Type alias should be usable for type hints