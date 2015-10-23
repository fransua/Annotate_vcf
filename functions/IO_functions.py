import sys
import bz2, gzip, zipfile, tarfile


def filenames2filehandles(filenames):
    filehandles = list()
    for filename in filenames:
        try:
            filehandles.append(magic_open(filename, "r"))
        except IOError:
            sys.exit("could not open file %s wrong input filename\n" % (filename))
    return(filehandles)

def magic_open(filename, mode = 'r', verbose=False):
    """
    To read uncompressed zip gzip bzip2 or tar.xx files

    :param filename: either a path to a file, or a file handler
    :param 'r' mode: opening mode 'r' or 'w'

    :returns: open file ready to be iterated
    """
    if isinstance(filename, str):
        fhandler = file(filename, mode + 'b')
        inputpath = True
        if tarfile.is_tarfile(filename):
            if verbose:
                print 'tar'
            thandler = tarfile.open(filename, mode)
            if len(thandler.members) != 1:
                raise NotImplementedError(
                    'Not exactly one file in this tar file.')
            return magic_open(thandler.extractfile(thandler.getnames()[0]),
                              mode)
    else:
        fhandler = filename
        filename = fhandler.name
        inputpath = False
        start_of_file = ''
    if inputpath:
        start_of_file = fhandler.read(1024)
        fhandler.seek(0)
    if start_of_file.startswith('\x50\x4b\x03\x04'):
        if verbose:
            print 'zip'
        zhandler = zipfile.ZipFile(fhandler, mode=mode)
        if len(zhandler.NameToInfo) != 1:
            raise NotImplementedError(
                'Not exactly one file in this zip file.')
        return zhandler.open(zhandler.NameToInfo.keys()[0], mode)
    if start_of_file.startswith('\x42\x5a\x68'):
        if verbose:
            print 'bz2'
        fhandler.close()
        return bz2.BZ2File(filename, mode)
    if start_of_file.startswith('\x1f\x8b\x08'):
        if verbose:
            print 'gz'
        return gzip.GzipFile(fileobj=fhandler)
    return fhandler
