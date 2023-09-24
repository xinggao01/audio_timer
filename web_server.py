from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "0.0.0.0"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Piano time</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        try:
            with open("/dev/shm/audio/counter", "r") as file:
                file_contents = file.read()
                self.wfile.write(
                    bytes(
                        '<p style="font-size: 40px;">'
                        + file_contents.replace("\n", "<br>")
                        + "</p>",
                        "utf-8",
                    )
                )
        except FileNotFoundError:
            self.wfile.write(bytes("<p>file not exist</p>", "utf-8"))

        self.wfile.write(bytes("</body></html>", "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
