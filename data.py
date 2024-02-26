import pandas as pd

def setup_dataset_filtered():
    dataset = pd.read_csv(
        "manuallySelected.csv",
        on_bad_lines="skip",
        quotechar='"',
        engine="python",
    )

    return dataset


def setup_dataset():
    dataset = pd.read_csv(
        "eval_segments.csv",
        sep=", ",
        on_bad_lines="skip",
        skiprows=2,
        quotechar='"',
        engine="python",
    )

    return dataset[dataset["positive_labels"].str.match(".*/m/04rlf.*")]

dataset = setup_dataset_filtered()

def get_video():
    row = dataset.sample().iloc[0]

    return {"id": row["# YTID"], "start_time": row["start_seconds"]}

def get_videos() -> list[dict]:
    videos = []
    for _, row in dataset.sample(10).iterrows():
        videos.append({"id": row["# YTID"], "start_time": row["start_seconds"]})
    return videos
