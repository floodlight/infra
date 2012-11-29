#!/usr/bin/python
## SourceObject ##
###############################################################################
#
# CEnumGenerator.py
#
# Enum-specific C code generation objects
#
###############################################################################
from cobjectgen import *
from cfunctiongen import *
from cmacrogen import *
from cstructgen import *
import sys
import util


class CEnumFindByValueHelper(CFunctionGenerator):

    def Init(self):
        self.rv = self.mapstruct.TypedefName() + '*'
        self.args = [ [ 'int', 'e' ], 
                      [ self.rv, 'map' ], 
                      [ 'int', 'size' ] ]

        self.body = """    int i;
    for(i = 0; i < size-1; i++) {
        if(map[i].%s == e) {
            return map+i;
         }
    }
    return NULL;""" % self.mapstruct.valueMember

class CEnumFindByNameHelper(CFunctionGenerator):
    
    def Init(self):
        self.rv = self.mapstruct.TypedefName() + '*'
        self.args = [ [ 'const char*', 'str' ], 
                      [ self.rv, 'map' ], 
                      [ 'int', 'size' ], 
                      [ 'int', 'subsearch']
                      ]
        
        self.body = """    int i;
    for(i = 0; i < size-1; i++) {
        if(!%s(str, map[i].%s)) {
            return map+i;
        }
    }
    /* No exact match */
    if(subsearch) {
        /* Substring search */
        for(i = 0; i < size-1; i++) {
            if(%s(map[i].%s, str)) {
                return map+i;
            }
        }
    }
    return NULL;""" % (self.f.GlobalStringCompare(), 
                       self.mapstruct.nameMember, 
                       self.f.GlobalSubstring(), 
                       self.mapstruct.nameMember)
                       


class CEnumUtilities(CObjectGenerator):
    objectType = 'enumutil'

    def Construct(self):
        self.mapstructName = 'aim_map_si'
        self.findByValueName = 'aim_map_si_i'
        self.findByNameName = 'aim_map_si_s'
        
    def Init(self):
        self.mapstruct = CStructIntMap(name=self.mapstructName, 
                                       comment="/** enum map */\n")
        self.findByValueHelper = CEnumFindByValueHelper(
            name=self.findByValueName, 
            mapstruct=self.mapstruct, 
            static=True)
        self.findByNameHelper = CEnumFindByNameHelper(
            name=self.findByNameName, 
            mapstruct=self.mapstruct, 
            static=True)

    def Header(self):
        s = ""
        s += self.mapstruct.Define()
        s += self.findByValueHelper.Prototype()
        s += self.findByNameHelper.Prototype()
        return s

    def Source(self):
        s = ""
        s += self.findByValueHelper.Define()
        s += self.findByNameHelper.Define()
        return s

    def All(self):
        s = ""
        s += self.Header()
        s += self.Source()
        return s


class CEnumValidMacro(CMacroGenerator):

    def Init(self):
        self.name = self.enum.name + "_valid"; 
        self.args = [ '_e' ]
        self.comment = "/** validator */\n"; 

    def Body(self):
        
        s = ""
        if self.enum.IsLinear():
            # Linear enums can be checked with a macro expression
            lastMember = self.enum.members[-1][0]
            s += ("    ( (0 <= (_e)) && ((_e) <= %s))" %
                 (self.f.EnumEntry(lastMember, self.enum.name)))
        else:
            # Nonlinear enums must be checked by lookup:
            s += ("    (%s)" %                 
                 (CEnumValidatorFunction(enum=self.enum).Call('(_e)')))
            
        return s


class CEnumValidatorFunction(CFunctionGenerator):
    
    def Init(self):
        self.comments = "/** Enum validator. */\n"; 
        self.rv = 'int'
        self.name = self.f.FunctionName("%sValid" % (self.enum.name))
        self.args = [ [ self.enum.EnumType(), 'e' ] ]
        
        maptable = self.enum.MapTableName();

        self.body = """    return %s ? 1 : 0;""" % (
            self.enum.util.findByValueHelper.Call('NULL', 
                                                  'e',
                                                  maptable, '0'))




