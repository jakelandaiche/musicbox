import pandas as pd

def setup_dataset_filtered():
    dataset = pd.read_csv(
        "filtered.csv",
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

def get_videos(N=10, dataset="musicCaps1.csv") -> list[dict]:
    dataset = pd.read_csv(
        dataset,
        on_bad_lines="skip",
        quotechar='"',
        engine="python",
    )

    videos = []
    for _, row in dataset.sample(N).iterrows():
        videos.append({"id": row["# YTID"], "start_time": row["start_seconds"]})
    return videos
