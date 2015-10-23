import re
import sys, os
import argparse
import bz2, gzip, zipfile, tarfile
import functions.IO_functions as IO_functions
import functions.vcf_functions as vcf_functions



def main():
    options = get_options()
    

    #Open files and merge headers
    try:
        main_file = IO_functions.magic_open(options.input_filename, 'r')
    except IOError:
        sys.exit('Could not open main vcf file to annotate %s check option %s'
                 % (options.input_filename, options.input_filename))

    try:
        output_file = open(options.output_filename, 'w')
    except IOError:
        sys.exit('Could not open output file %s for some reason, check path'
                 % (options.output_filename))

    list_of_handles = IO_functions.filenames2filehandles(options.db_list)


    main_metadata, main_header = vcf_functions.get_metadata(main_file)



    if options.merge_headers :
        for annotate_filehandle in list_of_handles:
            annotate_metadata, annotate_header = vcf_functions.get_metadata(annotate_filehandle)    
            main_metadata = main_metadata + annotate_metadata

    #Avoid duplicate metadata in output file.
    i=0
    while i < (len(main_metadata)-1): 
        if main_metadata[i] not in main_metadata[0:i]:
            output_file.write(main_metadata[i])
        i=i+1

    output_file.write(main_header)

    for file in list_of_handles:
        file.close()
    main_file.close()
    try:
        main_file = IO_functions.magic_open(options.input_filename, 'r')
    except IOError:
        sys.exit('Could not open main vcf file to annotate %s check option %s'
                 % (options.input_filename, options.input_filename))

    list_of_handles = IO_functions.filenames2filehandles(options.db_list)


    #Now we have n vcfs, need to join them
    for main_line in main_file:
        main_line.rstrip()
        if not main_line.startswith('#'):
            main_line_list = main_line.split('\t')
            main_pos = int(main_line_list[1])
            for fhandler in list_of_handles:
                while True:
                    try:
                        # te quito la funcion porque implica que hagas 6 tests en vez de 3
                        annotate_line_list = fhandler.next().split('\t')
                        if not annotate_line_list[0].startswith('#'):
                            annotate_pos = int(annotate_line_list[1])
                            if main_pos > annotate_pos:
                                continue
                            elif main_pos < annotate_pos:
                                break
                            else:
                            # Any of ALT alleles matches ANY of ALT alleles (because of multiallelic)
				
                                if bool(set(annotate_line_list[4].split(',')) & set(main_line_list[4].split(','))):
                                    if main_line_list[3] == annotate_line_list[3]:
	                                main_line_list[2] = main_line_list[2] + ';' + annotate_line_list[2].rstrip()
            	                        # esto nunca lo necesita en el ejemplo que me distes...
                                        main_line_list[7] = main_line_list[7] + ';' +annotate_line_list[7].rstrip()
                                        main_line_list[2] = re.sub('^.;', '', main_line_list[2])
                                        main_line_list[7] = re.sub('^.;', '', main_line_list[7])
                                        break
                        else:
                            continue
                    except StopIteration:
                        fhandler.close()
                        list_of_handles.remove(fhandler)
                        break
         
            output_file.write(('\t'.join(main_line_list)).rstrip()+'\n')

def valid_db_file(arg):
    if not os.path.isfile(arg):
        raise IOError('The db file %s does not exist!' % arg)
    else:
        return arg
    
def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output',
                        dest='output_filename',
                        default='out',
                        )
    parser.add_argument('-i', '--input',
                        dest='input_filename',
                        default='inp',
                        )
    parser.add_argument('-d', '--db_list', nargs='+', dest= 'db_list',
                        required=True, metavar='FILE',
                        type=str)
    parser.add_argument('-m', '--merge_headers', dest = 'merge_headers',
                        required = False, default = True)
                       
    options = parser.parse_args()
    
    return options


if __name__ == "__main__":
    exit(main())