class CEnumNameFunction(CFunctionGenerator):
    
    def Init(self):
        self.comments = "/** Enum names. */\n"
        self.rv = 'const char*'
        self.name = self.f.FunctionName("%sName" % (self.enum.name))
        self.args = [ [ self.enum.EnumType(), 'e' ] ]
        
        maptable = self.enum.MapTableName();

        self.body = """    const char* name; 
    if(%s) { 
        return name; 
    }
    else { 
        return "-invalid value for enum type '%s'";
    }""" % (
            self.enum.util.findByValueHelper.Call('&name',
                                                  'e', 
                                                  maptable, '0'), 
            self.enum.name)



class CEnumValueFunction(CFunctionGenerator):
    def Init(self):
        self.comments = "/** Enum values. */\n"
        self.rv = 'int'
        self.name = self.f.FunctionName("%sValue" % (self.enum.name))
        self.args = [ [ 'const char*', 'str' ], 
                      '%s* e' % self.enum.EnumType(), 
                      'int substr', 
                      ]
        
        maptable = self.enum.MapTableName();

        self.body = """    int i; 
    AIM_REFERENCE(substr);
    if(%s) {
        /* Enum Found */
        *e = i; 
        return 0; 
    }
    else {
        return -1; 
    }""" % (
            self.enum.util.findByNameHelper.Call('&i', 
                                                 'str',
                                                 maptable, '0'))



import pprint
import copy

