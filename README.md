Common Infrastructure Repository
================================

This repository contains the common development, build system, and runtime components used by other Floodlight projects. 


The Builder
-----------
The build system can be found in builder/unix. 



The Source Generator
--------------------
A custom C source code generator is available in the sourcegen directory. 

The sourcegen module is used by all C module libraries to produce and manage common data infrastructures for enumerations, configuration definitions, xmacros, and other constructs. 


The AIM Module
--------------
The AIM module provides a common runtime environment for all code modules and systems built from them. It includes a variety of system features for virtualizing IO, custom datatypes, and common primitives. 

