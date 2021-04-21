#!/usr/bin/expect

set timeout 360


# files that dont exist

#110
#120
#124
#
#204
#206
#211
#216
#218
#224
#225
#226
#227
#228
#229
###


# need to use Tcl syntax for the for loop, not shell syntax
for {set i 100} {$i < 235} {incr i} {

    if {($i == 110) || ($i == 120) || ($i == 204) || ($i == 206) || ($i == 211) || ($i == 216) || ($i == 218)} {
        continue
    }
     if {$i == 125} {
         set i 199
        continue
    }
    if {$i == 224} {
        set i 229
        continue
    }
   

    spawn xform -i ${i} -s 0 -n ${i}_alt
  
    expect "Output*" {send "125\n"}
    expect "Specify*" {send "\n"}
    expect "Choose*" {send "\n"}
    expect " Signal*" {send "\n"}
    expect " Signal*" {send "\n"}
    expect " Signal*" {send "\n"}
    expect " Signal*" {send "\n"}
}