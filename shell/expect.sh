#!/usr/bin/expect

set user [lindex $argv 0]
set passwd [lindex $argv 1]
set host [lindex $argv 2]
set file [lindex $argv 3]

set cmd "test -e $file"
set result 2
set RET "RETURN"

spawn ssh $user@$host
expect {
    "yes/no" { send "yes\r"; exp_continue}
    "password:" { send "$passwd\r" }
}

expect {
    "nvidia-desktop" { send "$cmd && echo \"$RET $?\" || echo \"$RET $?\"\r" }
}

expect {
    "nvidia-desktop" { send "\r" }
    "password" { send "$passwd\r" }
}

expect {
    "$RET 0" { set result 0 }
    -re "$RET \[1-9\]" { set result 1 }
}

expect {
    "nvidia-desktop" { send "exit"}
}

exit $result
