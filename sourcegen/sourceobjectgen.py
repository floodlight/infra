#!/usr/bin/python
#################################################################
#
#        Copyright 2013, Big Switch Networks, Inc.
#
# Licensed under the Eclipse Public License, Version 1.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#        http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the
# License.
#
#################################################################
#
# SourceObjectGenerator.py
#
# Base class for object generation (any language)
#
#################################################################
import util
import sys
import cm
import re

class SourceObjectGenerator:
    """ Subclass Object Generator """

    # Every object has a class-type for autogeneration
    objectType = None

    # Every object has access to the object factory that
    # Created it, if present
    objectFactory = None

    basename = None

    def __init__(self, **kwargs):

        # Everyone has a name
        self.name = None
        self.prefix = None

        # Default construction - static initialization only
        self.Construct()
        # Update ourselves based on arguments
        self.Update(kwargs)

        if self.name is None and self.basename:
            self.name = self.basename
            if self.prefix:
                self.name = self.prefix + "_" + self.name

        if 'cm' in kwargs and 'name' in kwargs:
            # Initialize from config manager
            self.InitFromConfig(kwargs['name'], kwargs['cm'])

        if kwargs.get('init', True):
            self.Init()



    def Update(self, d):
        if 'initargs' in d:
            ia = d.pop('initargs')
            self.__dict__.update(ia)
        self.__dict__.update(d)

    def Construct(self):
        return True

    def Init(self):
        return True

    def DefaultName(self):
        return None

    def DefaultData(self):
        return None


    def InitFromConfig(self, name, cm):
        """Initialize ourselves from the config manager data"""


        if name != None and name != '':
            if cm != None and self.objectType != None:
                # We have a name, a type, and config manager.
                # Try to lookup our data
                data = cm.FindTypedEntry(self.objectType, self.name)

                if data != None:
                    # We found data in the config manager for this object.
                    # Allow it to be normalized as per the object's requirements
                    data = self.NormalizeData(data)
                    # Update the object with the new data
                    self.Update(data)
                    return True
                else:
                    # 'name' was specified, but no data was found
                    return False
        return True


    def NormalizeData(self, data):
        """ Normalize our user-defined data definition to the
        object-cannonical format. Allows the user to specify a variety
        of syntax or shorthand, but produce a unified representation for
        processing in the object. This method should just return the
        new representation, not adjust any class member data.
        This method is optional. """
        return data



import cm
import sys
import imp
import os

class SourceObjectFactory:
    """Creates a SourceObjectGenerator"""

    objectLanguage = None

    def __init__(self, configManager=None, LoadLocal=True):
        self.objectReList = [
            # class(name)
            re.compile(r'(?P<cls>.*)\((?P<name>.*)'),
            # class.name
            re.compile(r'(?P<cls>.*?)\.(?P<name>.*)')
            ]
        self.methodReList = [
            # class(name).method
            re.compile(r'(?P<cls>.*)\((?P<name>.*)\).(?P<method>.*)'),
            # class.name.method
            re.compile(r'(?P<cls>.*)\.(?P<name>.*)\.(?P<method>.*)'),
            ]

        self.modules = []
        self.classes = {}
        self.objectTypes = {}
        self.cm = configManager

        if LoadLocal:
            # Load all modules in our local directory
            self.ImportModules(
                os.path.dirname(
                    os.path.abspath(sys.modules[__name__].__file__)))


    def __isSourceObjectModule(self, dir_, fName):
        base, ext = os.path.splitext(fName)
        if ext == ".sopy":
            # Assume true
            return base
        if ext == ".py":
            # check for SourceObject tag

            try:
                for line in open("%s/%s" % (dir_, fName)):
                    if re.match("## SourceObject ##", line):
                        return base
            except:
                pass

            return False

    def ImportModules(self, dir_):
        """Import all modules in a given directory """
        sys.path.append(dir_)
        for f in os.listdir(os.path.abspath(dir_)):
            m = self.__isSourceObjectModule(dir_, f)
            if m:
                self.ImportModule(m)

    def ImportModule(self, mod):
        """Import a module name """
        self.modules.append(__import__(mod))
        m = self.modules[-1]
        for obj in dir(m):
            try:
                __cls = getattr(m, obj)
                if issubclass(__cls, SourceObjectGenerator):
                    # Generator objects must have a valid objectType
                    ot = getattr(__cls, 'objectType')
                    if ot is not None:
                        self.classes[obj] = __cls
                        self.objectTypes[ot] = obj

            except TypeError, e:
                pass


    def ListClasses(self):
        for clsname, cls in self.classes.iteritems():
            print "%s:%s (type=%s)" % (clsname, cls, cls.objectType)


    def CreateObjectList(self, cls, name=None, data=None):
        objectClass = None
        objectList = []

        if cls in self.classes:
            # Requested by name
            objectClass = cls
        if cls in self.objectTypes:
            objectClass = self.objectTypes[cls]

        if objectClass != None:

            if name != None and name != '':
                # Get the list of specific object names to which
                # the requested name may refer:
                nameList = self.cm.ObjectNameList(
                    self.classes[objectClass].objectType,
                    name)

                # if nameList is empty, we couldn't resolve the symbol
                if len(nameList) == 0:
                    raise Exception('No entry found for %s::%s' %
                                    (cls, name))

                # Create all named objects
                for name in nameList:
                    obj = self.classes[objectClass](name=name, cm=self.cm)
                    obj.objectFactory = self
                    objectList.append(obj)

            else:
                # Name is empty
                obj = self.classes[objectClass](name=None)
                obj.objectFactory = self
                objectList.append(obj)

            return objectList

        raise Exception("Could not create object type '%s'" % cls)


    def __callObjectMethod(self, obj, method, raise_=True):
        #
        # Syntactic sugar
        # case-insensitive search for the method name
        #
        mName = method.lower()
        for name in dir(obj):
            if name.lower() == mName:
                return getattr(obj, name)()

        if raise_:
            raise Exception("object %s (type %s) has no method '%s'." %
                            (obj.__class__, obj.objectType, method))

        return None


    def EvalList(self, expr):

        for r in self.methodReList:
            x = r.match(expr)
            if x:
                # Method invocation. Get the matching objects
                objList = self.CreateObjectList(x.group('cls'),
                                                x.group('name'))
                resultList = []
                for obj in objList:
                    resultList.append(self.__callObjectMethod(obj,
                                                              x.group('method'),
                                                              True))
                return resultList

        for r in self.objectReList:
            x = r.match(expr)
            if x:
                return self.CreateObjectList(x.group('cls'), x.group('name'))

        raise Exception("Could not eval '%s'" % expr)

    def Eval(self, expr):
        return "\n".join(self.EvalList(expr))



if __name__ == "__main__":
    sof = SourceObjectFactory()




