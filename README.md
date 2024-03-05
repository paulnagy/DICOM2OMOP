# Dicom2OMOP
This project looks at creating a controlled vocabulary for the DICOM Pt 6 Data Dictionary with a focus on CS code strings in the OMOP vocabulary format and harmonizing common data elements (CDE).

- Create a library that takes a dicom tag
- - (eg Part 6 0010,0040 Patient Sex)
  - (Link to Part 16 CID 7455 Sex)
  - (Ingest FHIR JSON)
  - (Create "maps to" from Source to Standard vocabulary for OMOP gender)
- Identify current gaps in SNOMED and LOINC mapping from DICOM 

References
- [Part 5 of Dicom Standard identifying Code Structures.](https://dicom.nema.org/medical/dicom/current/output/html/part05.html)
- [Part 6 Dicom Data Dictionary](https://dicom.nema.org/medical/dicom/current/output/html/part06.html)
- [Part 16 Dicom Context Groups](https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_2)
- [OHDSI Vocabulary Tables CDM 5.4](https://ohdsi.github.io/CommonDataModel/cdm54.html#Vocabulary_Tables)
- [DICOM Vocab Browser](https://dicom.innolitics.com/ciods)


## Requirements

Developed and Tested for:
- WSL Ubuntu 22.04.3 LTS (Jammy Jellyfish)
- openjdk version "11.0.21" 2023-10-17
- Python 3.10.12

## Instructions

### 0. Ensure the system is up to date and install dependencies

```bash
sudo apt update && sudo apt upgrade
sudo apt install bzip2 default-jdk default-jre xsltproc libxml2-utils python3-pip python3.10-venv
```
For macOS, use Homebrew package management system
```bash
brew update
brew upgrade # if needed
```

Verify java installation

```bash
java -version
```
> openjdk version "11.0.21" 2023-10-17

The macOS has its legacy Java, and it is possible that your macOS is not using openjdk. You can install it and read the output for next steps (e.g., setting symlink and path)
```bash
brew install openjdk
brew info openjdk
```
Symlink
```bash
sudo ln -sfn /usr/local/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk
```
Set path
```bash
echo 'export PATH="/usr/local/opt/openjdk/bin:$PATH"' >> ~/.zshrc
```

### 1. Download the current source and rendering pipeline from dicom.nema.org using curl (wget or another method will also work)

```bash
curl https://dicom.nema.org/medical/dicom/current/DocBookDICOM2024a_sourceandrenderingpipeline_20240120075929.tar.bz2 --output sourceandrenderingpipeline.tar.bz2
```

### 2. Extract to a directory, remove archive, and navigate to the directory

```bash
mkdir sourceandrenderingpipeline 

tar -xvf sourceandrenderingpipeline.tar.bz2 -C sourceandrenderingpipeline

rm sourceandrenderingpipeline.tar.bz2

cd sourceandrenderingpipeline
```

### 3. Update absolute paths using the provided bash script

```bash
./updateabsolutepaths.sh
```

If you get an error message that gsed: command not found, then install gsed package first and run it again.
```bash
brew install gnu-sed
```

### 4. Generate the databases for the parts (example for part 16)

```bash
./generateolinkdb.sh 16
```
### 5. Generate FHIR valuesets

#### 5.1 Navigate to the valuesets subdirectory and download Java package dependencies

```bash
cd valuesets
curl https://repo1.maven.org/maven2/javax/json/javax.json-api/1.0/javax.json-api-1.0.jar --output javax.json-api-1.0.jar
curl https://repo1.maven.org/maven2/org/glassfish/javax.json/1.0.4/javax.json-1.0.4.jar --output javax.json-1.0.4.jar
```

#### 5.2 Create a backup of the bash script used to extract valuesets, then modify the reference to the Java packages in the bash file and run it

```bash
cp extractvaluesets.sh{,.old}
sed -i 's|${HOME}/work/pixelmed/imgbook/lib/additional/|./|g' extractvaluesets.sh
./extractvaluesets.sh
```

For macOS, `-i` syntax needs explicit argument specifying the extension for backup files.
```bash
cp extractvaluesets.sh{,.old}
sed -i.bak 's|${HOME}/work/pixelmed/imgbook/lib/additional/|./|g' extractvaluesets.sh
./extractvaluesets.sh
```

#### 5.3 Count the extracted json files to validate they match

```bash
find ./valuesets/fhir/json/ -type f -name "*.json" | wc -l
```
>1341

### 6. Setup the Python virtual environment

> note: this should be done in the root DICOM2OMOP directory. We use `cd ../..` here to navigate there from `DICOM2OMOP/sourceandrenderingpipeline/valuesets`

This may take a few minutes as packages are installed.

```bash
cd ../..
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
python DICOM_P16_harvest_json.py
```

## References

- [Part 5 of Dicom Standard identifying Code Structures.](https://dicom.nema.org/medical/dicom/current/output/html/part05.html)
- [Part 6 Dicom Data Dictionary](https://dicom.nema.org/medical/dicom/current/output/html/part06.html)
- [Part 16 Dicom Context Groups](https://dicom.nema.org/medical/dicom/current/output/html/part16.html#sect_CID_2)
- [OHDSI Vocabulary Tables CDM 5.4](https://ohdsi.github.io/CommonDataModel/cdm54.html#Vocabulary_Tables)
- [DICOM Vocab Browser](https://dicom.innolitics.com/ciods)