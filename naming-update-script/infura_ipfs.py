# for wrapped directory add use
#
# curl -X POST -u "PROJECT_ID:PROJECT_SECRET" \
#   "https://ipfs.infura.io:5001/api/v0/add?wrap-with-directory=true" \
#    -H "Content-Type: multipart/form-data" -F file=@"0" -F file=@"1"
#
# to grep the files like the above use (note that this does not work with files that contain spaces)
# FILES=$(find * -type f | grep -v ' ' | sed -e 's/ /\\ /g' | awk -v q="'" '{print " -F " q "file=@\"" $0 "\";filename=\"" $0 "\"" q}')
#
# to mv multiple files: mv `ls | grep -E '[0-9]+'` meta/
