import re
import sys
import optparse
import gzip


parser = optparse.OptionParser()
parser.add_option('-o', '--output',
                                    dest="output_filename",
                                    default="default.out",
                                    )
parser.add_option('-i', '--input',
                                    dest= "input_filename",
                                    )
parser.add_option('-d', '--db_list',
                                    dest="db_list",
                                    default="default.db_list",
                                    )
parser.add_option('-c', '--column_number',
                                    dest="column_number",
                                    default = 8,
                                    )




options, remainder = parser.parse_args()
list_of_files = options.db_list.split(",")
column_to_join = int(options.column_number) - 1
def compare_positions(pos_a,pos_b):
    if pos_a > pos_b:
        return(0)
    elif pos_a < pos_b:
        return(1)
    else:
        return(2)

def remove_col(list_to_remove,column_number):
    col_cont=0
    to_return_list = list()
    while col_cont < column_number:
        to_return_list.append(list_to_remove[col_cont])
        col_cont = col_cont+1
    col_cont = col_cont+1
    while col_cont < len(list_to_remove):
        to_return_list.append(list_to_remove[col_cont])
        col_cont=col_cont+1
    return(to_return_list)


#Open files and merge headers
if str(options.input_filename)[len(str(options.input_filename))-2:len(str(options.input_filename))] == "gz":
    try:
        file_a = gzip.open(options.input_filename,"r")
    except:
        sys.exit("Could not open main vcf file to annotate " + options.input_filename + "check option " + options.input_filename)
else:
    try:
        file_a = open(options.input_filename,"r")
    except:
        sys.exit("Could not open main vcf file to annotate " + options.input_filename + " check option " +options.input_filename)

try:
    output_file = open(options.output_filename,"w")
except:
    sys.exit("Could not open output file " + options.output_filename +" for some reason, check output file")
list_of_handles = list()
list_of_lines = list()

for a in list_of_files:
    if str(a)[len(a)-2:len(a)] == "gz":
        try:
            list_of_handles.append(gzip.open(a,"r"))
        except:
            sys.exit("could not open gzipped file " +a +" wrong input filename\n")
    else:
        try:
            list_of_handles.append(open(a,"r"))
        except:
            sys.exit("could not open file plain texplain text" + a +" wrong input filename\n")

for a in list_of_handles:
    list_of_lines.append(a.readline())


metadata_a = list()
line_a = file_a.readline()
while line_a[0:2]=="##":
    metadata_a.append(line_a)
    line_a =file_a.readline()
if line_a[0] == "#":
    header_a = line_a

file_counter=0
while file_counter < len(list_of_files):
    while list_of_lines[file_counter][0:2] =="##":
        metadata_a.append(list_of_lines[file_counter])
        list_of_lines[file_counter] = list_of_handles[file_counter].readline()
    file_counter=file_counter+1

for a in metadata_a:
    output_file.write(a)
try:
    output_file.write(header_a)
except:
    #VCF_has_no_header
    output_file.write("#NO HEADER\n")


file_counter=0
list_of_lines_as_lists = list()
while file_counter < len(list_of_files):
    list_of_lines_as_lists.append(list_of_handles[file_counter].readline().split("\t"))
    file_counter = file_counter+1
#Now we have n vcfs, need to join them



for line_a in file_a:
    line_a_as_list = line_a.split("\t")
    file_counter=0
    while file_counter < len(list_of_files):
        if list_of_lines_as_lists[file_counter][0] == '':
            list_of_files =remove_col(list_of_files,file_counter)
            list_of_lines_as_lists = remove_col(list_of_lines_as_lists,file_counter)
            list_of_handles[file_counter].close()
            list_of_handles = remove_col(list_of_handles,file_counter)
        else:
            compare_value=compare_positions(line_a_as_list[1],list_of_lines_as_lists[file_counter][1])
            if compare_value == 0:
                list_of_lines_as_lists[file_counter] = list_of_handles[file_counter].readline().split("\t")
            elif compare_value ==1:
                file_counter = file_counter +1
            elif compare_value == 2:
                if line_a_as_list[4] == list_of_lines_as_lists[file_counter][4]:
                    line_a_as_list[column_to_join] = line_a_as_list[column_to_join]+";"+list_of_lines_as_lists[file_counter][column_to_join]
                    line_a_as_list[2] =re.subn("^.;","",line_a_as_list[2])[0]
                    line_a = "\t".join(line_a_as_list)
                    list_of_lines_as_lists[file_counter] = list_of_handles[file_counter].readline().split("\t")
                else:
                    list_of_lines_as_lists[file_counter] = list_of_handles[file_counter].readline().split("\t")
    output_file.write(line_a)



