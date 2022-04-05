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

def is_match(search_string,  test_string, prefix_len = 0):
    search_check  = int.from_bytes(search_string, 'little')
    test_check = int.from_bytes(test_string, 'little')

    compare = search_check ^ test_check
    suffix = compare >> 8 * prefix_len
    return len(search_string) == len(test_string) and\
           len(search_string) > prefix_len and\
           suffix == 0



def search(disk_file, timestamp_len=2, threshold=2, ts_per_block=10000, prefix_len=0, window=6):
    """
    reads a disk file looking for repeated timestamps

    breaks large disks into blocks so the whole disk isn't in memory at once

    :param disk_file: file path to disk
    :param timestamp_len: the length in bytes of timestamp you are looking for
    :param threshold: the number of timestamp matches to indicate metadata found
    :param ts_per_block: the size of the blocks read from the file
    :return: array of indexes belonging to time stamps that were found to be repeated
    :param prefix_len: the number of prefix bytes to ignore in timestamps
    :param window: the number timestamp length blocks to be searched after the selected timestamp
    """
    window_len = timestamp_len * window
    block_len = ts_per_block * timestamp_len


    found_ts = []
    block_index = 0
    # read disk file block by block
    with open(disk_file, "rb") as f:

        search_block = f.read(block_len)
        while search_block:
            for search_index in range(0, len(search_block), timestamp_len):
                search_string = search_block[search_index: search_index + timestamp_len]

                # perform simple validation to prevent unnecessary checks
                if is_metadata(search_string):
                    match_count = 0

                    test_index = search_index + timestamp_len

                    while test_index < search_index + timestamp_len + window_len:
                        test_string = search_block[test_index: test_index + timestamp_len]
                        if is_match(search_string, test_string, prefix_len):
                            match_count += 1


                        if match_count >= threshold:
                            print("index:{}\n\ttext:{}\n\tmatches:{}\n\tlast match index:{}\n\tlast match text:{}"\
                                  .format(search_index, search_string, match_count, test_index, test_string))
                            found_ts.append(search_index + block_index)
                            test_index += search_index + timestamp_len + window_len
                            search_index += window_len - timestamp_len

                        test_index += timestamp_len
            search_block = f.read(block_len)
            block_index += block_len
    return found_ts


def main(argv):
    print('positive test prefix match:{}'.format(is_match(b'\xFF\xFF\xFF', b'\xAA\xAA\xFF', 2)))
    print('negative test prefix match:{}'.format(is_match(b'\xFF\xFF\xFF', b'\xAA\xAA\xAA', 2)))

    print('positive test generic match:{}'.format(is_match(b'\xAA\xFF', b'\xAA\xFF', 0)))
    print('negative test generic match:{}'.format(is_match(b'\xAA\xFF', b'\xAA\xAA', 0)))

    print(search(argv[0]))


if __name__ == "__main__":
    main(sys.argv[1:])