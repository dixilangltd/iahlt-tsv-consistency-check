# Copyright 2022 Yan Khachko for DixiLang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import timedelta
import argparse
import datetime
import typing
import csv
import os


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


parser = argparse.ArgumentParser()
parser.add_argument("--path", type=dir_path, required=True)

args = parser.parse_args()


def convert_to_timedelta(time: str) -> timedelta:
    """Convert 00:00:00:00 formatted from file to timedelta"""
    dt = datetime.datetime.strptime(time + "0000", "%H:%M:%S:%f")
    return timedelta(
        hours=dt.hour, minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond
    )


def get_len_from_meta(name: str) -> typing.Optional[timedelta]:
    """Get file length from {name}.meta.tsv file"""
    filepath = os.path.join(args.path, f"{name}.meta.tsv")
    with open(filepath, encoding="utf-8") as meta_file:
        lines = list(csv.reader(meta_file, delimiter="\t"))
        time = lines[1][2]
        try:
            dt = datetime.datetime.strptime(time, "%H:%M:%S")
        except ValueError:
            print(f"{filepath} Wrong duration format {time}")
            return None
        return timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)


def check_name_tsv(
        name: str, len_from_meta: timedelta, speakers: typing.List[str]
) -> typing.List[typing.Dict[str, str]]:
    """Check {name}.tsv (1.tsv etc) for bad rows"""
    wrong = []

    if not len_from_meta:
        wrong += {
            "filepath": filepath,
            "line": 1,
            "error": "No len from meta.tsv",
            "type": "name_tsv",
        }
        return wrong

    filepath = os.path.join(args.path, f"{name}.tsv")

    with open(filepath, encoding="utf-8") as tsv_file:
        name_tsv = csv.reader(tsv_file, delimiter="\t")
        for line, row in enumerate(list(name_tsv)[1:]):
            line += 2  # first line is header

            # check line format
            if len(row) != 4 or not row[-1]:
                wrong += {
                    "filepath": filepath,
                    "line": line,
                    "error": "wrong line format",
                    "type": "name_tsv",
                }
                print(f"{filepath}.{line}: name_tsv wrong line format {len(row)}")

            try:
                # convert times to timedelta
                start_from_tsv = convert_to_timedelta(row[0].split(" - ")[0])
                end_from_tsv = convert_to_timedelta(row[0].split(" - ")[1])
                duration_from_tsv = convert_to_timedelta(row[1])
            except ValueError:
                wrong += {
                    "filepath": filepath,
                    "line": line,
                    "error": "error while parsing time format, time format error",
                    "type": "name_tsv",
                }
                print(f"{filepath}.{line}: name_tsv error while parsing time format, time format error")
                continue

            # check if end bigger than file length
            if end_from_tsv > len_from_meta + timedelta(milliseconds=500):
                wrong += {
                    "filepath": filepath,
                    "line": line,
                    "error": "end bigger than file length",
                    "type": "name_tsv",
                }
                print(f"{filepath}.{line}: name_tsv end bigger than file length. {end_from_tsv} > {len_from_meta}")

            # check if start bigger than file length
            if start_from_tsv > len_from_meta + timedelta(milliseconds=500):
                wrong += {
                    "filepath": filepath,
                    "line": line,
                    "error": "start bigger than file length",
                    "type": "name_tsv",
                }
                print(f"{filepath}.{line}: name_tsv start bigger than file length. {start_from_tsv} > {len_from_meta}")

            # check if start bigger than end
            if start_from_tsv > end_from_tsv:
                wrong += {
                    "filepath": filepath,
                    "line": line,
                    "error": "start bigger than end",
                    "type": "name_tsv",
                }
                print(
                    f"{filepath}.{line}: name_tsv start bigger than end "
                    f"{start_from_tsv} > {end_from_tsv}"
                )

            # check if end - start != duration
            if end_from_tsv - start_from_tsv != duration_from_tsv:
                wrong += {
                    "filepath": filepath,
                    "line": line,
                    "error": "duration missmatch",
                    "type": "name_tsv",
                }
                print(
                    f"{filepath}.{line}: name_tsv duration missmatch "
                    f"{end_from_tsv} - {start_from_tsv} != {duration_from_tsv} (diff: {((end_from_tsv - start_from_tsv) - duration_from_tsv).total_seconds()}s)"
                )

            # check if speaker not in speakers.tsv
            if row[2] not in speakers and row[2] != "Group of Speakers":
                wrong += {
                    "filepath": filepath,
                    "line": line,
                    "error": "speaker not in speakers",
                    "type": "name_tsv",
                }
                print(f"{filepath}.{line}: name_tsv speaker \"{row[2]}\" not in speakers")

    # return dict with all errors from file
    return wrong


def check_speaker_tsv(name: str) -> (typing.List[dict], typing.List[str]):
    """Check {name}.speaker.tsv (1.speaker.tsv etc) for bad rows"""
    wrong = []
    speakers = []

    filepath = os.path.join(args.path, f"{name}.speaker.tsv")

    with open(filepath, encoding="utf-8") as tsv_file:
        speaker_tsv = csv.reader(tsv_file, delimiter="\t")
        for line, row in enumerate(list(speaker_tsv)[1:]):
            line += 2  # first line is header

            # check line format
            if len(row) != 8:
                wrong += {
                    "filepath": filepath,
                    "line": line,
                    "error": "wrong line format",
                    "type": "speaker_tsv",
                }
                print(f"{filepath}.{line}: speaker_tsv wrong line format {len(row)}")

            speakers.append(row[1])

    # return dict with all errors from file
    return wrong, speakers


def check_file(name: str) -> typing.List[dict]:
    """Check all files for one video"""

    errors = []

    wrong, speakers = check_speaker_tsv(name)
    errors.extend(wrong)
    errors.extend(check_name_tsv(name, get_len_from_meta(name), speakers))

    return errors


def check_if_file_exist(path: str) -> bool:
    """Check if file exist"""
    if os.path.exists(path):
        return False
    print(f'DOES NOT EXIST {path}')
    return True


if __name__ == "__main__":
    files = os.listdir(args.path)
    for file in files:
        if file.endswith(".meta.tsv"):
            file_name = ".".join(file.split(".")[:-2])

            # Check if all files for file exist
            if not sum(check_if_file_exist(p) for p in [os.path.join(args.path, file_name + '.speaker.tsv'),
                                                        os.path.join(args.path, file_name + '.tsv')]):
                check_file(file_name)
