# SelectRelated

Pass script function with the params:
  selectRelatedRecords(OriginTable, DestinationTable, PrimaryKeyField, ForeignKeyField, returnTwoWay=False, returnOrphans=False)
  
  OriginTable can be a selected set Table View or Feature Layer
  
  Will return Table View or Feature Layer containing the related features
  
  If returnTwoWay is True will return a list of Table Views and/or Feature Layers with the first index being Origin->Dest and the second being Dest->Origin
  
  If returnOrphans is True will return a list of OIDs for every feature in the Origin that does not have a related feature in the destination
  returnOrphans=True and returnTwoWay=True will return a list of OID lists with the first index being Origin->Dest and the second being Dest->Origin
