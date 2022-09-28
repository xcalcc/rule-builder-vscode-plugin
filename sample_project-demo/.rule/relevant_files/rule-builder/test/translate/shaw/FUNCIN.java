import io.xc5.RBC_ENGINE;

public class FUNCIN{
    public static void FUNCIN(){
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_begin("FUNCIN"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_start_state("start"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_final_state("end"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("start", "_ZN8ssd_safe3AppC1Ev", RBC_ENGINE.Get_this_pointer(), 1, "init", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("init", "_ZN8ssd_safe3App14checkNonssdataEJvv", RBC_ENGINE.Get_this_pointer(), 1, "state1", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("state1", "_ZN8ssd_safe3App11checkSsdataEJvv", RBC_ENGINE.Get_this_pointer(), 1, "end", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("init", "_ZN8ssd_safe3App11checkSsdataEJvv", RBC_ENGINE.Get_this_pointer(), 1, "end", "FUNCIN"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_set_default_action("init", "FUNCIN"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_set_default_action("state1", "FUNCIN"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_end("FUNCIN"));
    }
}
