import io.xc5.RBC_ENGINE;

public class SER03{
 public static void SER03(){
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_begin("SER03"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_start_state("start"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_final_state("end"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("start", "_ZN4java2io18ObjectOutputStreamC1EPNS0_12OutputStreamE", RBC_ENGINE.Get_this_pointer(), 1, "s1", ""));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s1", "_ZN4java2io18ObjectOutputStream11writeObjectEJvPNS_4lang6ObjectE", RBC_ENGINE.Get_this_pointer(), RBC_ENGINE.Not(RBC_ENGINE.Is_tag_attr_set(RBC_ENGINE.Get_arg(1), "sensitive", "sanitize_data")), "end", "SER03"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s1", "_ZN4java2io18ObjectOutputStream11writeObjectEJvPNS_4lang6ObjectE", RBC_ENGINE.Get_this_pointer(), RBC_ENGINE.Is_tag_attr_set(RBC_ENGINE.Get_arg(1), "sensitive", "sanitize_data"), "end", ""));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_end("SER03"));
  RBC_ENGINE.Rbc_declare_rule_info("SER03", "CUSTOM", "DEFAULT");
 }
}
