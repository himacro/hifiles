for f in *.JPG 
    do new_fn=$(exiftool $f | grep 'Create Date' | sed 's/Create Date\s\+:/YiYi/' | sed 's/:/-/g')
    cp -v "$f" "$new_fn.JPG"
done
