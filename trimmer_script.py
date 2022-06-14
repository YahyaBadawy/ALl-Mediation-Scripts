cd /Backup/Decoder/SDP/out
mkdir -p TEMP
zcat ASCII*  > TEMP/tmp.orig
mv  `find . -name "ASCII*"  -mmin +10 -exec ls {} \;`  old
cd TEMP
csplit tmp.orig \--prefix='tmp.' --suffix-format='%010d'\  /SDPCallDataRecord/ {*}
rm -f tmp.orig
/usr/bin/grep  "subscriberNumber : \"$1\"" * | awk '{print $1}' > tmp.file_name
>FINAL
for i in `cat tmp.file_name` ; do cat  "$i ">> FINAL ;done
find . -type f -name "tmp*" -exec rm {} \;
cp FINAL /Backup/faisal/SDP
