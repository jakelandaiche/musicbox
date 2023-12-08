import pandas as pd

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

dataset = setup_dataset()

def get_videos() -> list[dict]:
    videos = []
    for _, row in dataset.sample(10).iterrows():
        videos.append({"id": row["# YTID"], "start_time": row["start_seconds"]})
    return videos
