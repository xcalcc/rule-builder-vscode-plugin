package ssd_safe;

import java.io.IOException;

/**
 * Hello world!
 *
 */
public class App 
{
    //Assumpe Sensitive data
    static String ssd1 = "Sensitive data1";

    static String ssd2 = "Sensitive data2";
    public String readssd2(String str) {//@audit-info
        return str;
    }   

    public String readssd3() {//@audit-info
        return "Sensitive data3".toString();
    }    

    //Assumpe Nonsensitive data
    static String nonssd1 = "Nonsensitive data1";

    static String nonssd2 = "Nonsensitive data2";
    public String readnonssd2(String str) {
        return str;
    }  

    public String readnonssd3() { //@audit-info
        return "Nonsensitive data3".toString();
    }

    //Simulation program running
    //check Sensitive data
    public void checkSsdata(){
        
        riskAudit mrule = new riskAudit();

        // mrule.checkOut(ssd1);
        // mrule.checkStorage(ssd1);
        // mrule.checkIPCPipeParent(ssd1);
        // mrule.checkIPCPipeParent(ssd1);  
        // mrule.checkIPCSocketParent(ssd1);
        // mrule.checkIPCSocketChild(ssd1);

        mrule.checkOut(readssd2(ssd2));
        mrule.checkStorage(readssd2(ssd2));
        mrule.checkIPCPipeParent(readssd2(ssd2));
        mrule.checkIPCPipeChild(readssd2(ssd2));
        mrule.checkIPCSocketParent(readssd2(ssd2));
        mrule.checkIPCSocketChild(readssd2(ssd2));       

        // mrule.checkOut(readssd3());
        // mrule.checkStorage(readssd3());
        // mrule.checkIPCPipeParent(readssd3());
        // mrule.checkIPCPipeChild(readssd3());        
        // mrule.checkIPCSocketParent(readssd3());
        // mrule.checkIPCSocketChild(readssd3());    
    }

    //check Nonsensitive data
    public void checkNonssdata(){
        riskAudit mrule = new riskAudit();

        mrule.checkOut(nonssd1);
        mrule.checkStorage(nonssd1);
        mrule.checkIPCPipeParent(nonssd1);
        mrule.checkIPCPipeChild(nonssd1);    
        mrule.checkIPCSocketParent(nonssd1);
        mrule.checkIPCSocketChild(nonssd1);

        mrule.checkOut(readnonssd2(nonssd2));
        mrule.checkStorage(readnonssd2(nonssd2));
        mrule.checkIPCPipeParent(readnonssd2(nonssd2));
        mrule.checkIPCPipeChild(readnonssd2(nonssd2));
        mrule.checkIPCSocketParent(readnonssd2(nonssd2));
        mrule.checkIPCSocketChild(readnonssd2(nonssd2));  

        mrule.checkOut(readnonssd3());
        mrule.checkStorage(readnonssd3());  
        mrule.checkIPCPipeParent(readnonssd3());
        mrule.checkIPCPipeChild(readnonssd3());          
        mrule.checkIPCSocketParent(readnonssd3());
        mrule.checkIPCSocketChild(readnonssd3()); 
    }

    //check Nonsensitive data
    public void Processend(){

        System.out.println( "process end!" );
    }

    //Main program entry
    public static void main( String[] args )
    {
        System.out.println( "This is a sensitive data leakage security protection demo program!" );

        App testApp = new App();

        testApp.checkNonssdata();
        testApp.checkSsdata();    

        testApp.Processend();
    }

    //Missing call
    public static void test1( String[] args )
    {
        System.out.println( "Invoke API test!" );

        App testApp = new App();

        testApp.checkNonssdata();
    //    testApp.checkSsdata();    //Missing call checkSsdata, need report err

        testApp.Processend();
    }

    //Missing call
    public static void test2( String[] args )
    {
        System.out.println( "Invoke API test!" );

        App testApp = new App();

    //    testApp.checkNonssdata();     //Missing call checkNonssdata, need report err
        testApp.checkSsdata();    

        testApp.Processend();
    }

    //Missing call
    public static void test3( String[] args )
    {
        System.out.println( "Invoke API test!" );

        App testApp = new App();

    //    testApp.checkNonssdata();     //Missing call checkNonssdata, need report err
    //    testApp.checkSsdata();        //Missing call checkSsdata, need report err

        testApp.Processend();
    }  

    //Sequence error
    public static void test4( String[] args )
    {
        System.out.println( "Invoke API test!" );

        App testApp = new App();

        testApp.checkSsdata();    // Sequence error

        testApp.checkNonssdata();     

        testApp.Processend();
    }    
}
 
/**
 * Rule describe:
 *
*/
 /** 
 * Rule1: IDS00-J
 * 
 * <ssd_safe.App: void <init>()>
 * <ssd_safe.App: void checkNonssdata()>
 * <ssd_safe.App: void checkSsdata()>
 * 
*/
/**
 * Rule2:IDS01-J
 * <ssd_safe.App: void <init>()>
 * <ssd_safe.App: java.lang.String readssd2(java.lang.String)>
 * <ssd_safe.riskAudit: void checkOut(java.lang.String)>
*/
/**
 * Rule3:IDS07-J
 * <ssd_safe.App: void <init>()>
 * <ssd_safe.riskAudit: void checkOut(java.lang.String)>
 * <ssd_safe.App: void Processend()>
*/