# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 13:11:38 2012

@author: proto
"""

from pyparsing import Word, Suppress,Optional,alphanums,Group
from numpy import zeros,nonzero
import numpy as np
import json
import itertools
'''
This file in general classifies rules according to the information contained in
the json config file for classyfying rules according to their reactants/products
'''

class SBMLAnalyzer:
    
    def __init__(self,configurationFile):
        self.configurationFile = configurationFile
        
    def parseReactions(self,reaction):
        species =  (Word(alphanums+"_") 
        + Suppress('()')) + Optional(Suppress('+') + Word(alphanums+"_") 
        + Suppress("()")) + Optional(Suppress('+') + Word(alphanums+"_") 
        + Suppress("()")) + Optional(Suppress('+') + Word(alphanums+"_") 
        + Suppress("()"))
        rate = Word(alphanums + "()")
        grammar = (Group(species) + Suppress(Optional("<") + "->") + Group(species) + Suppress(rate)) \
        ^ (species + Suppress("->") + Suppress(rate))  
        result =  grammar.parseString(reaction).asList()
        if len(result) < 2:    
            result = [result,[]] 
        return result
    
    
    
    def loadConfigFiles(self,fileName):
        '''
        the reactionDefinition file must contain the definitions of the basic reaction types 
        we wnat to parse and what are the requirements of a given reaction type to be considered
        as such
        '''
        with open(fileName,'r') as fp:
            reactionDefinition = json.load(fp)
        return reactionDefinition
    
    def identifyReactions2(self,rule,reactionDefinition):
        '''
        This method goes through the list of common reactions listed in ruleDictionary
        and tries to find how are they related according to the information in reactionDefinition
        '''  
        #print reactionDefinition
        result = []
        for idx,element in enumerate(reactionDefinition['reactions']):
            if(len(rule[0]) == len(element[0]) and len(rule[1]) == len(element[1])):
                result.append(1)           
    #            for (el1,el2) in (element[0],rule[0]):
    #                if element[0].count(el1) == element[]
            else:
                result.append(0)
        return result
    
      
        
    def species2Rules(self,rules):
        '''
        This method goes through the rule list and classifies species tuples in a dictionary
        according to the reactions they appear in.
        '''
        ruleDictionary = {}
        for rule in rules:
            reaction2 = rule #list(parseReactions(rule))
            #print reaction2
            totalElements =  [item for sublist in reaction2 for item in sublist]
            if tuple(totalElements) in ruleDictionary:
                ruleDictionary[tuple(totalElements)].append(rules.index(rule))
            else:
                ruleDictionary[tuple(totalElements)] = [rules.index(rule)]
        return ruleDictionary
    
    def checkCompliance(self,ruleCompliance,tupleCompliance,ruleBook):
        '''
        This method is mainly useful when a single rule can be possibly classified
        in different ways, but in the context of its tuple partners it can only be classified
        as one
        '''
        
        ruleResult = np.zeros(len(ruleBook))
        for validTupleIndex in np.nonzero(tupleCompliance):
            for index in validTupleIndex:
                if 'r' in ruleBook[index] and np.any([ruleCompliance[temp] for temp in ruleBook[index]['r']]):
                    ruleResult[index] = 1
                #check if just this is enough
                if 'n' in ruleBook[index]:
                    ruleResult[index] = 1
        return ruleResult
            
     
    def analyzeNamingConventions(self,molecules,originalPattern='',modifiedPattern=''):
        '''
        *originalPattern* and *modifiedPattern* are regular expressions containing
        the patterns we wish to compare and see if they are the same.
        We will go through the list of molecules and check for names that match those
        patterns
        '''
        #original = originalPattern[0].replace('\\\\', '\\')
        #modified = modifiedPattern[0].replace('\\\\', '\\')
        #pOriginal = re.compile(original)
        #pModified = re.compile(modified)
        #oMolecules = []
        
        patternType = originalPattern
        pattern = modifiedPattern
        oMolecules = []
        results = []
        comparisonMethod = str.startswith if patternType == 'prefix' else str.endswith
        for molecule in [x.strip('()') for x in molecules]:
            if comparisonMethod(molecule,pattern):
                oMolecules.append(molecule)
        for molecule in [x.strip('()') for x in molecules]:
            if molecule in oMolecules:
                continue
            for superMolecule in oMolecules:
                if patternType == 'prefix':
                    comparison = superMolecule[len(pattern):]
                else:
                    comparison = superMolecule[:len(superMolecule)- len(pattern)]
                if comparison == molecule:
                    results.append((molecule,superMolecule))
                
#        for molecule in molecules:
#            mmatch = pModified.match(molecule)        
#            if mmatch and mmatch.group('key') in oMolecules:
#                results.append((mmatch.group('key'),molecule[0:-2]))
        return results
     
    def processNamingConventions(self,molecules,namingConventions):
        equivalenceTranslator = {}
        for idx,convention in enumerate(namingConventions):
            temp = self.analyzeNamingConventions(molecules,convention[0],convention[1])
            equivalenceTranslator[idx] = temp
        
        #now we want to fill in all intermediate relationships
        
        newTranslator = equivalenceTranslator.copy()
        for (key,key2) in [list(x) for x in itertools.combinations([y for y in equivalenceTranslator],2)]:
            if key == key2:
                continue
            intersection = [[x for x in set.intersection(set(sublist),set(sublist2))] 
                for sublist in equivalenceTranslator[key2] for sublist2 in equivalenceTranslator[key]]
            intersectionPoints = [(int(x/len(equivalenceTranslator[key])),int(x%len(equivalenceTranslator[key]))) for x in 
                range(0,len(intersection)) if len(intersection[x]) > 0]
            for (point) in (intersectionPoints):
                temp = list(equivalenceTranslator[key2][point[0]])
                temp.extend(list(equivalenceTranslator[key][point[1]]))
                temp2 = [x for x in temp if temp.count(x) == 1]
                temp2.sort(key=len)
                #FIXME: THIS IS TOTALLU JUST A HACK. FIX SO THAT THE INDIRECT 
                #RELATIONSHIP IS ASSIGNED CORRECTLY
                if len(temp2) == 2:
                    newTranslator[key2].append(tuple(temp2))
        return newTranslator
    
    def getReactionClassification(self,reactionDefinition,rules,equivalenceTranslator,useNamingConventions=True):
        '''
        *reactionDefinition* is ....
        *rules*
        This method will go through the list of rules and the list of rule definitions
        and tell us which rules it can classify according to the rule definitions list
        provided
        '''
        ruleDictionary = self.species2Rules(rules)
        #contains which rules are equal to reactions defined in reactionDefiniotion['reactions]    
        ruleComplianceMatrix = zeros((len(rules),len(reactionDefinition['reactions'])))
        for (idx,rule) in enumerate(rules):
            reaction2 = rule #list(parseReactions(rule))
            ruleComplianceMatrix[idx] = self.identifyReactions2(reaction2,reactionDefinition)
        #initialize the tupleComplianceMatrix array with the same keys as ruleDictionary
        tupleComplianceMatrix = {key:zeros((len(reactionDefinition['reactions']))) for key in ruleDictionary}
        #check which reaction conditions each tuple satisfies
        for element in ruleDictionary:
            for rule in ruleDictionary[element]:
                tupleComplianceMatrix[element] += ruleComplianceMatrix[rule]     
        #print tupleC
        #now we will check for the nameConventionMatrix
        tupleNameComplianceMatrix = {key:zeros((len(reactionDefinition['namingConvention']))) for key in ruleDictionary}
        for rule in ruleDictionary:
            for namingConvention in equivalenceTranslator:
                for equivalence in equivalenceTranslator[namingConvention]:
                    if all(element in rule for element in equivalence):
                        tupleNameComplianceMatrix[rule][namingConvention] +=1
                        break
        #check if the reaction conditions each tuple satisfies are enough to get classified
        #as an specific named reaction type
        tupleDefinitionMatrix = {key:zeros((len(reactionDefinition['definitions']))) for key in ruleDictionary}
        for key,element in tupleComplianceMatrix.items():
            for idx,member in enumerate(reactionDefinition['definitions']):
                #tupleDefinitionMatrix[key][idx] = True
                if 'r' in member:            
                    tupleDefinitionMatrix[key][idx] = np.all([element[reaction] for reaction in member[u'r']])
                if 'n' in member:
                    tupleDefinitionMatrix[key][idx] = np.all([tupleNameComplianceMatrix[key][reaction] for reaction in member[u'n']])
               # if 'n' in member:
                #    tupleDefinitionMatrix[key][idx] = tupleDefinitionMatrix[key][idx]  and ruleNameComplianceMatrix
                #if 'n' in member:
        #cotains which rules are equal to reactions defined in reactionDefinitions['definitions']
        #use the per tuple classification to obtain a per reaction classification
        ruleDefinitionMatrix = zeros((len(rules),len(reactionDefinition['definitions'])))
        for key,element in ruleDictionary.items():
            for rule in element:
                #FIXME: This is totally a hack. fix so that it doesn't mistakingly classify something as binding
                #if 'R2' in key and ('R' in key or 'Ra' in key):
                    #ruleComplianceMatrix[rule] = [0,0,0,0]
                    #pass
                ruleDefinitionMatrix[rule] = self.checkCompliance(ruleComplianceMatrix[rule],
    tupleDefinitionMatrix[key],reactionDefinition['definitions'])
        #use reactionDefinitions reactionNames field to actually tell us what reaction
        #type each reaction is
        results = []    
        for element in ruleDefinitionMatrix:
            nonZero = nonzero(element)[0]
            if(len(nonZero) == 0):
                results.append('None')
            #todo: need to do something if it matches more than one reaction
            else:
                results.append(reactionDefinition['reactionsNames'][nonZero[0]])
        #now we will process the naming conventions section
        return  results
    
    def setConfigurationFile(self,configurationFile):
        self.configurationFile = configurationFile
        
    def classifyReactions(self,reactions,molecules):
        '''
        classifies a group of reaction according to the information in the json
        config file
        '''
        reactionDefinition = self.loadConfigFiles(self.configurationFile)
        equivalenceTranslator = {}
        #determines if two molecules have a relationship according to the naming convention section
        equivalenceTranslator = self.processNamingConventions(molecules,reactionDefinition['namingConvention'])
        rawReactions = [self.parseReactions(x) for x in reactions]
        reactionClassification = self.getReactionClassification(reactionDefinition,rawReactions,equivalenceTranslator)
        listOfEquivalences = []
        for element in equivalenceTranslator:
            listOfEquivalences.extend(equivalenceTranslator[element])
        return reactionClassification,listOfEquivalences,equivalenceTranslator
    
    
    def reclassifyReactions(self,reactions,molecules,labelDictionary):
        rawReactions = [self.parseReactions(x) for x in reactions]
        #reactionDefinition = loadConfigFiles()
        reactionDefinition = self.loadConfigFiles(self.configurationFile)
        equivalenceTranslator = self.processNamingConventions(molecules,reactionDefinition['namingConvention'])
        for reactionIndex in range(0,len(rawReactions)):
            for reactantIndex in range(0,len(rawReactions[reactionIndex])):
                tmp = []
                for chemicalIndex in range(0,len(rawReactions[reactionIndex][reactantIndex])):
                    tmp.extend(list(labelDictionary[rawReactions[reactionIndex][reactantIndex][chemicalIndex]]))
                rawReactions[reactionIndex][reactantIndex] = tmp
        
        reactionClassification = self.getReactionClassification(reactionDefinition,rawReactions,equivalenceTranslator)
        return reactionClassification,[],equivalenceTranslator          

    
    def processAnnotations(self,molecules,annotations):
        processedAnnotations = []
        for element in annotations:
            if len(annotations[element]) > 1:
                pro = [list(x) for x in itertools.combinations([y for y in annotations[element]],2)]
                processedAnnotations.extend(pro)
            
        return {-1:processedAnnotations}
    
    def annotationClassificationHelper(self,reactions,annotations):
        for reaction in reactions:
           for annotation in annotations:
               
               if ((annotation[0],) in reaction[0] and (annotation[1],) in reaction[1]) or ((annotation[0],) in reaction[1] and (annotation[1],) in reaction[0]):
                       print reaction,annotation
    
    def classifyReactionsWithAnnotations(self,reactions,molecules,annotations,labelDictionary):        
        '''
        this model will go through the list of reactions and assign a 'modification' tag to those reactions where
        some kind of modification goes on aided through annotation information
        '''
        rawReactions = [self.parseReactions(x) for x in reactions]
        equivalenceTranslator = self.processAnnotations(molecules,annotations)     
        for reactionIndex in range(0,len(rawReactions)):
            for reactantIndex in range(0,len(rawReactions[reactionIndex])):
                tmp = []
                for chemicalIndex in range(0,len(rawReactions[reactionIndex][reactantIndex])):
                    tmp.extend(list(labelDictionary[rawReactions[reactionIndex][reactantIndex][chemicalIndex]]))
                rawReactions[reactionIndex][reactantIndex] = tmp
        #self.annotationClassificationHelper(rawReactions,equivalenceTranslator[-1])         
