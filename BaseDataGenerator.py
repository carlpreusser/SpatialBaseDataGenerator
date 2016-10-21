#  This script generates base data for the Environmental Health Service Area MobileGIS ArcPad Application
#  The data input is county level shapefiles and a directory of city named folders is created for storing
#  the clipped data to that level and area.
#  It is important to maintain the same input data where it is required...i.e. for the streets data input, use streets data.
#  author: Carl Preusser, created 6/17/2012

#import all modules
import arcpy
from arcpy import env
import os.path
import shutil
arcpy.env.overwriteOutput = True    

try:
    
    #Change Location A = Input city service area polygon
    #serviceArea = arcpy.GetParameterAsText(0)
    serviceArea = "boundaryCutshapefilepath"
    #make a feature layer for the serviceArea shapefile for geoprocessing...
    arcpy.MakeFeatureLayer_management(serviceArea,"cities_lyr")
    #describe the spatial reference of the service area shapefile.
    describeServiceArea = arcpy.Describe(serviceArea)
    spatialRefServiceArea = describeServiceArea.spatialReference

    #create the list for storing the county-level datasets...
    countyDataList = []

	#Change Location B = Input Streets 
    #streets = arcpy.GetParameterAsText(1)
    streets = "streetsshapefilepath"
    arcpy.MakeFeatureLayer_management(streets,"streets_lyr")
    countyDataList.append("streets_lyr")

	#Change Location C = Input Streams 
    # Streams
    streams = arcpy.GetParameterAsText(2)
    streams = "streetsshapefilename"
    arcpy.MakeFeatureLayer_management(streams,"streams_lyr")
    #countyDataList.append("streams_lyr")

	#Change Location C = Input Streams 
    # Parcels - Due to processing time, some 600,000 features in this dataset, this base data layer was left out...
    #           although this is what it would take to incorporate it.
    #parcels = "parcelsshapefilepath"
    #arcpy.MakeFeatureLayer_management(parcels,"parcels_lyr")
    #countyDataList.append("parcels_lyr")

    #create a list to store data tables to loop through for generating geographic features from...
    #programDataList = []
    # Storm Sewer Outfalls
    # programDataList.append(arcpy.GetParameterAsText(0))

    # Output File location
    #outputFolder = arcpy.GetParameterAsText(4)
    outputFolder = "outputfilepath"

	
	#this was a potential extension to iterate through programs to generate additional spatial data to cut to the city level
    # Household Sewage Systems - this is another program data source which would be utilized in the future to create a point
    #                            geographic data layer. Currently this program does not utilize mobileGIS.
    #programDataList.append(arcpy.GetParameterAsText(5))

except:
    arcpy.AddMessage("Error: Input data incorrect...check the input data are correct!")        
    

#this is an extension point to highly specific interally generated data...
#try:
    
    # For each program input table, create a point feature class
    #for table in programDataList: 
    #loop through all input program data tables and create a point feature class
    #There may be more tables added to this in the future for additional program data processing.
        #SQL to isolate only the storm water outfalls necessary for inspection, some are not listed as...
        #  Municipal Seperate Storm Sewer System (MS4) and therefore do not need inspected. 
        #stormSQL = "[OutfallType] = 'PUBS'"
        #utilize the SQL with a table view...
        #arcpy.MakeTableView_management(table, "ms4", stormSQL)
        #generate a dbf file
        #arcpy.CopyRows_management("ms4", outputFolder + "outfallView.dbf")
        # Set the spatial reference
        #spRef = r"Coordinate Systems\Geographic Coordinate Systems\North America\NAD 1983.prj"
        #outLayer = outputFolder + "stormOutfallPoints.shp" 
        # Make the XY event layer based on the stored latitude and longitude
        #arcpy.MakeXYEventLayer_management(outputFolder + "outfallView.dbf", "Longitude", "Latitude", outLayer, spRef)
        # Make a feature layer for further geoprocessing...
        #arcpy.MakeFeatureLayer_management(outLayer,"outfalls_lyr") 
        #Add this newly created county storm sewer outfall point layer to the county data list...
        #countyDataList.append("outfalls_lyr")
        
    #arcpy.AddMessage("Successfully generated outfall point layer!") 

#except:
    #arcpy.AddMessage("Error: Could not create the outfall point layer!") 

