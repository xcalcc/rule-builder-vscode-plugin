import io.xc5.RBC_ENGINE;

public class Informer{
    public static void inform(java.lang.String arg1){
        RBC_ENGINE.Model_decl(RBC_ENGINE.Set_tag(RBC_ENGINE.Get_arg(1), "tainted"));
    }
}
