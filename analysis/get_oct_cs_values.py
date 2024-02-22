import argparse
from pathlib import Path

import pandas as pd
from pydicom import dcmread
from pydicom.dataset import Dataset, FileDataset, Tag

# Flatten the dataset by iterating over data elements and excluding Sequence of Items (SQ) data elements
def get_flattened_dataset(dataset: FileDataset | Dataset) -> Dataset:
    return Dataset({de.tag: de for de in dataset.iterall() if de.VR != "SQ"})

# A list of DICOM tags to be excluded from the shared dataset in the create_sf_headers function
EXCLUDE_TAGS = [
    Tag("SharedFunctionalGroupsSequence"),
    Tag("PerFrameFunctionalGroupsSequence"),
    Tag("DimensionIndexSequence"),
    Tag("NumberOfFrames"),
    Tag("SourceImageEvidenceSequence"),
    Tag("ReferencedImageEvidenceSequence"),
    Tag("PixelData"),
]


def fix_sf_headers(dataset: Dataset) -> Dataset:
    # Update the EchoTime from EffectiveEchoTime if present
    if "EffectiveEchoTime" in dataset:
        dataset.EchoTime = dataset.EffectiveEchoTime
    # Normalize and update ScanningSequence based on existing tags and their values    
    scan_seq: list = (
        (
            dataset.ScanningSequence
            if dataset["ScanningSequence"].VM > 1
            else [dataset.ScanningSequence]
        )
        if "ScanningSequence" in dataset
        else []
    )
    if "EchoPulseSequence" in dataset:
        if dataset.EchoPulseSequence != "SPIN":
            scan_seq.append("GR")
        if dataset.EchoPulseSequence != "GRADIENT":
            scan_seq.append("SE")
    if dataset.get("InversionRecovery", "NO") == "YES":
        scan_seq.append("IR")
    if dataset.get("EchoPlanarPulseSequence", "NO") == "YES":
        scan_seq.append("EP")
    dataset.ScanningSequence = sorted(set(scan_seq))

    # Normalize and update SequenceVariant based on existing tags and their values
    seq_var: list = (
        (
            dataset.SequenceVariant
            if dataset["SequenceVariant"].VM > 1
            else [dataset.SequenceVariant]
        )
        if "SequenceVariant" in dataset
        else []
    )
    if dataset.get("SegmentedKSpaceTraversal", "SINGLE") != "SINGLE":
        seq_var.append("SK")
    if dataset.get("MagnetizationTransfer", "NONE") != "NONE":
        seq_var.append("MTC")
    if dataset.get("SteadyStatePulseSequence", "NONE") != "NONE":
        seq_var.append("TRSS" if dataset.SteadyStatePulseSequence == "TIME_REVERSED" else "SS")
    if dataset.get("Spoiling", "NONE") != "NONE":
        seq_var.append("SP")
    if dataset.get("OversamplingPhase", "NONE") != "NONE":
        seq_var.append("OSP")
    if len(seq_var) == 0:
        seq_var.append("NONE")
    dataset.SequenceVariant = sorted(set(seq_var))

    # Normalize and update ScanOptions based on existing tags and their values
    scan_opts: list = (
        (dataset.ScanOptions if dataset["ScanOptions"].VM > 1 else [dataset.ScanOptions])
        if "ScanOptions" in dataset
        else []
    )
    if dataset.get("RectilinearPhaseEncodeReordering", "LINEAR") != "LINEAR":
        scan_opts.append("PER")
    frame_type3 = dataset.FrameType[2]
    if frame_type3 == "ANGIO":
        dataset.AngioFlag = "Y"
    if frame_type3.startswith("CARD"):
        scan_opts.append("CG")
    if frame_type3.endswith("RESP_GATED"):
        scan_opts.append("RG")
    if "PartialFourierDirection" in dataset:
        if dataset.PartialFourierDirection == "PHASE":
            scan_opts.append("PFP")
        elif dataset.PartialFourierDirection == "FREQUENCY":
            scan_opts.append("PFF")
    if dataset.get("SpatialPresaturation", "NONE") != "NONE":
        scan_opts.append("SP")
    if dataset.get("SpectrallySelectedSuppression", "NONE").startswith("FAT"):
        scan_opts.append("FS")
    if dataset.get("FlowCompensation", "NONE") != "NONE":
        scan_opts.append("FC")
    dataset.ScanOptions = sorted(set(scan_opts))
    return dataset

