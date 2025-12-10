# DICOM2OMOP
This project builds on a published work, ["Development of Medical Imaging Data Standardization for Imaging-Based Observational Research: OMOP Common Data Model Extension"](https://pubmed.ncbi.nlm.nih.gov/38315345/). A copy of the full paper can also be found in the files folder.
This project aims to create a controlled vocabulary for the DICOM Pt 6 Data Dictionary and DICOM Pt 16, focusing on code strings in the OMOP vocabulary format.

- Create a library that takes a DICOM tag
- - (eg Part 6 0010,0040 Patient Sex)
  - (Link to Part 16 CID 7455 Sex)
  - (Ingest FHIR JSON)
  - (Create "maps to" from Source to Standard vocabulary for OMOP gender)
- Identify current gaps in SNOMED and LOINC mapping from DICOM 

### References
- [Part 5 of Dicom Standard identifying Code Structures.](https://dicom.nema.org/medical/dicom/current/output/html/part05.html)
- [Part 6 Dicom Data Dictionary](https://dicom.nema.org/medical/dicom/current/output/html/part06.html)
- [Part 16 Dicom Context Groups](https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_2)
- [OHDSI Vocabulary Tables CDM 5.4](https://ohdsi.github.io/CommonDataModel/cdm54.html#Vocabulary_Tables)
- [DICOM Vocab Browser](https://dicom.innolitics.com/ciods)

## Repo Structure
1. Harvest standards: this folder includes codes to ingest DICOM Standard from JSON and XML files. You may skip this step and access to ingested files in the files folder. You can use this code scripts to ingest newer versions of the DICOM Standard. 
2. DICOM to OMOP: this folder contains codes to build the imaging extension tables to your existing OMOP CDM, trainsform ingested DICOM Standards into OMOP format, and upload the newly created DICOM concepts to the OMOP CDM with imaging extension. 
3. Demonstration: we extracted data from Alzheimer's Disease Neuroimaging Initiative Image and Data Archive (ADNI IDA). The demographics, clinical data are in flat file formats, and the images in the DICOM format. We pre-loaded ADNI 3 DICOM images to Johns Hopkins Azure instance, and accessed the imaging file from the Azure. This folder includes scripts to download and unpack DICOM metadata from the images and transforming imaging metadata and data from flat files. In addition to the imaging metadata, we ran a segmentation algorithm from OpenMAP, and transformed the results into OMOP CDM format. The code to run the algorithm is not part of this repo, but the transformation of results is in "transform_upload_imaging_algo_results.ipynb" file.
4. Analysis: all the other exploratory analyses are stored in this folder.

## If you would like to add the imaging extension to your OMOP CDM
1. Download the DICOM custom concepts from [files](https://github.com/paulnagy/DICOM2OMOP/tree/main/files/OMOP%20CDM%20Staging). Pick the latest version of *omop_table_staging*.
2. Load DICOM concepts to your Concept table. Example code [here](https://github.com/paulnagy/DICOM2OMOP/blob/main/dicom_standard_to_omop/load_dicom_to_omop.ipynb)
3. Create imaging extension tables. Example code [here](https://github.com/paulnagy/DICOM2OMOP/blob/main/dicom_standard_to_omop/build_imaging_extension.ipynb)
4. Extract DICOM metadata from your storage. Example code [here](https://github.com/paulnagy/DICOM2OMOP/blob/main/demonstration/extract_ADNI_images.ipynb)
5. Transform DICOM metadata to OMOP format. Example code [here](https://github.com/paulnagy/DICOM2OMOP/blob/main/demonstration/transform_imaging_metadata.ipynb)
6. Load transformed metadata. Example code [here](https://github.com/paulnagy/DICOM2OMOP/blob/main/demonstration/load_imaging_data.ipynb)
7. If you have imaging algorithm results, you can also use the imaging extension tables to maintain the provenance and store the results back to OMOP CDM. Example code [here](https://github.com/paulnagy/DICOM2OMOP/blob/main/demonstration/transform_load_imaging_algo_results.ipynb)
