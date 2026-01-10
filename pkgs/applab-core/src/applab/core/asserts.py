from deepdiff import DeepDiff
from deepdiff.helper import COLORED_VIEW


def __get_all_paths(d, current_path="root"):
    """get all paths from a nested dict or list"""
    paths = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_path = f"{current_path}['{k}']"
            paths.extend(__get_all_paths(v, new_path))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_path = f"{current_path}[{i}]"
            paths.extend(__get_all_paths(v, new_path))
    else:
        # leaf node（int, str, float...）
        paths.append(current_path)
    return paths


def diff_subset(expected_subset: dict, fullset: dict, ):
    diff = DeepDiff(fullset, expected_subset, include_paths=__get_all_paths(expected_subset), view=COLORED_VIEW)
    assert {} == diff, diff
