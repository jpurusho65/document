import java.io.*;
import java.net.*;
import java.util.concurrent.*;

public class ConcurrentFileUploadServer {

    private static final int PORT = 8080;
    private static final int MAX_THREADS = 10;

    public static void main(String[] args) throws IOException {
        ExecutorService executor = Executors.newFixedThreadPool(MAX_THREADS);
        ServerSocket serverSocket = new ServerSocket(PORT);
        System.out.println("Server started on port " + PORT);

        while (true) {
            Socket clientSocket = serverSocket.accept();
            executor.submit(new FileUploadHandler(clientSocket));
        }
    }

    private static class FileUploadHandler implements Runnable {
        private final Socket clientSocket;

        public FileUploadHandler(Socket socket) {
            this.clientSocket = socket;
        }

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