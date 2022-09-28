package ssd_safe;

import java.io.IOException;

public class riskAudit
{
    // check the system.out.print
    public void checkOut(String str){
        
        checkSystemOut mpsysrint = new checkSystemOut();
        byte[] data = str.getBytes();
        int length = str.length();

        //invoke System.out.println
        mpsysrint.println2Char(data, length);
        mpsysrint.println2CharArray(data, length);
        mpsysrint.println2Double(data, length);
        mpsysrint.println2Float(data, length);
        mpsysrint.println2Int(data, length);
        mpsysrint.println2Long(data, length);
        mpsysrint.println2Object(data, length);
        mpsysrint.println2String(data, length);

        //invoke System.out.print
        mpsysrint.print2Object(data, length);
        mpsysrint.print2String(data, length);
        mpsysrint.print2Boolean(data, length);
        mpsysrint.print2Char(data, length);
        mpsysrint.print2CharArray(data, length);
        mpsysrint.print2Double(data, length);
        mpsysrint.print2Float(data, length);
        mpsysrint.print2Int(data, length);
        mpsysrint.print2Long(data, length);

        //invoke System.out.printf
        mpsysrint.printf2Locale(data, length);
        mpsysrint.printf2String(data, length);

        //invoke System.out.write
        mpsysrint.write2Byte(data, length);
        mpsysrint.write2Byte2(data, length);
        mpsysrint.write2Int(data, length);
    }

    // check the system.err.print
    public void checkErr(String str){
        
        checkSystemErr msyserr = new checkSystemErr();
        byte[] data = str.getBytes();
        int length = str.length();

        //invoke System.err.println
        msyserr.println2Char(data, length);
        msyserr.println2CharArray(data, length);
        msyserr.println2Double(data, length);
        msyserr.println2Float(data, length);
        msyserr.println2Int(data, length);
        msyserr.println2Long(data, length);
        msyserr.println2Object(data, length);
        msyserr.println2String(data, length);

        //invoke System.err.print
        msyserr.print2Object(data, length);
        msyserr.print2String(data, length);
        msyserr.print2Boolean(data, length);
        msyserr.print2Char(data, length);
        msyserr.print2CharArray(data, length);
        msyserr.print2Double(data, length);
        msyserr.print2Float(data, length);
        msyserr.print2Int(data, length);
        msyserr.print2Long(data, length);

        //invoke System.err.printf
        msyserr.printf2Locale(data, length);
        msyserr.printf2String(data, length);

        //invoke System.err.write
        msyserr.write2Byte(data, length);
        msyserr.write2Byte2(data, length);
        msyserr.write2Int(data, length);        
    }

    // check the file write
    public void checkStorage(String data){
        
        checkStorage mstorage = new checkStorage();

        try{
            mstorage.writeFileWithBufferedWriter(data);
            mstorage.appendFileWithBufferedWriter(data);
            mstorage.writingFileWithPrintWriter(data);
            mstorage.writingFileWithFileOutputStream(data);   
            mstorage.writingFileWithDataOutputStream(data);    
            mstorage.writeToPositionWithRAF(data);
            mstorage.writeWithFileChannel(data);
            mstorage.writeWithFiles(data);

        }catch (IOException e){
            System.err.println("ERROR");
        }
                             
    }

    // check the IPC Pipe
    public void checkIPCPipeParent(String str){

        checkIPCPipeParent mipcpipeparent = new checkIPCPipeParent();

        mipcpipeparent.main(str);
    }

    public void checkIPCPipeChild(String str){

        checkIPCPipeChild mipcpipetchild = new checkIPCPipeChild();

        mipcpipetchild.main(str);
    }

    // check the IPC Socket
    public void checkIPCSocketParent(String str){

        checkIPCSocketParent mipcsocketparent = new checkIPCSocketParent();

        mipcsocketparent.main(str);
    }

    public void checkIPCSocketChild(String str){

        checkIPCSocketChild mipcsocketchild = new checkIPCSocketChild();

        mipcsocketchild.main(str);
    }
}