try:

    #create the search cursor object for reading through the service area polygon file records
    rows = arcpy.SearchCursor(serviceArea)
    row = rows.next()

    #loop through every city in the service_area dataset        
    while row:
        #This field in the serviceArea shapefile holds the city name in a capitalized format with spaces in between words.
        city = row.MCDNAME
        #make the city name all lower case...
        cityLower = city.lower()
        #replace the spaces in the city name with underscores
        cityName = cityLower.replace(" ", "_")
        #This script generates data for an ArcPad application which works with data stored at the city level in folders
        #  with a specific nomenclature.  We need to ensure that nomenclature exists.
        #check to see if the folder of the city name of the current record we are on exists...
        if os.path.exists(outputFolder + "\\" + cityName) == True:
            #This city file exists...we need to dump it to prepare for new data!
            shutil.rmtree(outputFolder + "\\" + cityName)
            #change the directory to the output folder
            os.chdir(outputFolder)
            #make the folder with the proper city name
            os.makedirs(cityName) 
        else:
            #No folder exists for this city record...create one!
            os.chdir(outputFolder)
            os.makedirs(cityName)
            
        #Now we loop through our input county-level data set list and begin our clip process.
        for fc in countyDataList:
            #Check the feature classes from the list of base data
            #Look for the desired transformation
            describeFC = arcpy.Describe(fc)
            spatialRefFC = describeFC.spatialReference
            #Ensure the spatial reference matches the serviceArea shapefile, ArcPad does not re-project on the fly and will
            # simply not show any data if the projection does not match.
            if spatialRefFC.Name != spatialRefServiceArea.Name:
                arcpy.Project_management(fc, fc, spatialRefServiceArea)     
                    
            #generate SQL clause for the selection by attribute
            whereClause = '"MCDNAME"' + " = '" + str(city) + "'"
            #This selects the current record of the loop in the serviceArea data
            arcpy.SelectLayerByAttribute_management("cities_lyr", "NEW_SELECTION", whereClause)
            #This variable stores the split name of the layer of the current county level data
            #  The names for the created layers have a specific nomenclature as well as the city data.
            #  Notice that the desired identifier name of the data is on the right side (streets, streams, outfalls, etc.)
            fcNamePieces = fc.split("_")
            #Select the right side word for labeling the output.
            fcName = fcNamePieces[0]
            outFeatureClass = os.path.join(outputFolder + "\\" + cityName, cityName + "_" + fcName + ".shp")
            #Execute the clip tool
            arcpy.Clip_analysis(fc,"cities_lyr",outFeatureClass, 0)
            #Each created city data shapefile must also have an associated XML file which has a suffix .apl
            #  These are for the ArcPad program to read and generate consistent symbology.
            #The source is generated based on the user input file location...
            #  The name of the individual file is further defined by the addition of the identifier name defined above.
              #srcAPL = outputFolder + "\\" + "_" + fcName + ".apl"
            #The final output APL file name includes the directory of the current city name folder and city name/data 
              #outAPL = outputFolder + "\\" + cityName + "\\" + cityName + "_" + fcName + ".apl"
            #The file is copied from the source to the new location
              #shutil.copy(srcAPL, outAPL)
			
			#this section seeks to utilize the layer to kml tool to generate the keyhole markup language format Geo data
			# Set Local Variables
            #composite = 'NO_COMPOSITE'
            #pixels = 2048
            #dpi = 192
            # Strips the '.lyr' part of the name and appends '.kmz'
            outKML = os.path.join(outputFolder + "\\" + cityName, cityName + "_" + fcName + ".kmz")
            arcpy.MakeFeatureLayer_management(outFeatureClass,"city_kml")
            try:
				arcpy.LayerToKML_conversion("city_kml", outKML, 1)
				arcpy.AddMessage(outKML + " file successfully generated...")
            except:
				arcpy.AddMessage("Could not complete the KML conversion!")

        arcpy.AddMessage(city + " data successfully generated. On to the next city...")
        #go to the next city record for further processing of the data...    
        row = rows.next()

    arcpy.AddMessage("City data processing complete!")
    
except:
    arcpy.AddMessage("Could not complete the data analysis!")

# Clean up cursor and row objects
del row
del rows

# Clean up feature layers
# It's best to loop through and clean up that way...
for fc in countyDataList:
    arcpy.Delete_management(fc)
	
# def addRanks(table, sort_fields, category_field, rank_field='RANK'):
    # """Use sort_fields and category_field to apply a ranking to the table.
 
    # Parameters:
        # table: string
        # sort_fields: list | tuple of strings
            # The field(s) on which the table will be sorted.
        # category_field: string
            # All records with a common value in the category_field
            # will be ranked independently.
        # rank_field: string
            # The new rank field name to be added.
    # """
 
    add rank field if it does not already exist
    # if not arcpy.ListFields(table, rank_field):
        # arcpy.AddField_management(table, rank_field, "SHORT")
 
    # sort_sql = ', '.join(['ORDER BY ' + category_field] + sort_fields)
    # query_fields = [category_field, rank_field] + sort_fields
 
    # with arcpy.da.UpdateCursor(table, query_fields,
                               # sql_clause=(None, sort_sql)) as cur:
        # category_field_val = None
        # i = 0
        # for row in cur:
            # if category_field_val == row[0]:
                # i += 1
            # else:
                # category_field_val = row[0]
                # i = 1
            # row[1] = i
            # cur.updateRow(row)
 
# if __name__ == '__main__':
    # addRanks(r'C:\Data\f.gdb\gen_near_table_patients2hosp',
             # ['distance'], 'patient', 'rank')
