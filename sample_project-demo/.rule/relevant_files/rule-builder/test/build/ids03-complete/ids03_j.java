import java.util.logging.Logger;
import java.lang.String;

class Informer{
    private static final Logger LOGGER = Logger.getLogger(ids03_j.class.getName());

    static void inform(String msg){
        LOGGER.info(msg);
        LOGGER.severe(msg);
    }
}

public class ids03_j{
    
    public static void main(String[] args){
        Informer inf = new Informer();
        inf.inform("abc");
    }

}
