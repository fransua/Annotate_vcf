##IO_FUNCTIONS:

  magic_open --> François Serra, open a compressed file
  	Input: Filepath
	Return: Filehandle

  filenames2filehandles --> Apply magic_open to a list of filenames.

##vcf_functions:
  get_metadata --> Fetch metadata and header line from a vcf file
	Input: Filehandle
	Return: metadata, header
 
