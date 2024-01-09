import java.io.*;
import java.net.*;
import java.util.concurrent.*;

/**
 * A concurrent file upload server which provides multithreaded service to clients that upload files.
 * The maximum number of threads is 10, and the server listens on port 8080.
 */
public class ConcurrentFileUploadServer {

    /**
     * The port on which the server will listen for incoming connections.
     */
    private static final int PORT = 8080;

    
    /**
     * The maximum number of threads in the thread pool for handling file upload tasks.
     */
    private static final int MAX_THREADS = 10;

    /**
     * The entry point of the program.
     * Sets up the server to listen on specified PORT
     * and keeps server running infinitely, accepting all incoming client requests
     * Each client request is handed over to ExecutorService (Thread Pool) to be processed concurrently
     *
     * @param args command-line arguments (not used)
     * @throws IOException if an I/O error occurs when server socket is opened
     */
    public static void main(String[] args) throws IOException {

        ExecutorService executor = Executors.newFixedThreadPool(MAX_THREADS);

        ServerSocket serverSocket = new ServerSocket(PORT);

        System.out.println("Server started on port " + PORT);

        while (true) {
            Socket clientSocket = serverSocket.accept();

            executor.submit(new FileUploadHandler(clientSocket));
        }
    }

    
    /**
     * A runnable task for handling file upload from a client.
     */
    private static class FileUploadHandler implements Runnable {
 
        /**
         * Socket connected to the client.
         */
        private final Socket clientSocket;

        /**
         * Constructs a FileUploadHandler for the given socket
         *
         * @param socket The socket connected to the client
         */
        public FileUploadHandler(Socket socket) {
            this.clientSocket = socket;
        }

        /**
         * Perform the file upload by reading from the client socket Input Stream and writing to a local file
         * The method runs in a separate thread
         */
        @Override
        public void run() {
            try (DataInputStream dis = new DataInputStream(clientSocket.getInputStream());
                 FileOutputStream fos = new FileOutputStream("uploaded_file_" + Thread.currentThread().getId() + ".dat")) {

                byte[] buffer = new byte[4096];
                int read;

                while ((read = dis.read(buffer)) > 0) {
                    fos.write(buffer, 0, read);
                }

                System.out.println("File uploaded successfully by thread " + Thread.currentThread().getId());

            } catch (IOException e) {
                System.err.println("Error handling file upload: " + e.getMessage());
            } finally {
                try {
                    clientSocket.close();
                } catch (IOException e) {
                    System.err.println("Error closing socket: " + e.getMessage());
                }
            }
        }
    }
}