# Create shared datasets excluding specified tags and update with flattened shared functional groups
def create_sf_headers(dataset: Dataset | FileDataset) -> list[Dataset]:
    shared_ds = Dataset({de.tag: de for de in dataset if de.tag not in EXCLUDE_TAGS})
    shared_ds.file_meta = dataset.file_meta
    shared_ds.update(get_flattened_dataset(dataset.SharedFunctionalGroupsSequence[0]))
    flattened_frame_ds_list = [
        get_flattened_dataset(dataset.PerFrameFunctionalGroupsSequence[i])
        for i in range(len(dataset.PerFrameFunctionalGroupsSequence))
    ]
    # Flatten each frame in the PerFrameFunctionalGroupsSequence and update
    sf_ds_list = []
    for flat_frame_ds in flattened_frame_ds_list:
        sf_ds = Dataset({de.tag: de for de in shared_ds})
        sf_ds.update(flat_frame_ds)
        if sf_ds.Modality == "MR":
            sf_ds = fix_sf_headers(sf_ds)
        sf_ds_list.append(sf_ds)
    return sf_ds_list

# Iterate through DICOM objects and extract CS values
def main(subjects: list[Path], part6: pd.DataFrame, out_file: Path):
    for i, subject in enumerate(subjects):
        records = []
        subject_id = f'{i:05}'
        studies = []
        for session in subject.glob('*'):
            study = subject.name + session.name
            try:
                study_id = f'{studies.index(study):02}'
            except ValueError:
                studies.append(study)
                study_id = f'{len(studies) - 1:02}'
            series_uids = []
            images = []
            for dcm_file in session.rglob("*.dcm"):
                ds_orig = dcmread(dcm_file, stop_before_pixels=True)
                if "SharedFunctionalGroupsSequence" in ds_orig:
                    ds_list = create_sf_headers(ds_orig)
                else:
                    ds_list = [ds_orig]
                for i, ds in enumerate(ds_list):
                    try:
                        series_id = f'{series_uids.index(ds.SeriesInstanceUID):02}'
                    except ValueError:
                        series_uids.append(ds.SeriesInstanceUID)
                        series_id = f'{len(series_uids) - 1:02}'
                    image = ds.SeriesInstanceUID + str(ds.InstanceNumber) + str(i)
                    try:
                        image_id = f'{images.index(image):03}'
                    except ValueError:
                        images.append(image)
                        image_id = f'{len(images) - 1:03}'
                    for tag_id in part6.tag.values:
                        if tag_id in ds:
                            tag = ds[tag_id]
                            if tag.VM <= 1:
                                values = [tag.value]
                            else:
                                values = tag.value
                            for v in values:
                                records.append(
                                    {
                                        "institution": ds.InstitutionName,
                                        "manufacturer": ds.Manufacturer,
                                        "model": ds.ManufacturerModelName,
                                        "modality": ds.Modality,
                                        "year": ds.SeriesDate[:4],
                                        "tag": tag_id,
                                        "value": v,
                                        "subject": subject_id,
                                        "session": subject_id + study_id,
                                        "series": subject_id + study_id + series_id,
                                        "image": subject_id + study_id + series_id + image_id,
                                    }
                                )
        df = pd.DataFrame(records)
        df.to_csv(out_file, mode='a', index=False)

# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("subjects", type=Path, nargs="+")
    parser.add_argument("--part6-csv", type=Path, required=True)
    parser.add_argument("--out-file", type=Path, required=True)
    parsed = parser.parse_args()

    main(parsed.subjects, pd.read_csv(parsed.part6_csv), parsed.out_file)