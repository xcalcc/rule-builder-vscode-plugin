import io.xc5.RBC_ENGINE;

public class FILECROSS2{
 public static void FILECROSS2(){
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_begin("FILECROSS2"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_start_state("start"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_new_final_state("end"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("start", "_ZN8ssd_safe3AppC1Ev", RBC_ENGINE.Get_this_pointer(), 1, "s1", ""));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s1", "_ZN8ssd_safe9riskAudit8checkOutEJvPN4java4lang6StringE", RBC_ENGINE.Get_this_pointer(), 1, "s2", ""));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s2", "_ZN8ssd_safe14checkSystemErr12println2CharEJvP6JArrayIcEi", RBC_ENGINE.Get_this_pointer(), 1, "end", ""));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_add_transition("s1", "_ZN8ssd_safe14checkSystemErr12println2CharEJvP6JArrayIcEi", RBC_ENGINE.Get_this_pointer(), 1, "end", "FILECROSS2"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_set_default_action("s1", "FILECROSS2"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_set_default_action("s2", "FILECROSS2"));
  RBC_ENGINE.Model_decl(RBC_ENGINE.Fsm_build_end("FILECROSS2"));
  RBC_ENGINE.Rbc_declare_rule_info("FILECROSS2", "CUSTOM", "DEFAULT");
 }
}
