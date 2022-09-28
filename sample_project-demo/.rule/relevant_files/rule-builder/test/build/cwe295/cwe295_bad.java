import org.apache.commons.mail.*;


/**
Example of bad case for the cwe295 in SimpleEmail example
*/

public class cwe295_bad{
    public static void main(String[] args) throws EmailException{
        Email email = new SimpleEmail();
        email.setSmtpPort(45);
        email.setAuthenticator(new DefaultAuthenticator("username", "password"));
        email.send();
    }
}
