import sys

# if all bytes are the same we likely aren't reading metadata
# TODO more accurate / faster validation


def is_metadata(timestamp):
    last_e = timestamp[0]

    for e in timestamp:
        if e != last_e:
            return True

        last_e = e

    return False


def search(disk_file, timestamp_len=2, threshold=3, ts_per_block=10000):
    """
    reads a disk file looking for repeated timestamps

    breaks large disks into blocks so the whole disk isn't in memory at once

    :param disk_file: file path to disk
    :param timestamp_len: the length in bytes of timestamp you are looking for
    :param threshold: the number timestamp length blocks to be searched after the selected timestamp
    :param ts_per_block: the size of the blocks read from the file
    :return: array of indexes belonging to time stamps that were found to be repeated
    """
    threshold_len = timestamp_len * threshold
    block_len = ts_per_block * timestamp_len


    found_ts = []
    block_index = 0
    # read disk file block by block
    with open(disk_file, "rb") as f:
        search_block = f.read(block_len)

        for search_index in range(0, len(search_block), timestamp_len):
            search_string = search_block[search_index: search_index + timestamp_len]

            # perform simple validation to prevent unnecessary checks
            if is_metadata(search_string):
                match_count = 0

                test_index = search_index + timestamp_len

                while test_index < search_index + timestamp_len + threshold_len:
                    test_string = search_block[test_index: test_index + timestamp_len]
                    if search_string == test_string:
                        match_count += 1

                    test_index += timestamp_len

                    if match_count >= threshold:
                        print("index:{}\n\ttext:{}\n\tmatches:{}".format(search_index, search_string, match_count))
                        found_ts.append(search_index + block_index)
                        test_index += search_index + timestamp_len + threshold_len
                        search_index += threshold_len - timestamp_len

        block_index += block_len
    return found_ts


def main(argv):
    print(search(argv[0]))


if __name__ == "__main__":
    main(sys.argv[1:])