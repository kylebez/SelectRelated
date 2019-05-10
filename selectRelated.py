import arcpy

'''Source from StackExchange, modified by Kyle Beswick'''

# function to establishes the where clause used to select related records from table
def buildWhereClauseFromList(OriginTable, PKeyField, FKeyField, valueList):
    """Takes a list of values and constructs a SQL WHERE
       clause to select those values within a given PrimaryKeyField
       and OriginTable."""
    # Add DBMS-specific field delimiters
    fieldDelimited = arcpy.AddFieldDelimiters(arcpy.Describe(OriginTable).path, FKeyField)

    # Determine field type
    fieldType = arcpy.ListFields(OriginTable, PKeyField)[0].type

    # Add single-quotes for string field values
    if str(fieldType) == 'String':
        valueList = ["'%s'" % value for value in valueList]
    # Format WHERE clause in the form of an IN statement
    whereClause = "%s IN(%s)" % (fieldDelimited, ', '.join(map(str, valueList)))
    if len(valueList)==0:whereClause = None
    return whereClause

# Primary function used to select related records
# returns list of related features if returnOrphans is False, otherwise returns an orphan list
# returns a one-object list if returnTwoWay is False, otherwise, returns a two-object list
def selectRelatedRecords(OriginTable, DestinationTable, PrimaryKeyField, ForeignKeyField, returnTwoWay=False, returnOrphans=False):    
    """Defines the record selection from the record selection of the OriginTable
      and applys it to the DestinationTable using a SQL WHERE clause built
      in the previous definition
      Optional PARAM to check a two-way relationship
      Optional PARAM to return a set of orphaned values
      """
    def getOrphans(relatedDict, fullDict):
        relatedSet = set(relatedDict.values())
        fullSet = set(fullDict.values())
        fullDictSwap = {val:key for (key, val) in fullDict.items()}        
        orphanSet = set()
        if fullSet.issuperset(relatedSet):
            for o in fullSet.difference(relatedSet):
                orphanSet.add(fullDictSwap[o])
        if str(orphanSet) == 'set()': orphanSet = None
        return orphanSet

    # Function to return all keys specified
    def getSourceIDs(table, keyfield):
        # Set the SearchCursor to look through the selection of the OriginTable
        if keyfield == "OBJECTID": fields = [keyfield]
        else:
            fields = ["OBJECTID", keyfield]
        curs = arcpy.da.SearchCursor(table, fields)#add recently edited clause?
        sourceIDs = dict()
        with curs:
            for row in curs:
                sourceIDs[row[0]] = row[len(row)-1]
        return sourceIDs
        
    # Wrapper function to establishes the where clause used to select related records from table
    def getWhereClause(ids):          
        whereClause = buildWhereClauseFromList(OriginTable, PrimaryKeyField, ForeignKeyField, ids)
        return whereClause
    idsOneWay = getSourceIDs(OriginTable, PrimaryKeyField)  
    whereOneWay = getWhereClause(idsOneWay.values())
    whereTwoWay = None
    relatedFeaturesOneWay = None
    relatedFeaturesTwoWay =  None

    # if doing a two-way relation, switch the parameters in order to reverse the relationship selection
    if returnTwoWay is True:
        OriginTable, DestinationTable = DestinationTable, OriginTable
        PrimaryKeyField, ForeignKeyField = ForeignKeyField, PrimaryKeyField
        idsTwoWay = getSourceIDs(OriginTable, PrimaryKeyField)
        whereTwoWay = getWhereClause(idsTwoWay.values())
        DestinationTable, OriginTable = OriginTable, DestinationTable
        ForeignKeyField, PrimaryKeyField = PrimaryKeyField, ForeignKeyField 

    # Select features on the built where clause  
    if whereOneWay is not None:        
        relatedFeaturesOneWay = arcpy.SelectLayerByAttribute_management(DestinationTable, "NEW_SELECTION", whereOneWay)    
    if whereTwoWay is not None:
        relatedFeaturesTwoWay = arcpy.SelectLayerByAttribute_management(OriginTable, "NEW_SELECTION", whereTwoWay)
   
    # return feature list if not returning orphans
    if not returnOrphans:
        relatedFeatures = [relatedFeaturesOneWay]
        if returnTwoWay:
            relatedFeatures.append(relatedFeaturesTwoWay)            
        return relatedFeatures
    # return feature list if not returning orphans   
    else:
        orphanList = []
        if not relatedFeaturesOneWay is None:            
            idsFromOneWaySelection = getSourceIDs(relatedFeaturesOneWay, ForeignKeyField)
            orphanList = [getOrphans(idsFromOneWaySelection,idsOneWay)]
        if returnTwoWay:
            if not relatedFeaturesTwoWay is None:
                idsFromTwoWaySelection = getSourceIDs(relatedFeaturesTwoWay, PrimaryKeyField)
                orphanList.append(getOrphans(idsFromTwoWaySelection,idsTwoWay))
        if len(orphanList)==0:orphanList=None        
        return orphanList