class CEnumGenerator(CObjectGenerator):
    """ C Enum Generator Subclass """

    objectType='enum'

    def Construct(self):
        self.util = CEnumUtilities()
        self.novalue = False; 

    def Init(self):
        self.validatorFunction = CEnumValidatorFunction(enum=self)
        self.enumNameFunction = CEnumNameFunction(enum=self)
        self.enumValueFunction = CEnumValueFunction(enum=self)
        self.enumValidMacro = CEnumValidMacro(enum=self)



    def NormalizeData(self, data):
        """ Normalize Enum Definitions """
        
        # 
        # The member's key can be a list of str or a list of lists, 
        # depending upon whether or not values are specified. 
        # 
        # We convert everything here to a list of lists representation
        # 
        data['members'] = util.listifyElements(data['members']); 
        
        if 'memberfilter' in data:
            data = copy.deepcopy(data); 
            for member in data['members']:
                member[0] = eval(data['memberfilter'])

        return data



    ############################################################
    #
    # Internal helper methods
    #
    ############################################################
    
    def IsLinear(self):
        """ Determine whether or not we are a linear enum """

        # Explicit marking as linear or non-linear is possible:
        if hasattr(self, 'linear'):
            return self.linear

        #
        # If specific values are specified in the enum
        # definition then the mapping is nonlinear. 
        #
        for member in self.members:
            if len(member) > 1:
                # Member has a specific value
                return False

        return True


    def IncludeLast(self):
        """ Determines whether the Last entry is included in this enum"""
        # Last makes no sense for nonlinear enums
        if self.IsLinear() == False:
            Last = False; 
        elif hasattr(self, 'Last'):
            Last = self.Last
        else:
            Last = True

        return Last


    def IncludeCount(self):
        """ Determines whether the Count entry is included in an enum"""
        # Count makes no sense for nonlinear enums
        if self.IsLinear() == False:
            Count = False
        elif hasattr(self, 'Count'):
            Count = self.Count
        else:
            Count = True
        
        return Count



    def IncludeInvalid(self):
        """ Determines whether the Invalid entry is included in an enum"""
        if self.IsLinear() == False:
            return False

        if hasattr(self, 'Invalid'):
            return self.Invalid
        if hasattr(self, 'invalid'):
            return self.invalid

        return True

    def IncludeTypedef(self):
        if hasattr(self, 'typedef'):
            return self.typedef
        else:
            return True


    def EnumType(self):
        """ Returns the type required to declare this enum """
        if self.IncludeTypedef():
            return self.f.TypedefEnumName(self.name)
        else:
            return "enum %s" % (self.f.EnumName(self.name))


    def MapTableName(self):
        return "%s_map" % (self.name)


    def MapTableType(self):
        return self.struct.name


    ############################################################
    #
    # Generation Directives
    #
    # These methods generate code for this enumeration
    #
    ############################################################
    def Define(self):
        """ Generate an Enum Definition """

        #
        # The default behavior is to typedef all enums. 
        # If you don't want a typedef, specify 'typedef:False'
        # in the enum specification
        # 
        s = "/** %s */\n" % (self.name)
        if self.IncludeTypedef():
            s += "typedef "
            
        s += "enum %s {\n" % self.f.EnumName(self.name)
        for member in self.members:
            s += "    %s" % self.f.EnumEntry(member[0], self.name)
            
            if (len(member) > 1) and (self.novalue == False):            
                # Value specified
                if hasattr(self, 'hex'):
                    s += " = 0x%x" % int(member[1])
                else:
                    s += " = %s" % member[1]

            s += ",\n"

        #
        # The default generation includes an automatically generated
        # Invalid, Last, and Count entry for all Linear enums. 
        # 
        # If you don't want any of these, you can specify:
        # 'Invalid':False, 'Count':False, 'Last':False
        # 
        # The default value for Invalid is -1. You can specify
        # 'Invalid': <value> if you want to change it. 
        #

        # Note that 'member' currently contains the last entry
        lastMember = member[0]

        if self.IncludeLast() != False:
            s += "    %s = %s,\n" % (
                self.f.EnumLast(self.name), 
                self.f.EnumEntry(lastMember, self.name))
        
        if self.IncludeCount() != False:
            s += "    %s,\n" % self.f.EnumCount(self.name)
        
        if self.IncludeInvalid() != False:
            value = self.IncludeInvalid()
            if value is True:
                value = -1; 
            s += "    %s = %s,\n" % (self.f.EnumInvalid(self.name), value)

        s += "}"
        
        if self.IncludeTypedef():
            s += " %s" % self.f.TypedefEnumName(self.name)

        s += ";\n"
        return s


    def StringsMacro(self):
        """ Output the STRINGS macro """

        # The String Macro can only generated for Linear enums
        if self.IsLinear() == False:
            raise Exception('Cannot generate a STRINGS macro for'
                            ' nonlinear enum %s' % (self.name))


        s = "/** Strings macro. */\n"
        s += "#define %s_STRINGS \\\n" % self.f.InMacro(self.name)
        s += "{\\\n"

        for member in self.members:
            s += "    \"%s\", \\\n" % member[0]

        s += "}\n"
        return s


 

    def MapTable(self, static=False):
        """ Output the enum map table """
        s = ""
        if static:
            s += self.f.Static() + " "

        s += self.util.mapstruct.DefineTable(self.MapTableName())
        s += "{\n"; 

        for member in self.members:
            s += """    { "%s", %s },\n""" % (
                member[0], 
                self.f.EnumEntry(member[0], self.name))
        s += "    { NULL, 0 }\n"    
        s += "};\n"
        return s


    def EnumProtos(self):
        s = ""
        s += self.enumNameFunction.Prototype() + "\n"
        s += self.enumValueFunction.Prototype() + "\n"
        if not self.IsLinear():
            s += self.validatorFunction.Prototype() + "\n"
        s += self.enumValidMacro.Define() + "\n"

        return s

    def Header(self):
        s = ""
        s += self.Define() + "\n"

        if self.IsLinear():
            s += self.StringsMacro()

        s += self.EnumProtos()

        return s; 

    def Source(self):
        s = ""
        s += self.MapTable() + "\n"
        s += self.enumNameFunction.Define() + "\n"
        s += self.enumValueFunction.Define() + "\n"
        if not self.IsLinear():
            s += self.validatorFunction.Define() + "\n"
            
        return s

        for member in self.members:
            s += "    \"%s\", \\\n" % member[0]

    def __getitem__(self, item):
        for m in self.members:
            if m[0] == item:
                return self.f.EnumEntry(m[0], self.name)
        raise Exception("No enum entry named %s" % item)

        
###############################################################################
#
# Enum Unit testing
#
###############################################################################
if __name__ == "__main__":

    e = CEnumGenerator(name="testEnum", members=[ ['member1'], ['member2'], 
                                                  ['member3']])

    print e.Define()

    
    

