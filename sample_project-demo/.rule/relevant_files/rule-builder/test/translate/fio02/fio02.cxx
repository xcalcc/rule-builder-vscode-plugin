 #include "stdio.h"
 #include "rbc_base.h"
 #ifdef __cplusplus
extern "C" {
 #endif
RBC_ENGINE rbc;
        FILE* fopen(const char* arg1, const char* arg2){
            rbc.Rbc_assert(rbc.Not(rbc.Is_parm_tainted(rbc.Get_arg(1))), "FIO02-C");
            return NULL;
        }
 #ifdef __cplusplus
}
 #endif
