#!/bin/bash

if [ $# -ne 4 ];then
 printf "usage: $0 <element> <outdir> <oper list> <inc json>\n"
 exit 1
fi

home=$(pwd)/

element=$1
outdir=$2
operlis=$3
inc_json=$4

printf "\nscript:\t\t$0\n"
printf 'inputs:\n'
printf "\telement:\t\t$element\n"
printf "\toutdir:\t\t\t$outdir\n"
printf "\toperlis:\t\t$operlis\n"
printf "\tinc_json:\t\t$inc_json\n"

# Make the inc output dir and create the jobs to run
mkdir -p $outdir
cd $outdir

pbs=make_inc.pbs

printf "#PBS -m bae -A AE_H1_A240\n">$pbs
printf "#PBS -N make_inc -j eo -e make_inc.cpr\n">>$pbs
printf "#PBS -lselect=1:ncpus=1:mem=2gb\n">>$pbs
printf "#PBS -l walltime=2:00:00 -W umask=007\n">>$pbs
printf "#PBS -l place=shared\n">>$pbs
printf "#!/bin/bash\n">>$pbs
printf "set -x\n\n">>$pbs

printf 'cd $PBS_O_WORKDIR\n\n'>>$pbs

printf "element=$element\n">>$pbs
printf "home=$home\n">>$pbs
printf "operlis=$operlis\n">>$pbs
printf "inc_json=$inc_json\n">>$pbs
printf "outdir=${home}${outdir}/\n\n">>$pbs

printf 'cd $TMPDIR\n\n'>>$pbs

printf "# Copy and untar the PLOs\n">>$pbs
printf 'tar -kxzvf ${home}PLO.tar.gz -C .\n\n'>>$pbs

printf "# Make the PLO set list files\n">>$pbs
printf "rm -f plosets.lis 2>/dev/null\n">>$pbs
printf 'for oper in $(cat $operlis)\n'>>$pbs
printf "do\n">>$pbs
printf 'ls *${oper}.PLO >ploset_${oper}.lis\n'>>$pbs
printf 'echo ploset_${oper}.lis >>plosets.lis\n'>>$pbs
printf "done\n\n">>$pbs

printf "# Make the inc files\n">>$pbs
printf 'python3.6 /project/issloads/PyLnD/thermal/scripts/make_inc.py $element $inc_json $operlis plosets.lis\n\n'>>$pbs

printf '# Copy back the inputs\n'>>$pbs
printf 'cp -p $operlis .\n'>>$pbs
printf 'cp -p $inc_json .\n'>>$pbs
printf 'tar -czvf ${outdir}inputs.tar.gz *.lis *.json\n\n'>>$pbs

printf '# Copy back the results\n'>>$pbs
printf 'cp *.inc $outdir\n\n'>>$pbs

printf 'cd $PBS_0_WORKDIR\n\n'>>$pbs

printf 'rm -rf $TMPDIR\n\n'>>$pbs

printf 'jcost\n'>>$pbs

printf 'outputs:\n'
printf "\tpbs:\t\t\t$outdir/$pbs\n"
