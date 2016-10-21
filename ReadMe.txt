You might find this script useful if you need small data footprint on disk available for consumption from a program or 
website

The PyBaseDataGenerator script works in the following manner:

1. Utilizes ArcGIS tools to take a boundary file and creates a list of datasets to cut to the original boundary file polygons

2. Next loops through all records within the boundary file and generates a folder with the identified individual record within the boundary
name (i.e. like a city or whatever boundary level your at...parcel, etc.) 

3. Inside the loop it will loop/iterate through the cut dataset list and cut all datasets identified to this record's boundary level

so you will be left with a file structure like this:

\BoundaryName (cityname...attribute point you declare in the boundary file)
\BoundaryName\boundaryname_cutfilename.shp

Requirements Prior to Use:

1. Python 2.6-2.7 ---may work with later versions or earlier versions

2. Valid ArcGIS license for the computer which the script is run

3. Saving a copy of the script on your local computer

4. Opening the script file copy in a Text Editor and renaming the locations of:
  CHANGE LOCATIONS (as detailed in the comments of the script file)
   A. your path location to the boundary file
   B-C. your path location to the boundary cut files	
   
Known Issues:

- Requires manual renaming of the file names.
- could export to file or personal geodatabase also


TO DO List:
 
- provide a class/OOB architecture to the creation of a cut dataset or utilize an existing arcpy dataset attributes for naming
- error handling alerts if this is a nightly run script


