def save2mat(**kwargs):
    """Function to save a list of dictionaries with numpy arrays to a mat file."""
    from scipy.io import savemat

    # Get the input arguments.
    if "olist" in kwargs.keys():
        out_list = kwargs["olist"]
        if type(out_list) is not list:
            out_list = [out_list]
    else:
        raise Exception("!!! olist has not been specified. !!!")
    if "ofile" in kwargs.keys():
        out_file = kwargs["ofile"]
    else:
        raise Exception("!!! olist has not been specified. !!!")
    if "key" in kwargs.keys():
        key = kwargs["key"]
        if type(key) is not list:
            key = [key]
    else:
        raise Exception("!!! key has not been specified. !!!")

    # Loop over the list of dictionaries and save to a mat file.
    mdict = {}
    for i, data in enumerate(out_list):
        out = []
        extract_ndarray(data, out, [key[i]], mdict, 0)
    savemat(out_file, mdict=mdict)


def extract_ndarray(d, out, name, mdict, i):
    """Return flattened dictionary for ndarray."""
    if type(d) is dict:
        for k, v in d.items():
            name.append(k.__str__())
            if type(v) is dict:
                d_keys = list(v.keys())
                out.append([k, d_keys])
                extract_ndarray(v, out, name, mdict, i)
            else:
                i += 1
                kname = '_'.join(name)
                mdict[kname] = v
                del name[-1]
                if out:
                    if i == out[-1][1].__len__():
                        i = 0
                        del name[-1]
                pass
    return out


def depth(d):
    """Count the depth of a nested dictionary."""
    if not isinstance(d, dict) or not d:
        return 0
    else:
        return max(depth(v) for k, v in d.items()) + 1


def readmat(matfile):
    """Function to read mat file into dictionary and type."""
    import numpy as np
    import scipy.io

    # Load the mat file and create a dictionary structure.
    mat = scipy.io.loadmat(matfile)
    var_types = []
    var_dicts = []
    for k, v in mat.items():
        k_val = k.split('_')
        var_types.append(k_val[0])
        k_names = k_val[1:]
        if k_val[0] == 'pfile':
            var_dicts.append({int(k_names[0]): {int(k_names[1]): v}})
        else:
            print('!!! Skipping unidentified varaible name: %s' % k)
            var_types.pop()
    return var_types, var_dicts
