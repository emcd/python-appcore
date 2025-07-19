.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Release Notes
*******************************************************************************

.. towncrier release notes start

Appcore 1.3 (2025-07-19)
========================

Enhancements
------------

- Support logfile paths, in addition to log streams, for logger preparation. A
  ``TargetDescriptor`` includes a location, an optional open mode (append or
  truncate; ``truncate`` by default), and an optional codec (``utf-8``, by
  default).


Appcore 1.2 (2025-07-15)
========================

Enhancements
------------

- Application: Require name if constructing application information object
  directly. During preparation, construct absent application information object
  using the distribution name as the application name.


Appcore 1.1 (2025-07-13)
========================

Enhancements
------------

- Documentation: Cover all modules in the public API. (Forgot to do this during
  initial release.)


Repairs
-------

- Distribution: Improve package detection to properly handle namespace packages and installed packages using `__name__` attribute and sys.modules boundary detection instead of ineffective `__module__` checking.


Appcore 1.0.2 (2025-07-10)
==========================

Repairs
-------

- Distribution: Do not skip packages in Python site packages directories when
  detecting the caller.


Appcore 1.0.1 (2025-07-10)
==========================

Repairs
-------

- Fix configuration system to gracefully handle missing templates by returning empty dictionary instead of crashing.
- Fix distribution detection to auto-detect calling package instead of incorrectly using appcore package location for configuration files.


Appcore 1.0 (2025-07-09)
========================

No significant changes.
