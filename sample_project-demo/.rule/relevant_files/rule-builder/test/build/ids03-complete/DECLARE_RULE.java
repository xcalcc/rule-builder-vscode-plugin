import io.xc5.RBC_ENGINE;

public class DECLARE_RULE{
    public void IDS03(){
        RBC_ENGINE.Rbc_declare_rule_info("IDS03-J", "CERT",
        "unsanitized user input must no be passed to Logger");        
    }
}
