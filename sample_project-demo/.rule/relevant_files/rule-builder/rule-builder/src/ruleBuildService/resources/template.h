#ifdef LANG_JAVA
#define PACKAGE(X) package X;
#define IMPORT1 import io.xc5.RBC_ENGINE;
#define IMPORT2
#define IFDEF1
#define IFDEF2
#define IFDEF3
#define ENDIFDEF
#define CLASS(x) public class x{
#define INTERFACE(X) public interface X{
#define END_CLASS }
#define START_RULE(x) public static void x(){
#define END_RULE }
#define ENGINE RBC_ENGINE
#define DECLARE(x) ENGINE.Model_decl(x)
#else // C or __cplusplus
#define PACKAGE(X)
#define IMPORT1 #include <stdio.h>
#define IMPORT2 #include "rbc_base.h"
#define IFDEF1 #ifdef __cplusplus
#define IFDEF2 extern "C" {
#define ENDIFDEF }
#define IFDEF3 #endif
#define CLASS(x) RBC_ENGINE rbc;
#define INTERFACE(X) 
#define END_CLASS
#define START_RULE(x) int x(void) {
#define END_RULE }
#define ENGINE rbc
#define DECLARE(X) ENGINE.Model_decl(X)
#define FAKE_TYPE(x) typedef struct x { } x;
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
#define ADD_TRANSITION(T,U,V,W,X,Y,Z) DECLARE(ENGINE.Fsm_add_transition(T, U, V, W, X, Y, Z));
#define SET_DEFAULT_ACTION(X,Y,Z) DECLARE(ENGINE.Fsm_set_default_action(X, Y, Z));
#define IS_SENSITIVE_DATA(X) ENGINE.Is_tag_attr_set(GET_ARG(X), "sensitive", "sanitize_data")
#define RBC_ASSERT(X,Y) ENGINE.Rbc_assert(X, Y)
#define RBC_SET_TAG(X,Y) DECLARE(ENGINE.Set_tag(X, Y))
#define RBC_IS_TAG_ATTR_SET(X,Y,Z) ENGINE.Is_tag_attr_set(X,Y,Z)
#define PRE_CALL(X) ENGINE.Pre_call(X)
#define SET_IMPLICIT_ASSIGN(X,Y) DECLARE(ENGINE.Set_implicit_assign(X,Y))
#define SET_PARM_MOD(X) DECLARE(ENGINE.Set_parm_mod(X))
#define SET_PARM_DEREF(X) DECLARE(ENGINE.Set_parm_deref(X))
#define SET_FUNC_MAY_SLEEP(X) DECLARE(ENGINE.Set_func_may_sleep(X))
#define SET_ATOMIC_REGION_BEGIN DECLARE(ENGINE.Set_atomic_region_begin())
#define SET_ATOMIC_REGION_END DECLARE(ENGINE.Set_atomic_region_end())
#define SET_FUNC_ATOMIC DECLARE(ENGINE.Set_func_atomic())
#define SET_FUNC_SHUTDOWN DECLARE(ENGINE.Set_func_shutdown())
#define SET_FUNC_COLL_APPEND(X,Y) DECLARE(ENGINE.Set_func_coll_append(X,Y))
#define SET_FUNC_COLL_REMOVE(X,Y) DECLARE(ENGINE.Set_func_coll_remove(X,Y))
#define SET_FUNC_COLL_GET(X,Y) DECLARE(ENGINE.Set_func_coll_get(X,Y))
#define SET_FUNC_MAP_PUT(X,Y,Z) DECLARE(ENGINE.Set_func_map_put(X,Y,Z))
#define SET_FUNC_MAP_GET(X,Y) DECLARE(ENGINE.Set_func_map_get(X,Y))
#define SET_FUNC_STR_GET(X,Y) DECLARE(ENGINE.Set_func_str_get(X,Y))
#define COPY_TAG(X,Y) DECLARE(ENGINE.Copy_tag(X,Y))
#define OR_TAG(X,Y) DECLARE(ENGINE.Or_tag(X,Y))
#define FSM_USE(X) DECLARE(ENGINE.Fsm_use(X))
#define SET_TAG_ATTR(W,X,Y,Z) DECLARE(ENGINE.Set_tag_attr(W,X,Y,Z))
#define EVAL_TAG(X,Y) DECLARE(ENGINE.Eval_tag(X,Y))
#define IS_PARM_TAINTED(X) ENGINE.Is_parm_tainted(X)
#define FUNC_MAY_NOT_RETURN(X) ENGINE.Func_may_not_return(X)
#define AND(X,Y) ENGINE.And(X,Y)
#define OR(X,Y) ENGINE.Or(X,Y)
#define EQ(X,Y) X == Y
#define GET_VAR(X) X
