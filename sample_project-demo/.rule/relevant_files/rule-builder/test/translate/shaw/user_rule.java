import io.xc5.RBC_ENGINE;

public class user_rule{
    public static void user_rule(){
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_begin("user_rule"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_start_state("start"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_final_state("end"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("start", "_ZN8ssd_safe3AppC1Ev", RBC_ENGINE.Get_this_pointer(), 1, "s1", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s1", "_ZN8ssd_safe3App8readssd2EJPN4java4lang6StringES4_", RBC_ENGINE.Get_this_pointer(), 1, "s2", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s2", "_ZN8ssd_safe3App8readssd2EJPN4java4lang6StringES4_", RBC_ENGINE.Get_this_pointer(), 1, "s2", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s2", "_ZN8ssd_safe3App14checkNonssdataEJvv", RBC_ENGINE.Get_this_pointer(), 1, "s3", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s1", "_ZN8ssd_safe3App14checkNonssdataEJvv", RBC_ENGINE.Get_this_pointer(), 1, "s4", "URULE01"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("start", "_ZN8ssd_safe3App8readssd2EJPN4java4lang6StringES4_", RBC_ENGINE.Get_this_pointer(), RBC_ENGINE.Not(RBC_ENGINE.Pre_call("_ZN8ssd_safe3AppC1Ev")), "s5", "URULE04"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("start", "_ZN8ssd_safe3App14checkNonssdataEJvv", RBC_ENGINE.Get_this_pointer(), RBC_ENGINE.Not(RBC_ENGINE.Pre_call("_ZN8ssd_safe3AppC1Ev")), "s6", "URULE05"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_set_default_action("s1", "URULE02"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_set_default_action("s2", "URULE03"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_end("user_rule"));
    }
}
