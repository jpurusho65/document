import java.io.*;
import java.net.*;
import java.util.concurrent.*;

/**
 * This class represents a server that facilitates concurrent file uploads.
 */
public class ConcurrentFileUploadServer {

    // Defines the port on which the server listens.
    private static final int PORT = 8080;

    // Defines the maximum number of thread the server will spawn.
    private static final int MAX_THREADS = 10;

    /**
     * The main method to start the server.
     *
     * @param args Command line arguments
     * @throws IOException if it encounters any I/O error when performing server operations.
     */
    public static void main(String[] args) throws IOException {
        // Creates a thread pool.
        ExecutorService executor = Executors.newFixedThreadPool(MAX_THREADS);

        // Creates a server socket on the specified PORT.
        ServerSocket serverSocket = new ServerSocket(PORT);

        System.out.println("Server started on port " + PORT);

        // Continuously accepts incoming client connections and spawns a new thread for each connection.
        while (true) {
            Socket clientSocket = serverSocket.accept();

            // Submits the new file upload task to the executor.
            executor.submit(new FileUploadHandler(clientSocket));
        }
    }

    /**
     * The FileUploadHandler class is a Runnable that handles a single client's file upload.
     */
    private static class FileUploadHandler implements Runnable {
        // Represents the socket of the client this FileUploadHandler handles.
        private final Socket clientSocket;

        /**
         * Constructor initializing a FileUploadHandler for a given client socket.
         *
         * @param socket The client socket
         */
        public FileUploadHandler(Socket socket) {
            this.clientSocket = socket;
        }

        /**
         * This method reads data from the client and writes it to a file.
         */
        @Override
        public void run() {
            try (DataInputStream dis = new DataInputStream(clientSocket.getInputStream());
                 // Creates a FileOutputStream to write the uploaded file.
                 FileOutputStream fos = new FileOutputStream("uploaded_file_" + Thread.currentThread().getId() + ".dat")) {
                
                byte[] buffer = new byte[4096];
                int read;

                // Continuously reads data from the client and writes it to a file until there is no more data.
                while ((read = dis.read(buffer)) > 0) {
                    fos.write(buffer, 0, read);
                }

                System.out.println("File uploaded successfully by thread " + Thread.currentThread().getId());

            } catch (IOException e) {
                System.err.println("Error handling file upload: " + e.getMessage());
            } finally {
                try {
                    // Closes the client socket.
                    clientSocket.close();
                } catch (IOException e) {
                    System.err.println("Error closing socket: " + e.getMessage());
                }
            }
        }
    }
}