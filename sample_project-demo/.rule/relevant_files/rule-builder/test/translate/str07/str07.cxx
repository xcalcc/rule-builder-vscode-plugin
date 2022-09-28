 #include "stdio.h"
 #include "rbc_base.h"
 #ifdef __cplusplus
extern "C" {
 #endif
RBC_ENGINE rbc;
        char* strcpy(char* arg1, const char* arg2){
            rbc.Rbc_assert(rbc.Do_not_get_called(), "STR07-C");
            return NULL;
        }
        char* strcat(char* arg1, const char* arg2){
            rbc.Rbc_assert(rbc.Do_not_get_called(), "STR07-C");
            return NULL;
        }
        char* strncpy(char* arg1, const char* arg2, size_t arg3){
            rbc.Rbc_assert(rbc.Do_not_get_called(), "STR07-C");
            return NULL;
        }
        char* strncat(char* arg1, const char* arg2, size_t arg3){
            rbc.Rbc_assert(rbc.Do_not_get_called(), "STR07-C");
            return NULL;
        }
 #ifdef __cplusplus
}
 #endif
