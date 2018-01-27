#!/bin/bash
#
#
#
#


if [ ! -d "design" ]
then
    echo "Please run this from the project root"
    exit
fi

mkdir -p gui/forms

init=gui/forms/__init__.py
temp=gui/forms/scratch
rm -f $init $temp
echo "# This file auto-generated by build_ui.sh. Don't edit." > $init
echo "__all__ = [" >> $init

echo "Generating forms.."
for i in design/*.ui
do
    base=$(basename $i .ui)
    py="gui/forms/${base}.py"
    echo " \"$base\"," >> $init
    echo "from . import $base" >> $temp
    if [ $i -nt $py ]; then
        echo " * "$py
        pyuic5 --from-imports $i -o $py
    fi
done

echo "]" >> $init
cat $temp >> $init
rm $temp

echo "Building resources.."
pyrcc5 design/icons.qrc -o gui/forms/icons_rc.py
pyrcc5 design/textbooks.qrc -o gui/forms/textbooks_rc.py