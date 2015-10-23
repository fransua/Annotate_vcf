import re

def get_metadata(file):
    metadata = []
    header="#NO HEADER\n"
    for line in file:
        if line.startswith('##'):
            metadata.append(line)
            continue
        if line.startswith('#'):
            header = line
        else:
            return metadata, header


