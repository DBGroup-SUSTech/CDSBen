# YCSB Adaptation Instruction

[toc]

# Background

YCSB contains its core component (ycsb/core) and adaptors for each different storage system, e.g., redis, rocksdb, etc. The core component is unaware of the APIs of each different system. It implements an abstraction layer of I/O APIs on top of the adaptor and generates generic I/O workloads according to the configuration file. The adaptors implement generic I/O APIs with the APIs of the storage system. For example, the adaptor of redis, ```ycsb-master/redis/src/main/java/site/ycsb/db/RedisClient.java```, implements APIs such as read and insert by calling the jedis APIs.

# Adaptor for Your Storsage Tier

To run CDSben on the storage tier of your cloud-native database system, it is essential that you implement a corresponding adaptor.

# YCSB-core Adaptation

There are two main adaptations. First, we have to modify how YCSB generates I/O requests. Second, we have to modify how YCSB executes requests.

## Request Generation in YCSB

As we discussed in our paper, the adapted YCSB loads the generated I/O requests for sequential execution. To implement this feature, we have to bypass the process of reading configuration files and generating I/O requests according to the configuration file in YCSB-core.

In ```YCSB-master/core/src/main/java/site/ycsb/Client.java``` line 302, it loads a ```Workload``` object which is used to control the I/O workload generation. In YCSB, a threadpool containing multiple threads are used to generate and execute I/O requests. All the client threads in the threadpool share the ```Workload``` object. They call ```doTransaction``` API in the ```Workload``` object to determine which request to execute next. To bypass this process, first, in ```YCSB-master/core/src/main/java/site/ycsb/Client.java#main```, we can add source code between line 302 and line 304 to load the I/O requests into YCSB. Then, after line 312, where the client threads are initialized, we assign each client thread a queue of requests this client should execute. The way we assign requests to client threads could be round-robin.
```java
    //...
    // The next line is line 302.
    Workload workload = getWorkload(props);
    // Add code here to load the I/O requests.
    final Tracer tracer = getTracer(props, workload);

    initWorkload(props, warningthread, workload, tracer);

    System.err.println("Starting test.");
    final CountDownLatch completeLatch = new CountDownLatch(threadcount);

    final List<ClientThread> clients = initDb(dbname, props, threadcount, targetperthreadperms,
        workload, tracer, completeLatch);
    // Add code here to assign each client thread a queue of requests to execute.
    // ...
```
Then, in ```YCSB-master/core/src/main/java/site/ycsb/ClientThread.java#run```, from line 122 to line 124, instead of letting the ```Workload``` determine what request to execute next, the client thread executes the next request in its request queue.
```java
          //...
          // The next line is line 122. Load the next request from the queue.
          if (!workload.doTransaction(db, workloadstate)) {
            break;
          }
          //...
```

## Request Execution in YCSB

In YCSB, the I/O requests are issued in a constant speed. However, to execute I/O requests with burstiness, the adapted YCSB must be able to issue I/O requests with different intensity each second. In the loaded requests, each request comes with a timestamp indicates when it should be executed, and we modify YCSB to execute I/O requests according to this timestamp. In ```YCSB-master/core/src/main/java/site/ycsb/ClientThread.java#run``` line 128, YCSB implements its control of intensity. We replace it and insert before line 122 to sleep until it is time to execute the next I/O request.
```java
        //...
        // The next line is line 120.
        while (((opcount == 0) || (opsdone < opcount)) && !workload.isStopRequested()) {
          // Load the next request and sleep until it is time to execute the loaded request.
          if (!workload.doTransaction(db, workloadstate)) {
            break;
          }

          opsdone++;
          // Remove the next line.
          throttleNanos(startTimeNanos);
        }
        //...
```

# References

[1] Brian F. Cooper, Adam Silberstein, Erwin Tam, Raghu Ramakrishnan, and Russell Sears. 2010. Benchmarking cloud serving systems with YCSB. In Proceedings of the 1st ACM symposium on Cloud computing (SoCC '10). Association for Computing Machinery, New York, NY, USA, 143–154. https://doi.org/10.1145/1807128.1807152
