# Getting started with implementing Java destinations

Java is one of the most widely used programming languages, and being able to write syslog-ng destinations in Java will allow you to easily interface with any Java codebase.  In this section, you will learn how to create a java destination for syslog-ng which takes messages and logs them to a file. This tutorial assumes a basic understanding of Java.

###The syslog-ng config file

To create a Java destination, you will need to specify the destination in your syslog-ng configuration file.

Here is an example of a python destination in the config file:

```c
destination java_to_file{
  java(
    class_name("SampleJavaDestination")
    class_path("/home/adam/work/projects/javatext/out/production/samplejava/")
    option("name", "value")
    option("filepath", "/home/adam/example.txt")
  );
};

```

You will see that this Java destination requires a few parameters: of the parameters listed here, only the first two are absolutely necessary. The others are destination-specific options that the destination designer can require.

#### Class_name

The syntax for the class parameter is the name of the compiled Java .class file without the .class extension

#### class_path

This is the location of the folder containing the file specified in class_name




###The SampleJavaDestination class

To interface with syslog-ng, you will need a class that looks something like this:

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
