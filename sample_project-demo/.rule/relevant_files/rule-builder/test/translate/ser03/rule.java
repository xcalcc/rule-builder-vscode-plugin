import io.xc5.RBC_ENGINE;

public class rule{
    public static void rule(){
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_begin("rule"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_start_state("start"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_final_state("end"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("start", "_ZN4java2io18ObjectOutputStreamC1EPNS0_12OutputStreamE", RBC_ENGINE.Get_this_pointer(), 1, "init", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("init", "_ZN4java2io18ObjectOutputStream11writeObjectEJvPNS_4lang6ObjectE", RBC_ENGINE.Get_this_pointer(), RBC_ENGINE.Not(RBC_ENGINE.Is_tag_attr_set(RBC_ENGINE.Get_arg(1),"sensitive","sanitize_data")), "END", "SER03"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("init", "_ZN4java2io18ObjectOutputStream11writeObjectEJvPNS_4lang6ObjectE", RBC_ENGINE.Get_this_pointer(), RBC_ENGINE.Is_tag_attr_set(RBC_ENGINE.Get_arg(1),"sensitive","sanitize_data"), "END", ""));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_end("rule"));
    }
}
