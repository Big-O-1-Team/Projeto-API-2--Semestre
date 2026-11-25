import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class CEP(BaseHTTPRequestHandler):
    def do_GET(self):
        dados = {"12210000": "SP", "20040020": "RJ"}
        partes = self.path.split("/")
        uf = dados.get(partes[2]) if len(partes) == 4 else None
        corpo = json.dumps({"uf": uf} if uf else {"erro": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(corpo)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8765), CEP).serve_forever()
