def read_op4_phi(msfile):
    """Function to read a NASTRAN op4 file into numpy array.

    \tMSC Nastran 2012.2 DMAP Programmer's Guide: OUTPUT4 page 1243
    """
    import numpy as np

    # Read through the binary op4 words to find data.
    with open(msfile, 'r') as f:
        [bytes_in_record] = np.fromfile(f, dtype=np.int32, count=1)
        if bytes_in_record == 8:    # Slightly different format for plm.f12
            [num_cols, num_rows] = np.fromfile(f, dtype=np.int32, count=2)
            [bytes_in_record_end] = np.fromfile(f, dtype=np.int32, count=1)
            matrix_name = 'DIS'
        elif bytes_in_record == 24: # NASTRAN f12
            [num_cols, num_rows, matrix_form, matrix_type] = np.fromfile(f, dtype=np.int32, count=4)
            matrix_name = np.fromfile(f, dtype=np.int8, count=8)
            matrix_name = ''.join([chr(item) for item in matrix_name]).strip()
            [bytes_in_record_end] = np.fromfile(f, dtype=np.int32, count=1)
        phi = np.zeros([num_rows, num_cols])
        # For each row read and save matrix.
        for i in range(0, num_cols):
            [bytes_in_record, i_col, i_row, num_words] = np.fromfile(f, dtype=np.int32, count=4)
            phi[i_row - 1:num_words, i_col - 1] = np.fromfile(f, dtype=np.float32, count=num_words)
            [bytes_in_record_end] = np.fromfile(f, dtype=np.int32, count=1)
    return matrix_name, phi
