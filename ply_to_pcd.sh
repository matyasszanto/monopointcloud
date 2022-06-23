#!/bin/bash

for f in *.ply;
do
  echo $f
  space=" "
  len=${#f}
  name=${f:0:$len-4}
  pcd=".pcd"
  str="$f$space$name$pcd"
  pcl_ply2pcd $str
done

