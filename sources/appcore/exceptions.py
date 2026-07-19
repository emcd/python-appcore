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


''' Family of exceptions for package API.

    This module defines a comprehensive exception hierarchy for the appcore
    library, providing specific exception types for different failure modes
    while maintaining a consistent interface for error handling and debugging.

    Exception Hierarchy
    ===================

    The exception hierarchy follows a two-tier design:

    * :class:`Omniexception` - Base for all package exceptions
    * :class:`Omnierror` - Base for error exceptions, inherits from both
      ``Omniexception`` and ``Exception``

    Usage
    =====

    Catch all package errors with :class:`Omnierror` or with built-in exception
    types. See class inheritance for details.
'''


from . import __


class Omniexception( __.immut.exceptions.Omniexception ):
    ''' Base for all exceptions raised by package API. '''

    def render_dictionary( self ) -> dict[ str, __.typx.Any ]:
        ''' Returns dictionary representation of exception. '''
        return render_dictionary( self )

    def render_json( self, compact: bool = False, indent: int = 2 ) -> str:
        ''' Renders exception as JSON into string. '''
        dictionary = self.render_dictionary( )
        from json import dumps
        if compact:
            return dumps(
                dictionary, ensure_ascii = False, separators = ( ',', ':' ) )
        return dumps( dictionary, ensure_ascii = False, indent = indent )

    def render_markdown( self ) -> tuple[ str, ... ]:
        # TODO: Properly handle exception groups.
        # TODO: Optionally handle tracebacks.
        ''' Renders exception as Markdown into sequence of lines. '''
        dictionary = self.render_dictionary( )
        summary = "[**{fqclass}**] {message}".format(
            fqclass = dictionary[ 'fqclass' ],
            message = dictionary[ 'message' ] )
        return ( summary, )

    def render_toml( self ) -> str:
        ''' Renders exception as TOML into string. '''
        from tomli_w import dumps
        return dumps( self.render_dictionary( ) )


def render_dictionary( exception: BaseException ) -> dict[ str, __.typx.Any ]:
    # TODO? Handle via third-party library.
    # TODO: Properly handle exception groups.
    # TODO: Optionally handle tracebacks.
    ''' Returns dictionary representation of exception. '''
    class_ = type( exception )
    return {
        'class': class_.__name__,
        'fqclass': f"{class_.__module__}.{class_.__qualname__}",
        'message': str( exception ), }


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


class AddressLocateFailure( Omnierror, LookupError ):
    ''' Failure to locate address. '''

    def __init__(
        self, subject: str, address: __.cabc.Sequence[ str ], part: str
    ):
        super( ).__init__(
            f"Could not locate part '{part}' of address '{address}' "
            f"in {subject}." )


class AsyncAssertionFailure( Omnierror, AssertionError, TypeError ):
    ''' Assertion of awaitability of entity failed. '''

    def __init__( self, entity: __.typx.Any ):
        super( ).__init__( f"Entity must be awaitable: {entity!r}" )


class ContextInvalidity( Omnierror, TypeError, ValueError ):

    def __init__( self, auxdata: __.typx.Any ):
        # TODO: Add module name to fully-qualified name.
        fqname = type( auxdata ).__qualname__
        super( ).__init__( f"Invalid context object type: {fqname}" )


class DependencyAbsence( Omnierror, ImportError ):

    def __init__( self, dependency: str, feature: str ):
        super( ).__init__(
            f"Optional dependency {dependency!r} missing "
            f"feature {feature!r}." )


class EntryAssertionFailure( Omnierror, AssertionError, KeyError ):
    ''' Assertion of entry in dictionary failed. '''

    def __init__( self, subject: str, name: str ):
        super( ).__init__( f"Could not find entry '{name}' in {subject}." )


class FileLocateFailure( Omnierror, FileNotFoundError ):
    ''' Failure to locate file. '''

    def __init__( self, subject: str, name: str ):
        super( ).__init__(
            f"Could not locate file '{name}' for {subject}." )


class OperationInvalidity( Omnierror, RuntimeError ):
    ''' Invalid operation. '''

    def __init__( self, subject: str, name: str ):
        super( ).__init__(
            f"Could not perform operation '{name}' on {subject}." )
