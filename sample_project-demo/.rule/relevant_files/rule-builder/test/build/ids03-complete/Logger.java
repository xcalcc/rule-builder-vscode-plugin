package java.util.logging;
import io.xc5.RBC_ENGINE;
public class Logger{
        public void severe(java.lang.String arg1){
            RBC_ENGINE.Rbc_assert(RBC_ENGINE.Is_tag_attr_set(RBC_ENGINE.Get_arg(1),"tainted","sanitize_fmt_str"), "IDS03-J");
        }
        public void info(java.lang.String arg1){
            RBC_ENGINE.Rbc_assert(RBC_ENGINE.Is_tag_attr_set(RBC_ENGINE.Get_arg(1),"tainted","sanitize_fmt_str"), "IDS03-J");
        }
}
