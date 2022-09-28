public class StringTest
{
    public void derefParm(String parm1)
    {
        String a = "abc";
        a.compareTo(parm1);  // NPD: parm1 is dereferenced in String::compareTo
    }

    public static void main(String[] args) {
        StringTest t1 = new StringTest();
        String parm1 = null;
        t1.derefParm(parm1);
    }
}
