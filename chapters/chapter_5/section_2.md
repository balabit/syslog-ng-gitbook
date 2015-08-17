# Getting started with implementing Java destinations

Java is one of the most widely used programming languages, and being able to write syslog-ng destinations in Java will allow you to easily interface with any Java codebase.  In this section, you will learn how to create a java destination for syslog-ng which takes messages and logs them to a file. This tutorial assumes a basic understanding of Java.


###The syslog-ng config file

To create a Java destination, you will need to specify the destination of your compiled Java destination in your syslog-ng configuration file. It must be compiled into either a .class file or a .jar file. 
If compiled into a .class file, the class path argument must be the folder containing the .class file.

Here is an example of a Java destination in the config file, where the java destination is compiled to a .class file:

```c
destination java_to_file{
  java(
    class_name("SampleJavaDestination")
    class_path("/home/user/work/projects/javatext/out/production/samplejava/")
    option("name", "value")
    option("filepath", "/home/user/example.txt")
  );
};

```

If you compile your Java destination to a .jar file, you must instead specify the full path to the jar file in the class_path, and include the path inside the jar file in class_path.

```c
destination d_local {
  java(
    class_path("/usr/lib/syslog-ng/3.6/elasticsearch.jar:/usr/share/elasticsearch/lib/elasticsearch-1.4.0.jar:/usr/s\
hare/elasticsearch/lib/lucene-core-4.10.2.jar")
    class_name("org.syslog_ng.destinations.ElasticSearch")
    template("$(format-json --scope rfc5424 --exclude DATE --key ISODATE)")
    option("cluster" "cl1")
    option("index" "syslog")
    option("type" "test")
    option("server" "192.168.1.104")
    option("port" "9300")
  );
};


```


You will see that this Java destination requires a few parameters: of the parameters listed here, only class_path and class_name are absolutely necessary. The others are destination-specific options that the destination designer can require.





###The SampleJavaDestination class

To interface with syslog-ng, you will need to extend the TextLogDestination or StructuredLogDestination abstract class, located in the SyslogNg.jar file, which can be found in the moduledir after make install.
The class you extend will end up looking something like this:

```java

import org.syslog_ng.*;

public class SampleJavaDestination extends TextLogDestination {

  public SampleJavaDestination(long arg0) {
        super(arg0);
    }

    public void deinit(){
    ...
    }

    public void onMessageQueueEmpty(){
    ...
    }   

    public boolean init(){
    ...
    }

    public boolean open(){
    ...
    }

    public boolean isOpened(){
    ... 
    }

    public void close(){
    ...
    }

    public boolean send(String message){
    ...
    }


```

Your class should extend either TextLogDestination or StructuredLogDestination.

When syslog-ng starts, it will create an instance of the class, then attempt to run the init method. This method should do any initialization that needs to be done at the start of the program.

Whenever a new message is generated and fed to your Java class, the send function will be called and passed the message as a String.

To show you a complete (albeit basic) example, here is a Java class which takes messages and logs them to a file, using the destination defined above.

Java file:

```

Javaimport org.syslog_ng.*;

import java.io.*;


public class SampleJavaDestination extends TextLogDestination {

    private String name;
    private String filepath;
    private BufferedWriter writer;

    public SampleJavaDestination(long arg0) {
        super(arg0);
    }

    public void deinit() {
        InternalMessageSender.debug("Deinit");
    }

    public void onMessageQueueEmpty() {
        InternalMessageSender.debug("onMessageQueueEmpty");
    }

    public boolean init() {
        this.name = getOption("name");
        this.filepath = getOption("filepath");

        if (this.name == null) {
            InternalMessageSender.error("Name is a required option for this destination");
            return false;
        }
        if (this.filepath == null) {
            InternalMessageSender.error("Filepath is a required option for this destination");
            return false;
        }


        File textDestination = new File(this.filepath);

        if (!textDestination.exists()) {
            try {
                textDestination.createNewFile();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        try {
            FileOutputStream is = new FileOutputStream(textDestination);
            OutputStreamWriter outputWriter = new OutputStreamWriter(is);
            this.writer = new BufferedWriter(outputWriter);
        } catch (FileNotFoundException e) {
            InternalMessageSender.error(e.getMessage());
            return false;
        }

        InternalMessageSender.debug("Init " + name);
        return true;
    }

    public boolean open() {
        InternalMessageSender.debug("open");
        return true;
    }

    public boolean isOpened() {
        InternalMessageSender.debug("isOpened");
        return true;
    }

    public void close() {
        InternalMessageSender.debug("close");
        try {
            this.writer.close();
        } catch (IOException e) {
            InternalMessageSender.error(e.getMessage());
        }
    }

    public boolean send(String message) {
        try {
            InternalMessageSender.debug("Incoming message: " + message);
            this.writer.write(message);
            this.writer.newLine();
            this.writer.flush();
        }
        catch (Exception e)
        {
            InternalMessageSender.error("error in writing message :" + message);
            return false;
        }
        return true;
    }
}
        
```
### Java-specific Notes
To use a syslog-ng java destination, you have to add the path of the libjvm.so to the LD_LIBRARY_PATH.
