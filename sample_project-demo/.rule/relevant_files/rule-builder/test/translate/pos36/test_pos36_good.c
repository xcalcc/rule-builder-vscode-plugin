#include <stdio.h>
#include <unistd.h>

void func() {
    int gid_stat = setgid(getgid());
    int uid_stat = setuid(getuid());
}