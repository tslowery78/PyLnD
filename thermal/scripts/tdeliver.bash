#!/ots/sw/osstoolkit/15.2/sles11-x86_64/bin/bash

# Functions

usage () {
echo "Usage: $0 [run type: s0run] [delivery dir] [list of sources]"
exit 1
}

checkdir () {
if [ ! -d $1 ];then
    echo "Directory does not exist:  $1"
    exit 1
fi
}

combine () {
# Function to combine the requested outreqs.

# Make the location list.
rm -f $outdir${rtype}_loc.lis 2>/dev/null
for loc in "${indirs[@]}"; do
    echo $hpath$loc/$rtype/ >>$outdir${rtype}_loc.lis
done

# Loop over each delivery type if exists, find txt files, make combo script and execute.

# Make a list of all expected txt/TXT files.
checkdir ${indirs[0]}/$rtype
cd ${indirs[0]}/$rtype
otypes=
for txt_dir in "${ot[@]}"; do
    if [ -d $txt_dir ];then
        otypes="${otypes} $txt_dir"
    	cd $txt_dir
    	ls *.txt *TXT >$outdir$txt_dir.lis
	cd ../
    fi
done

# Create the combo script.
echo '#!/ots/sw/osstoolkit/15.2/sles11-x86_64/bin/bash

if [ $# -eq 0 ];then
    echo "Usage: $0 [type list: cbar_forces.lis] [loc list: p3run_loc.lis]"
    exit 1
fi

txtlist=$1
loclist=$2
otype=$(echo $txtlist|awk -F. '"'"'{print $1}'"'"')
rm -rf $otype
mkdir -p $otype
cd $otype

# Cat all txt files together in the order of the loc list.
for txt in $(cat ../$txtlist); do
    echo "Combining $otype/$txt in $loclist"
    for loc in $(cat ../$loclist); do
        if [ -f $txt ];then
	    cat $txt $loc$otype/$txt >$$ && mv $$ $txt
	else
	    cat $loc$otype/$txt >$txt
	fi
    done
done' >${outdir}cold_hot_cat.bash

# Execute the script for each output type.
cd $outdir
for ot in $(echo $otypes); do
    bash cold_hot_cat.bash $ot.lis ${rtype}_loc.lis 
done

cd $hpath

}

# End Functions

if [ $# -eq 0 ];then
    usage
fi

# Get the inputs.
i=1; idx=0
for arg in "$@"; do
    if [ $i == 1 ];then
        rtype=$arg
    elif [ $i == 2 ];then
        ddir=$arg
    else
        indirs[$idx]=$arg
        checkdir ${indirs[$idx]}/$rtype
	idx=$(($idx+1))
    fi
    i=$(($i+1))
done

# Customize delivery for the current run type.
case "$rtype" in
 node1run|pma?run|z1run|bga??run|?1run|??pvr?run|alrun|labrun|?4run|?6lsrun|?6iearun|??fp?run|elc?run|?3run)
 	scav=1
	;;
 s0run)
	scav=1
	s0flag=1
	;;
 mtrun)
	mtflag=1
	;;
 ?5run)
 	scav=1
 	flag5=1
	;;
esac

# Create output directory.
hpath=$(pwd)/
outdir=$hpath$ddir/$rtype/
mkdir -p $outdir

# Combine and deliver the scavenger run results.
if [ ! -z $scav ];then
# Define the different types of scavenger outreqs.
    ot[0]=cbar_forces
    ot[1]=cbeam_forces
    ot[2]=cquad_forces
    ot[3]=cbar_stresses
    ot[4]=cbeam_streses
    ot[5]=cquad_stresses
    ot[6]=ang_cquad_stresses
    ot[7]=chexa_stresses
    ot[8]=celas2_forces
    ot[9]=gp_forces
    combine
fi

if [ ! -z $s0flag ];then
# Define the s0 delivery types of outreqs.
 ot=
 ot[0]=mt_rail
 ot[1]=ssas_float
 ot[2]=mts_fittings
 ot[3]=mts_struts
 ot[4]=ssas_loads
 combine
fi

if [ ! -z $mtflag ];then
# Define the s0 delivery types of outreqs.
 ot=
 ot[0]=mt_defls
 combine
fi

if [ ! -z $flag5 ];then
# Define the p5/s5 delivery types of outreqs.
 ot=
 ot[0]=rtas_56
 ot[1]=mrtas_45
 combine
fi


