#include <stdio.h>
#include <unistd.h>

void func(){
    int uid_stat = setuid(getuid());
    int gid_stat = setgid(getfid());
}
