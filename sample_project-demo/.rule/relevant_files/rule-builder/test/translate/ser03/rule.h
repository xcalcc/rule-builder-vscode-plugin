#ifdef LANG_JAVA
#define PACKAGE(X) package X;
#define IMPORT1 import io.xc5.RBC_ENGINE;
#define IMPORT2
#define CLASS(x) public class x{
#define INTERFACE(X) public interface X{
#define END_CLASS }
#define START_RULE(x) public static void x(){
#define END_RULE }
#define ENGINE RBC_ENGINE
#define DECLARE(x) ENGINE.Model_decl(x)
#else // C or __cplusplus
#define PACKAGE(X)
#define IMPORT1 #include "sys_base.h"
#define IMPORT2 #include "rbc_base.h"
#define CLASS(x) RBC_ENGINE rbc;
#define INTERFACE(X) 
#define END_CLASS
#define START_RULE(x) int x(void) {
#define END_RULE }
#define ENGINE rbc
#define DECLARE(X) ENGINE.Model_decl(X)
#endif
#define FUNC_SIG(W,X,Y) W X Y{
#define BUILD_BEGIN(X) DECLARE(ENGINE.Fsm_build_begin(X));
#define NEW_START_STATE DECLARE(ENGINE.Fsm_new_start_state("start"));
#define NEW_FINAL_STATE DECLARE(ENGINE.Fsm_new_final_state("end"));
#define BUILD_END(X) DECLARE(ENGINE.Fsm_build_end(X));
#define RULE_INFO(X,Y) ENGINE.Rbc_declare_rule_info(X, "CUSTOM", Y);
#define DECLARE_RULE_INFO(X,Y,Z) ENGINE.Rbc_declare_rule_info(X, Y, Z);
#define THIS_POINTER ENGINE.Get_this_pointer()
#define GET_RET ENGINE.Get_ret()
#define GET_VALUE(X) ENGINE.Get_value(X)
#define GET_ARG(X) ENGINE.Get_arg(X)
#define NOT(X) ENGINE.Not(X)
#define ADD_TRANSITION(U,V,W,X,Y,Z) DECLARE(ENGINE.Fsm_add_transition(U, V, W, X, Y, Z));
#define SET_DEFAULT_ACTION(X,Y) DECLARE(ENGINE.Fsm_set_default_action(X, Y));
#define IS_SENSITIVE_DATA(X) ENGINE.Is_tag_attr_set(GET_ARG(X), "sensitive", "sanitize_data")
#define RBC_ASSERT(X,Y) ENGINE.Rbc_assert(X, Y)
#define RBC_SET_TAG(X,Y) DECLARE(ENGINE.Set_tag(X, Y))
#define RBC_IS_TAG_ATTR_SET(X,Y,Z) ENGINE.Is_tag_attr_set(X,Y,Z)
IMPORT1
IMPORT2
CLASS(SER03)
    START_RULE(SER03)
        BUILD_BEGIN("SER03")
        NEW_START_STATE
        NEW_FINAL_STATE
       ADD_TRANSITION("start","_ZN4java2io18ObjectOutputStreamC1EPNS0_12OutputStreamE",THIS_POINTER,1,"init","")
       ADD_TRANSITION("init","_ZN4java2io18ObjectOutputStream11writeObjectEJvPNS_4lang6ObjectE",THIS_POINTER,NOT(RBC_IS_TAG_ATTR_SET(GET_ARG(1),"sensitive","sanitize_data")),"end","SER03")
       ADD_TRANSITION("init","_ZN4java2io18ObjectOutputStream11writeObjectEJvPNS_4lang6ObjectE",THIS_POINTER,RBC_IS_TAG_ATTR_SET(GET_ARG(1), "sensitive", "sanitize_data"),"end","")
        BUILD_END("SER03")
    END_RULE
END_CLASS
