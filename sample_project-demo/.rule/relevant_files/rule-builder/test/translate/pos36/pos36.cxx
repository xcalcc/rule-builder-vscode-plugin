#include "stdio.h"
#include "rbc_base.h"
RBC_ENGINE rbc;
#ifdef __cplusplus
extern "C" {
#endif
    int pos36(void) {
       rbc.Model_decl(rbc.Fsm_build_begin("pos36"));
       rbc.Model_decl(rbc.Fsm_new_start_state("start"));
       rbc.Model_decl(rbc.Fsm_new_final_state("end"));
       rbc.Model_decl(rbc.Fsm_add_transition("start", "setuid", NULL, 1, "uid", ""));
       rbc.Model_decl(rbc.Fsm_add_transition("uid", "setgid", NULL, 1, "end", "POS36-C"));
       rbc.Model_decl(rbc.Fsm_build_end("pos36"));
    }
#ifdef __cplusplus
}
#endif
