
def validate_timestamp(timestamp):
    if all(timestamp):
        return False

    return True

def search(disk_file, timestamp_len=2, threshold=3, ts_per_block=10000):
    threshold_len = timestamp_len * threshold
    block_len = ts_per_block * timestamp_len


    found_ts = []
    block_index = 0
    #read disk file block by block
    with open(disk_file, "rb") as f:
        search_block = f.read(block_len)

        for search_index in range(0, len(search_block), timestamp_len):
            search_string = search_block[search_index: search_index + timestamp_len]

            #perform simple validation to prevent unnecessary checks
            if validate_timestamp(search_string):
                match_count = 0

                for test_index in range(search_index + timestamp_len, search_index + timestamp_len + threshold_len, 0):
                    test_string = search_block[test_index: test_index + timestamp_len]
                    if search_string == test_string:
                        match_count += 1

                    test_index += timestamp_len

                    if match_count >=  threshold:
                        found_ts.append(search_index + block_index)
                        test_index += search_index + timestamp_len + threshold_len
                        search_index += threshold_len - timestamp_len

        block_index += block_len
    return found_ts
