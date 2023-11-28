# DicomVocab2OMOP
This project looks at creating a controlled vocabulary for the DICOM Pt 6 Data Dictionary with a focus on CS code strings in the OMOP vocabulary format and harmonizing common data elements (CDE).

- Create a library that takes a dicom tag
- - (eg Part 6 0010,0040 Patient Sex)
  - (Link to Part 16 CID 7455 Sex)
  - (Ingest FHIR JSON)
- Identify current gaps in SNOMED and LOINC mapping from DICOM 

References
- [Part 5 of Dicom Standard identifying Code Structures.](https://dicom.nema.org/medical/dicom/current/output/html/part05.html)
- [Part 6 Dicom Data Dictionary](https://dicom.nema.org/medical/dicom/current/output/html/part06.html)
- [Part 16 Dicom Context Groups](https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_2)
- [OHDSI Vocabulary Tables CDM 5.4](https://ohdsi.github.io/CommonDataModel/cdm54.html#Vocabulary_Tables)




