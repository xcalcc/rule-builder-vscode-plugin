import io.xc5.RBC_ENGINE;

public class CWE295{
    public static void CWE295(){
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_begin("CWE295"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_start_state("start"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_final_state("end"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("start", "_ZN3org6apache7commons4mail11SimpleEmailC1Ev", RBC_ENGINE.Get_this_pointer(), 1, "init", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("init", "_ZN3org6apache7commons4mail5Email15setSSLOnConnectEJPS3_b", RBC_ENGINE.Get_this_pointer(), RBC_ENGINE.Get_value(RBC_ENGINE.Get_arg(1)), "ssl_connect", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("ssl_connect", "_ZN3org6apache7commons4mail5Email25setSSLCheckServerIdentityEJPS3_b", RBC_ENGINE.Get_this_pointer(), RBC_ENGINE.Get_value(RBC_ENGINE.Get_arg(1)), "verified", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("verified", "_ZN3org6apache7commons4mail5Email4sendEJPN4java4lang6StringEv", RBC_ENGINE.Get_this_pointer(), 1, "end", ""));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("init", "_ZN3org6apache7commons4mail5Email4sendEJPN4java4lang6StringEv", RBC_ENGINE.Get_this_pointer(), 1, "end", "CWE295"));
       RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("ssl_connect", "_ZN3org6apache7commons4mail5Email4sendEJPN4java4lang6StringEv", RBC_ENGINE.Get_this_pointer(), 1, "end", "CWE295"));
        RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_end("CWE295"));
    }
}
