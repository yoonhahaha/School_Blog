from django.core.management.commands.runserver import Command as RunserverCommand
import os
import ssl

class Command(RunserverCommand):
    help = "Run server with HTTPS support"
    
    def handle(self, *args, **options):
        # Create certificate paths in the proper location
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cert_path = os.path.join(base_dir, 'server.crt')
        key_path = os.path.join(base_dir, 'server.key')
        
        # Generate certificates if they don't exist
        if not (os.path.exists(cert_path) and os.path.exists(key_path)):
            from OpenSSL import crypto
            
            # Create a key pair
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 2048)
            
            # Create a self-signed cert
            cert = crypto.X509()
            cert.get_subject().C = "KR"
            cert.get_subject().ST = "Seoul"
            cert.get_subject().L = "Seoul"
            cert.get_subject().O = "Blog Project"
            cert.get_subject().CN = "192.168.0.101"
            cert.set_serial_number(1000)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10*365*24*60*60)  # 10 years
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.sign(k, 'sha256')
            
            # Save the certificate and key
            with open(cert_path, "wb") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            with open(key_path, "wb") as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            
            print(f"Generated SSL certificate: {cert_path}")
            print(f"Generated SSL key: {key_path}")
        
        # Configure SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        
        # Set HTTPS options
        options['ssl_context'] = ssl_context
        
        # Call the original handle method
        super().handle(*args, **options)