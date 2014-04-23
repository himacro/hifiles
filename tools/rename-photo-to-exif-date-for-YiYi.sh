for f in *.JPG;
do 
    new_fn=$(exiftool $f | grep 'Create Date' | sed 's/Create Date\s\+:/YiYi/' | sed 's/:/-/g')
    if [[ -e ${new_fn}.JPG ]]
    then
        new_fn=${new_fn}-2
    fi
    cp -v "$f" "$new_fn.JPG"
done
